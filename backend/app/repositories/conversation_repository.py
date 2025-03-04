from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.database import Conversation, Message, Source

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_conversations(self) -> List[Conversation]:
        return self.db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def create_conversation(self, title: str) -> Conversation:
        conversation = Conversation(
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def delete_conversation(self, conversation_id: int) -> bool:
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        self.db.delete(conversation)
        self.db.commit()
        return True
    
    def update_conversation_title(self, conversation_id: int, title: str) -> Optional[Conversation]:
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def add_message(self, conversation_id: int, role: str, content: str, sources=None) -> Message:
        # Create the message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        self.db.flush()  # To get message.id
        
        # Update conversation timestamp
        conversation = self.get_conversation(conversation_id)
        conversation.updated_at = datetime.utcnow()
        
        # Add sources if provided
        if sources:
            for source_data in sources:
                source = Source(
                    message_id=message.id,
                    content=source_data.get("content", ""),
                    source=source_data.get("source", "")
                )
                self.db.add(source)
        
        self.db.commit()
        self.db.refresh(message)
        return message