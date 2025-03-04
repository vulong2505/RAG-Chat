from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.database import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.models.types import ConversationCreate, ConversationResponse

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    repo = ConversationRepository(db)
    conversations = repo.get_all_conversations()

    # Manual conversion to match expected response model
    result = []
    for conv in conversations:
        messages = []
        for msg in conv.messages:
            sources = []
            for src in msg.sources:
                sources.append({
                    "content": src.content,
                    "source": src.source
                })
            
            messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
                "sources": sources
            })
        
        result.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "messages": messages
        })
    
    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    repo = ConversationRepository(db)
    conversation = repo.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Manual conversion
    messages = []
    for msg in conversation.messages:
        sources = []
        for src in msg.sources:
            sources.append({
                "content": src.content,
                "source": src.source
            })
        
        messages.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at,
            "sources": sources
        })
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": messages
    }

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    repo = ConversationRepository(db)
    return repo.create_conversation(conversation.title)

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    repo = ConversationRepository(db)
    success = repo.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}