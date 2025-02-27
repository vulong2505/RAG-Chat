from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.types import ChatRequest, ChatResponse
from .workflow.graph import RAGWorkflowManager

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Initialize workflow manager 
    workflow_manager = RAGWorkflowManager()
    
    # Process the message
    result = await workflow_manager.process_message(request.message)
    
    return ChatResponse(
        answer=result["generation"]["answer"],
        sources=[{"content": doc.page_content, "source": doc.metadata.get("source")} 
                for doc in result.get("documents", [])]
    )