import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
from pathlib import Path
from langchain.schema import Document
from app.chains.base import ChainManager
from app.workflow.graph import RAGWorkflowManager
from langchain_community.chat_models import ChatOllama

async def test_system():

    # Initialize workflow (which also initializes the ChainManager and the chat and rag models)
    workflow_manager = RAGWorkflowManager()
    
    # Test document ingestion
    test_docs = [
        Document(
            page_content="LLM agents are autonomous systems that use large language models as their core controller.",
            metadata={"source": "test_doc_1"}
        ),
        Document(
            page_content="RAG (Retrieval Augmented Generation) is a technique that enhances LLM responses with relevant context.",
            metadata={"source": "test_doc_2"}
        )
    ]
    
    # Add documents via ChainManager
    await workflow_manager.chain_manager.add_documents(test_docs)
    print("Documents added successfully")
    
    # Initialize workflow manager
    
    # Test questions
    test_questions = [
        "Hi, how are you?",  # Should route to direct
        "What are LLM agents?",  # Should route to vectorstore
        "What's the weather in Paris?",  # Should route to web search
    ]

    for question in test_questions:
        print(f"\nTesting question: {question}")
        result = await workflow_manager.process_message(question)
        print(f"Final answer: {result.get('generation', 'No generation found')}")
        print("Documents used:", len(result.get('documents', [])))

    more_test_docs = [
        Document(
            page_content="Whales are big and blue and lives in the ocean.",
            metadata={"source": "test_doc_3"}
        ),
        Document(
            page_content="A Moon landing or lunar landing is the arrival of a spacecraft on the surface of the Moon, including both crewed and robotic missions. The first human-made object to touch the Moon was Luna 2 in 1959. In 1969 Apollo 11 was the first crewed mission to land on the Moon. There were six crewed landings between 1969 and 1972, and numerous uncrewed landings.",
            metadata={"source": "test_doc_4"}
        )
    ]

    await workflow_manager.chain_manager.add_documents(more_test_docs)
    print("Documents added successfully")

    test_questions = [
        "Hi, how are you?",  # Should route to direct
        "What is a whale?",  # Should route to vectorstore
        "Tell me about the moon landing." # Should route to vectorstore, not web search
    ]


    for question in test_questions:
        print(f"\nTesting question: {question}")
        result = await workflow_manager.process_message(question)
        print(f"Final answer: {result.get('generation', 'No generation found')}")
        print("Documents used:", len(result.get('documents', [])))


if __name__ == "__main__":
    asyncio.run(test_system())