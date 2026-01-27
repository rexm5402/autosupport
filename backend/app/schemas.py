from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"


# Ticket Schemas
class TicketCreate(BaseModel):
    """Schema for creating a ticket"""
    customer_name: str
    customer_email: EmailStr
    customer_id: Optional[str] = None
    subject: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)


class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None


class TicketAssign(BaseModel):
    """Schema for assigning a ticket to an agent"""
    agent_id: int


class TicketResponse(BaseModel):
    """Schema for ticket response"""
    id: int
    ticket_number: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    category: Optional[TicketCategory]
    category_confidence: Optional[float]
    priority: TicketPriority
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    urgency_score: Optional[float]
    status: TicketStatus
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Agent Schemas
class AgentCreate(BaseModel):
    """Schema for creating an agent"""
    name: str
    email: EmailStr
    expertise: str
    max_tickets: int = 10


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = None
    expertise: Optional[str] = None
    max_tickets: Optional[int] = None
    is_available: Optional[bool] = None


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: int
    name: str
    email: str
    expertise: str
    max_tickets: int
    is_active: bool
    is_available: bool
    total_tickets_handled: int
    average_resolution_time: float
    customer_satisfaction_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Response Message Schemas
class MessageCreate(BaseModel):
    """Schema for creating a response message"""
    ticket_id: int
    message: str
    is_agent_response: bool = True
    agent_name: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    ticket_id: int
    message: str
    is_agent_response: bool
    agent_name: Optional[str]
    is_ai_suggested: bool
    suggestion_confidence: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Classification Schemas
class ClassificationRequest(BaseModel):
    """Schema for classification request"""
    text: str


class ClassificationResponse(BaseModel):
    """Schema for classification response"""
    category: str
    confidence: float
    all_predictions: dict


class SentimentResponse(BaseModel):
    """Schema for sentiment response"""
    sentiment: str
    score: float
    urgency_score: float


# Analytics Schemas
class TicketStats(BaseModel):
    """Schema for ticket statistics"""
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    average_resolution_time: float
    tickets_by_category: dict
    tickets_by_priority: dict
    sentiment_distribution: dict


class AgentStats(BaseModel):
    """Schema for agent statistics"""
    total_agents: int
    available_agents: int
    busy_agents: int
    average_tickets_per_agent: float
    top_performers: List[dict]


class AnalyticsResponse(BaseModel):
    """Schema for analytics response"""
    ticket_stats: TicketStats
    agent_stats: AgentStats
    trends: dict


# RAG Schemas
class SuggestedResponse(BaseModel):
    """Schema for suggested response"""
    suggested_text: str
    confidence: float
    source_tickets: List[str]
    reasoning: str


# Knowledge Base Schemas
class KnowledgeBaseCreate(BaseModel):
    """Schema for creating knowledge base article"""
    title: str
    content: str
    category: TicketCategory
    tags: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response"""
    id: int
    title: str
    content: str
    category: TicketCategory
    tags: Optional[str]
    view_count: int
    helpful_count: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
