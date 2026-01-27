from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random
import string

from app.core.database import get_db
from app.schemas import (
    TicketCreate, TicketUpdate, TicketResponse, 
    TicketAssign, MessageCreate, MessageResponse
)
from models.ticket import Ticket, TicketResponse as TicketResponseModel, TicketStatus

router = APIRouter()


def generate_ticket_number():
    """Generate unique ticket number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TKT-{timestamp}-{random_str}"


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket"""
    
    # Create ticket
    db_ticket = Ticket(
        ticket_number=generate_ticket_number(),
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        customer_id=ticket.customer_id,
        subject=ticket.subject,
        description=ticket.description
    )
    
    # Simple keyword-based classification (no ML service needed for now)
    text_lower = ticket.description.lower()
    
    # Determine category
    if any(word in text_lower for word in ['password', 'login', 'access', 'account']):
        db_ticket.category = "account"
        db_ticket.urgency_score = 0.6
    elif any(word in text_lower for word in ['payment', 'charge', 'bill', 'refund']):
        db_ticket.category = "billing"
        db_ticket.urgency_score = 0.7
    elif any(word in text_lower for word in ['error', 'bug', 'crash', 'not working', 'broken']):
        db_ticket.category = "technical"
        db_ticket.urgency_score = 0.8
    elif any(word in text_lower for word in ['feature', 'suggest', 'add', 'implement']):
        db_ticket.category = "feature_request"
        db_ticket.urgency_score = 0.3
    elif any(word in text_lower for word in ['disappointed', 'terrible', 'angry', 'complaint']):
        db_ticket.category = "complaint"
        db_ticket.urgency_score = 0.7
    else:
        db_ticket.category = "general"
        db_ticket.urgency_score = 0.5
    
    db_ticket.category_confidence = 0.75
    
    # Simple sentiment analysis
    negative_words = ['angry', 'terrible', 'worst', 'disappointed', 'frustrated', 'broken']
    positive_words = ['great', 'good', 'thanks', 'appreciate', 'helpful']
    
    neg_count = sum(1 for word in negative_words if word in text_lower)
    pos_count = sum(1 for word in positive_words if word in text_lower)
    
    if neg_count > pos_count:
        db_ticket.sentiment = "negative"
        db_ticket.sentiment_score = 0.3
    elif pos_count > neg_count:
        db_ticket.sentiment = "positive"
        db_ticket.sentiment_score = 0.8
    else:
        db_ticket.sentiment = "neutral"
        db_ticket.sentiment_score = 0.5
    
    # Set priority based on urgency
    if db_ticket.urgency_score > 0.8:
        db_ticket.priority = "urgent"
    elif db_ticket.urgency_score > 0.6:
        db_ticket.priority = "high"
    elif db_ticket.urgency_score > 0.3:
        db_ticket.priority = "medium"
    else:
        db_ticket.priority = "low"
    
    # Save to database
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket


@router.get("/", response_model=List[TicketResponse])
def get_tickets(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    category: str = None,
    priority: str = None,
    db: Session = Depends(get_db)
):
    """Get all tickets with optional filters"""
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    if priority:
        query = query.filter(Ticket.priority == priority)
    
    tickets = query.offset(skip).limit(limit).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a specific ticket by ID"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket"""
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_data = ticket_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    
    # If status is being set to resolved, set resolved_at timestamp
    if ticket_update.status == TicketStatus.RESOLVED and not db_ticket.resolved_at:
        db_ticket.resolved_at = datetime.now()
    
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(ticket_id: int, assignment: TicketAssign, db: Session = Depends(get_db)):
    """Assign ticket to an agent"""
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if agent exists
    from models.ticket import Agent
    agent = db.query(Agent).filter(Agent.id == assignment.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent is available and has capacity
    if not agent.is_available or agent.current_ticket_count >= agent.max_tickets:
        raise HTTPException(status_code=400, detail="Agent is not available or at capacity")
    
    db_ticket.assigned_to = assignment.agent_id
    db_ticket.status = TicketStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Delete a ticket"""
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(db_ticket)
    db.commit()
    return None


@router.post("/{ticket_id}/responses", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_response(ticket_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    """Add a response to a ticket"""
    # Check if ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Create response
    db_response = TicketResponseModel(
        ticket_id=ticket_id,
        message=message.message,
        is_agent_response=message.is_agent_response,
        agent_name=message.agent_name
    )
    
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response


@router.get("/{ticket_id}/responses", response_model=List[MessageResponse])
def get_ticket_responses(ticket_id: int, db: Session = Depends(get_db)):
    """Get all responses for a ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket.responses


@router.post("/{ticket_id}/suggest-response")
async def suggest_response(ticket_id: int, db: Session = Depends(get_db)):
    """Get AI-suggested response for a ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Simple suggestion based on category
    suggestions = {
        "account": "Thank you for contacting support. I can help you with your account issue. Please verify your email address and I'll send you a password reset link.",
        "billing": "I apologize for the billing concern. I've reviewed your account and will process a refund within 3-5 business days.",
        "technical": "Thank you for reporting this issue. Our technical team is investigating. Please try clearing your cache and let us know if the problem persists.",
        "complaint": "I sincerely apologize for your experience. Your feedback is important to us. I'd like to understand the issue better - could you provide more details?",
        "feature_request": "Thank you for your suggestion! I've forwarded your feature request to our product team. We appreciate customer feedback.",
        "general": "Thank you for reaching out. I'm here to help. Could you provide more details about your inquiry?"
    }
    
    suggestion_text = suggestions.get(ticket.category, suggestions["general"])
    
    return {
        "suggested_text": suggestion_text,
        "confidence": 0.8,
        "source_tickets": [],
        "reasoning": f"Based on category: {ticket.category}"
    }