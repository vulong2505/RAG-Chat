from typing import List, Dict, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class GraphState(TypedDict):
    """
    Represents the state in the graph.

    Attributes:
        question: Original prompted question
        generation: LLM generation
        documents: List of documents
        history: Conversation history (list of role/content dicts)
        metadata: Additional state info 
    """

    question: str
    generation: str
    documents: List[str]
    history: List[Dict[str, str]]
    metadata: Optional[Dict[str, any]] = {}

###### API Models #####

class ChatRequest(BaseModel):
    message: str
    conversation_id: int = None

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[Dict[str, str]]] = None

###### Structured output #####

class ExtractedTopics(BaseModel):
    topics: List[str] = Field(
        description="List of short keywords that encompass the main topics of the documents"
    )

class ExtractedTitle(BaseModel):
    title: str = Field(
        description="A very concise summary title for a chat session based on this initial question."
    )

###### Conversation #####

class ConversationCreate(BaseModel):
    title: str

class SourceResponse(BaseModel):
    content: str
    source: str
    
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    sources: List[SourceResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)