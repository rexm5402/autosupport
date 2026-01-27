from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas import AgentCreate, AgentUpdate, AgentResponse
from models.ticket import Agent

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent"""
    
    # Check if email already exists
    existing_agent = db.query(Agent).filter(Agent.email == agent.email).first()
    if existing_agent:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_agent = Agent(
        name=agent.name,
        email=agent.email,
        expertise=agent.expertise,
        max_tickets=agent.max_tickets
    )
    
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.get("/", response_model=List[AgentResponse])
def get_agents(
    skip: int = 0,
    limit: int = 100,
    is_available: bool = None,
    db: Session = Depends(get_db)
):
    """Get all agents"""
    query = db.query(Agent)
    
    if is_available is not None:
        query = query.filter(Agent.is_available == is_available)
    
    agents = query.offset(skip).limit(limit).all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get a specific agent by ID"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """Update an agent"""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete an agent (soft delete by setting is_active=False)"""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Soft delete
    db_agent.is_active = False
    db.commit()
    return None


@router.get("/{agent_id}/tickets")
def get_agent_tickets(agent_id: int, db: Session = Depends(get_db)):
    """Get all tickets assigned to an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.tickets


@router.get("/{agent_id}/stats")
def get_agent_stats(agent_id: int, db: Session = Depends(get_db)):
    """Get performance statistics for an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    from models.ticket import TicketStatus
    
    open_tickets = len([t for t in agent.tickets if t.status == TicketStatus.OPEN])
    in_progress_tickets = len([t for t in agent.tickets if t.status == TicketStatus.IN_PROGRESS])
    resolved_tickets = len([t for t in agent.tickets if t.status == TicketStatus.RESOLVED])
    
    return {
        "agent_id": agent.id,
        "name": agent.name,
        "current_workload": {
            "open": open_tickets,
            "in_progress": in_progress_tickets,
            "total_active": open_tickets + in_progress_tickets
        },
        "performance": {
            "total_handled": agent.total_tickets_handled,
            "resolved": resolved_tickets,
            "avg_resolution_time": agent.average_resolution_time,
            "satisfaction_score": agent.customer_satisfaction_score
        },
        "capacity": {
            "max_tickets": agent.max_tickets,
            "current_tickets": agent.current_ticket_count,
            "available_slots": agent.max_tickets - agent.current_ticket_count
        }
    }
