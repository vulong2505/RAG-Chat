from typing import Dict, Any
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
from langgraph.graph import END, StateGraph, START
from fastapi.responses import StreamingResponse

from ..config.settings import settings
from ..chains.base import ChainManager
from ..models.types import GraphState

import json

class RAGWorkflowManager:
    def __init__(self):
        # Initialize models
        self.chat_llm = ChatOllama(
            model=settings.CHAT_MODEL,
            temperature=0.7
        )
        self.rag_llm_json = ChatOllama(
            model=settings.RAG_MODEL,
            temperature=0,
            format="json"
        )
        self.rag_llm_structured = ChatOllama(
            model=settings.RAG_MODEL,
            temperature=0
        )
        
        # Initialize chain manager
        self.chain_manager = ChainManager(
            chat_llm=self.chat_llm,
            rag_llm_json=self.rag_llm_json,
            rag_llm_structured=self.rag_llm_structured
        )
        
        # Set up workflow graph
        self.workflow = self._build_graph()
        self.app = self.workflow.compile()

    def _build_graph(self) -> StateGraph:
        """Build the RAG workflow graph"""
        
        workflow = StateGraph(GraphState)
        
        # Add nodes using chain_manager's nodes
        workflow.add_node("web_search", self.chain_manager.web_search)
        workflow.add_node("retrieve", self.chain_manager.retrieve)
        workflow.add_node("grade_documents", self.chain_manager.grade_documents)
        workflow.add_node("generate", self.chain_manager.generate)
        workflow.add_node("transform_query", self.chain_manager.transform_query)

        # Build graph edges
        workflow.add_conditional_edges(
            START,
            self.chain_manager.route_question,
            {
                "web_search": "web_search",
                "vectorstore": "retrieve",
                "generate": "generate"
            },
        )
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self.chain_manager.decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            self.chain_manager.grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "transform_query",
            },
        )
        
        return workflow

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a message through the RAG workflow"""
        inputs = {"question": message}
        final_output = None
        
        # Stream through the workflow
        async for output in self.app.astream(inputs):
            # Store the final output
            final_output = output
            
        return final_output["generate"] # .astream() returns {"node_name": state}, and we want to return the state
    

    async def process_message_stream(self, message: str):
        """Stream the RAG process with status updates to the frontend"""
        inputs = {"question": message}
        
        # Define user-friendly descriptions for each node
        status_messages = {
            "retrieve": "Retrieving relevant documents...",
            "grade_documents": "Evaluating document relevance...",
            "generate": "Generating your answer...",
            "transform_query": "Refining search query...",
            "web_search": "Searching the web for information..."
        }
        
        async def event_generator():
            current_node = None
            final_state = None
            
            # Use astream to get node information
            async for output in self.app.astream(inputs):
                # Get the node name (first and only key)
                node_name = list(output.keys())[0]
                state = output[node_name]
                final_state = state  # Keep track of the latest state
                
                # Send status update if node has changed
                if node_name != current_node:
                    current_node = node_name
                    status = status_messages.get(node_name, f"Processing: {node_name}")
                    yield f"data: {json.dumps({'status': status})}\n\n"
            
            # After the stream is complete, send the final answer
            if final_state and "generation" in final_state:
                answer = final_state["generation"]["answer"]
                yield f"data: {json.dumps({'answer': answer})}\n\n"
            
        # Return a streaming response
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )