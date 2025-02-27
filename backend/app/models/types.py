from typing import List, Dict, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class GraphState(TypedDict):
    """
    Represents the state in the graph.

    Attributes:
        question: Original prompted question
        generation: LLM generation
        documents: List of documents
        metadata: Additional state info 
    """

    question: str
    generation: str
    documents: List[str]
    metadata: Optional[Dict[str, any]] = {}

###### API Models #####

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[Dict[str, str]]] = None

###### Structured output #####

class ExtractedTopics(BaseModel):
    topics: List[str] = Field(
        description="List of short keywords that encompass the main topics of the documents"
    )
