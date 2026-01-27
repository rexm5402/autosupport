from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class TicketStatus(str, enum.Enum):
    """Ticket status enum"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    """Ticket priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    """Ticket category enum"""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, index=True, nullable=False)
    
    # Customer information
    customer_name = Column(String(100))
    customer_email = Column(String(100), index=True)
    customer_id = Column(String(50))
    
    # Ticket content
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    category = Column(Enum(TicketCategory), nullable=True)
    category_confidence = Column(Float, nullable=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    
    # Sentiment analysis
    sentiment = Column(String(20))  # positive, negative, neutral
    sentiment_score = Column(Float)
    urgency_score = Column(Float)
    
    # Status and assignment
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    assigned_to = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="tickets")
    responses = relationship("TicketResponse", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket {self.ticket_number}: {self.subject}>"


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Skills and expertise
    expertise = Column(String(500))  # Comma-separated categories
    max_tickets = Column(Integer, default=10)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    
    # Performance metrics
    total_tickets_handled = Column(Integer, default=0)
    average_resolution_time = Column(Float, default=0.0)  # in hours
    customer_satisfaction_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="agent")
    
    @property
    def current_ticket_count(self):
        """Get current number of assigned tickets"""
        return len([t for t in self.tickets if t.status != TicketStatus.CLOSED])
    
    def __repr__(self):
        return f"<Agent {self.name} ({self.email})>"


class TicketResponse(Base):
    """Ticket response/message model"""
    __tablename__ = "ticket_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    
    # Response content
    message = Column(Text, nullable=False)
    is_agent_response = Column(Boolean, default=True)
    agent_name = Column(String(100))
    
    # AI suggestions
    is_ai_suggested = Column(Boolean, default=False)
    suggestion_confidence = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="responses")
    
    def __repr__(self):
        return f"<TicketResponse for Ticket {self.ticket_id}>"


class KnowledgeBase(Base):
    """Knowledge base articles for RAG system"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(TicketCategory))
    
    # Metadata
    tags = Column(String(500))  # Comma-separated tags
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    # Status
    is_published = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeBase {self.title}>"
