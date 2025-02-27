from typing import Dict, Any, List
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.documents import Document
from langchain import hub
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.tools.tavily_search import TavilySearchResults
from pathlib import Path
import os

from ..config.settings import settings
from ..models.types import ExtractedTopics

class ChainManager:
    
    def __init__(self, chat_llm: ChatOllama, rag_llm_json: ChatOllama, rag_llm_structured: ChatOllama):
        # Store LLMs
        self.chat_llm = chat_llm
        self.rag_llm_json = rag_llm_json
        self.rag_llm_structured = rag_llm_structured

        # Initialize ChromaDB with persistence
        self._initialize_vectorstore()

        # Set up multi-query retriever
        self._setup_retriever()

        # Vectorstore topics
        self.vectorstore_topics = set()

        # Initialize web search tool with Tavily
        self.web_search_tool = TavilySearchResults(k=3)

        # Setup all chains
        self._setup_chains()

    ##### VECTOR STORE #####

    def _initialize_vectorstore(self):
        """Initialize and load ChromaDB"""

        base_dir = Path(__file__).parent.parent # app/
        PERSIST_DIRECTORY = os.path.join(base_dir, "data", "vectorstore")   # app/data/vectorstore

        # Create directory if it doesn't exist
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

        # Initialize/Load ChromaDB
        self.vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local"),
            collection_name="user_documents"
        )

    def _setup_retriever(self):
        """Set up the multi-query retriever with initialized vectorstore"""
        self.multiquery_retriever = MultiQueryRetriever.from_llm(
            retriever=self.vectorstore.as_retriever(),
            llm=self.rag_llm_json
        )

    async def add_documents(self, documents: List[Document]):
        """
        Add documents into the vector store with chunking
        
        Args:
            documents: List of Langchain Document objects
        """
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=250, 
            chunk_overlap=0
        )

        # Split documents
        doc_splits = text_splitter.split_documents(documents)
        
        # Add to vectorstore
        self.vectorstore.add_documents(doc_splits)

        # Update vector store topics
        self.vectorstore_topics.update(self.extract_topics(doc_splits))
        print("Current vectorstore topics: ", self.vectorstore_topics)
        
        # Persist changes
        self.vectorstore.persist()


    def get_vectorstore_info(self) -> Dict[str, Any]:
        """Get information about the current vector store"""

        if not self.vectorstore:
            return {"status": "not_initialized"}
        
        try:
            collection = self.vectorstore.get()
            return {
                "status": "initialized",
                "count": len(collection["ids"]),
                "collection_name": self.vectorstore._collection.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    ##### CHAIN AGENTS #####

    def _setup_chains(self):
        """Initialize chains"""

        # Router chain
        self.question_router = self._create_question_router_chain()

        # Grading chain
        self.retrieval_grader = self._create_retrieval_grader()
        self.hallucination_grader = self._create_hallucination_grader()
        self.answer_grader = self._create_answer_grader()

        # Generate chain
        self.generate_chain = self._create_generate_chain()

        # Question re-writer chain
        self.question_rewriter = self._create_question_rewriter()

        # Extract topics chain
        self.extract_topics_chain = self._create_extract_topics_chain()

    def _create_question_router_chain(self):
        """Agent to route the workflow to the vectorstore, web search, or directly based on the user's question"""

        question_router_prompt = PromptTemplate(
            template="""You are an expert at routing a user question to the appropriate source.

            For questions about factual information that requires context or verification:
            - Use 'vectorstore' for questions regarding {vectorstore_topics}
            - Use 'web_search' for current event context, real-time information, fact verification, or broad information synthesis

            For questions that are more conversational, analytical, or can be answered with general knowledge:
            - Use 'direct' for:
            * Simple calculations or logic problems
            * Questions about hypothetical scenarios
            * Questions asking for opinions or analysis
            * General coding questions
            * Basic explanations
            * Common knowledge

            Return a JSON with a single key 'datasource' with value either 'vectorstore', 'web_search', or 'direct'.
            No preamble or explanation.

            Question to route: {question}""",
            input_variables=["question", "vectorstore_topics"],
        )

        return question_router_prompt | self.rag_llm_json | JsonOutputParser()

    def _create_retrieval_grader(self):
        """Agent to grade the relevance of the retrieved documents to the user's question"""

        retrieval_grader_prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question. \n
            Here is the retrieved document: \n\n {document} \n\n
            Here is the user question: {question} \n
            If the document contains keywords related to the user question, grade it as relevant. \n
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
            Provide the binary score as a JSON with a single key 'score' and no premable or explanation.""",
            input_variables=["question", "document"],
        )

        return retrieval_grader_prompt | self.rag_llm_json | JsonOutputParser()

    def _create_hallucination_grader(self):
        """Agent to check for hallucinations in answer"""

        hallucination_grader_prompt = PromptTemplate(
            template="""You are a grader assessing whether an answer is grounded in / supported by a set of facts. \n
            Here are the facts:
            \n ------- \n
            {documents}
            \n ------- \n
            Here is the answer: {generation}
            Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. \n
            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
            input_variables=["generation", "documents"],
        )

        return hallucination_grader_prompt | self.rag_llm_json | JsonOutputParser()

    def _create_answer_grader(self):
        """Agent to grade the answer's usefulness"""

        answer_grader_prompt = PromptTemplate(
            template="""You are a grader assessing whether an answer is useful to resolve a question. \n
            Here is the answer:
            \n ------- \n
            {generation}
            \n ------- \n
            Here is the question: {question}
            Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question. \n
            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
            input_variables=["generation", "question"],
        )

        return answer_grader_prompt | self.rag_llm_json | JsonOutputParser()

    def _create_question_rewriter(self):
        """Agent to rewrite the question"""

        rewrite_prompt = PromptTemplate(
            template="""You a question re-writer that converts an input question to a better version that is optimized \n
            for vectorstore retrieval. Look at the initial and formulate an improved question. \n
            Here is the initial question: \n\n {question}. Improved question with no preamble: \n """,
            input_variables=["generation", "question"],
        )

        return rewrite_prompt | self.rag_llm_json | JsonOutputParser()

    def _create_generate_chain(self):
        """The generate chain using the RAG context (if provided) and user's question"""

        generate_prompt = PromptTemplate(
            template="""You are a helpful and conversational assistant. Ground your answer in the provided context. If the context doesn't provide enough information, answer based on your existing, expert knowledge and don't mention the source of your information or what the context does or doesn't include.

        Context (if provided):
        -- <START CONTEXT>
        {context}
        -- <END CONTEXT>

        Question: {question}

        Provide a clear, conversational explanation using the information from the context.""",
            input_variables=["context", "question"]
        )

        return generate_prompt | self.chat_llm | self.structure_response

    def _create_extract_topics_chain(self):
        """Agent to extract vector store topics from documents"""

        parser = JsonOutputParser(pydantic_object=ExtractedTopics)

        extract_topic_prompt = PromptTemplate(
            template="""Extract ONLY the main topics from these documents as a list of short keywords.
            
            Documents:
            {documents}
            
            {format_instructions}

            Important instructions:
            - Return ONLY a list of short topic keywords
            - Do NOT include any summary or explanation
            - Each topic should be a single word or short phrase
            - Focus on the central themes and subjects
            - Return exactly in the JSON format specified above
            """,
            input_variables=["documents"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return extract_topic_prompt | self.rag_llm_structured | parser

    ##### NODES #####

    def retrieve(self, state: Dict) -> Dict:
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        
        print("---RETRIEVE---")
        question = state["question"]

        # Retrieval
        documents = self.multiquery_retriever.invoke(question)

        return {"documents": documents, "question": question}


    def generate(self, state: Dict) -> Dict:
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """

        print("---GENERATE---")
        question = state["question"]
        documents = state.get("documents", [])
        formatted_documents = self.format_docs(docs=documents)

        # RAG generation
        generation = self.generate_chain.invoke({"context": formatted_documents, "question": question})

        return {"documents": documents, "question": question, "generation": generation}

    def grade_documents(self, state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with only filtered relevant documents
        """

        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        for d in documents:
            score = self.retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score["score"]
            if grade == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                continue
        return {"documents": filtered_docs, "question": question}

    def transform_query(self, state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """

        print("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]

        # Re-write question
        better_question = self.question_rewriter.invoke({"question": question})
        better_question_str = next(iter(better_question.values())) # Unsure if the key will always be "question", so this is used to extract the value in the case it's something else.
        return {"documents": documents, "question": better_question_str}

    def web_search(self, state):
        """
        Web search based on the re-phrased question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with appended web results
        """

        print("---WEB SEARCH---")
        question = state["question"]

        # Web search
        docs = self.web_search_tool.invoke({"query": question})
        web_results = "\n".join([d["content"] for d in docs])
        web_results = [Document(page_content=web_results)]

        return {"documents": web_results, "question": question}

    ##### EDGES #####

    def route_question(self, state):
        """
        Route question to web search or RAG.

        Args:
            state (dict): The current graph state

        Returns:
            str: Next node to call
        """

        print("---ROUTE QUESTION---")
        question = state["question"]
        print(f"Question: {question}")
        print(f"Vectorstore topics used to route: ", {', '.join(list(self.vectorstore_topics))})
        source = self.question_router.invoke({"question": question, "vectorstore_topics": ', '.join(self.vectorstore_topics)})
        print(source)
        print(source["datasource"])
        if source["datasource"] == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "web_search"
        elif source["datasource"] == "vectorstore":
            print("---ROUTE QUESTION TO RAG---")
            return "vectorstore"
        elif source["datasource"] == "direct":
            print("---ROUTE QUESTION TO DIRECT---")
            return "generate"
        else:
            print("---ROUTE QUESTION TO DEFAULT---")
            return "generate"

    def decide_to_generate(self, state):
        """
        Determines whether to generate an answer, or re-generate a question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Binary decision for next node to call
        """

        print("---ASSESS GRADED DOCUMENTS---")
        state["question"]
        filtered_documents = state["documents"]

        if not filtered_documents:
            # All documents have been filtered check_relevance
            # We will re-generate a new query
            print(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
            )
            return "transform_query"
        else:
            # We have relevant documents, so generate answer
            print("---DECISION: GENERATE---")
            return "generate"

    def grade_generation_v_documents_and_question(self, state):
        """
        Determines whether the generation is grounded in the document and answers question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Decision for next node to call
        """

        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        print(f"Length of docs: {len(documents)}")
        print(f"Type of docs: {type(documents)}")
        print(f"Docs: {documents}")

        if len(documents) == 0: # Decided not to retrieve documents
            return "useful"

        score = self.hallucination_grader.invoke(
            {"documents": documents, "generation": generation}
        )
        grade = score["score"]

        # Check hallucination
        if grade == "yes":
            print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            # Check question-answering
            print("---GRADE GENERATION vs QUESTION---")
            score = self.answer_grader.invoke({"question": question, "generation": generation})
            grade = score["score"]
            if grade == "yes":
                print("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"
        else:
            print("Generation:", generation)
            print("Documents:", documents)
            print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"



    ##### UTILITY #####

    @staticmethod
    def format_docs(docs: List) -> str:
        """Format documents into a clean string of their contents"""

        return "\n\n".join(doc.page_content for doc in docs)

    def structure_response(self, response) -> Dict:
        """Explicitly format the model's answer as {"answer": "response"}"""

        return {"answer": response.content}

    def extract_topics(self, documents: List[Document]) -> set:
        """Extract main topics from documents using the RAG LLM"""

        response = self.extract_topics_chain.invoke({"documents": self.format_docs(docs=documents)})
        print("In extract_topics:\n", response)
        topics = set(response["topics"])
        print("Extracted topics: ", topics)

        return topics
