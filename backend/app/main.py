from fastapi import FastAPI, Body, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from typing import List, Optional
from sqlalchemy.orm import Session

import os
import tempfile

from app.models.types import ChatRequest, ChatResponse
from app.workflow.graph import RAGWorkflowManager
from app.database.session import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.api.conversations import router as conversation_router

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add router
app.include_router(conversation_router, prefix="/api")

# Initialize workflow manager upon app startup
workflow_manager = RAGWorkflowManager()


@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # Extract conversation_id from the request body
    conversation_id = request.conversation_id
    
    # Initialize repositories
    repo = ConversationRepository(db)
    
    # Create conversation if not provided
    if not conversation_id:
        # Generate a title from the message
        title = workflow_manager.chain_manager.extract_session_title(request.message)
        conversation = repo.create_conversation(title)
        conversation_id = conversation.id
        history = []
    else:
        # Verify conversation exists
        conversation = repo.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get conversation history
        history = []
        for msg in conversation.messages:
            history.append({
                "role": msg.role,
                "content": msg.content
            })
    
    # Save user message
    repo.add_message(conversation_id, "user", request.message)
    history.append({"role": "user", "content": request.message})
    
    # Process the message
    result = await workflow_manager.process_message(request.message, history)
    
    # Handle different formats of generation response
    answer = ""
    if isinstance(result.get("generation"), dict) and "answer" in result["generation"]:
        answer = result["generation"]["answer"]
    elif isinstance(result.get("generation"), str):
        answer = result["generation"]
    else:
        answer = str(result.get("generation", "No response generated"))
    
    # Format sources if available
    sources = []
    if "documents" in result and result["documents"]:
        for doc in result["documents"]:
            sources.append({
                "content": doc.page_content if hasattr(doc, "page_content") else str(doc),
                "source": doc.metadata.get("source", "unknown") if hasattr(doc, "metadata") else "unknown"
            })

    # Save assistant message with sources
    repo.add_message(conversation_id, "assistant", answer, sources)

    return {
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation_id
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to be processed and added to the RAG system.
    Supports .txt, .pdf, and .docx files.
    """

    # Check file extension
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    # Get the file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Create temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        # Write uploaded file content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Process the file based on its type
        documents: List[Document] = []
        
        if file_extension == ".txt":
            loader = TextLoader(temp_path)
            documents = loader.load()
        elif file_extension == ".pdf":
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
        elif file_extension in [".docx", ".doc"]:
            loader = Docx2txtLoader(temp_path)
            documents = loader.load()
        else:
            os.unlink(temp_path)  # Clean up temp file
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Please upload .txt, .pdf, or .docx files."
            )
        
        # Set metadata for the document
        for doc in documents:
            doc.metadata["source"] = filename
            
        # Add documents to the vector store
        await workflow_manager.chain_manager.add_documents(documents)
        
        # Clean up the temp file
        os.unlink(temp_path)
        
        return {
            "status": "success",
            "message": f"Document '{filename}' processed and added to knowledge base",
            "document_count": len(documents)
        }
        
    except Exception as e:
        # Clean up the temp file in case of error
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        print(e)
        
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
