from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import get_db
from models.ticket import Ticket, Agent, TicketStatus, TicketCategory, TicketPriority

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get comprehensive dashboard analytics"""
    
    # Ticket statistics
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    in_progress = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()
    closed = db.query(Ticket).filter(Ticket.status == TicketStatus.CLOSED).count()
    
    # Category distribution
    category_counts = db.query(
        Ticket.category, 
        func.count(Ticket.id)
    ).group_by(Ticket.category).all()
    
    tickets_by_category = {cat: count for cat, count in category_counts if cat}
    
    # Priority distribution
    priority_counts = db.query(
        Ticket.priority,
        func.count(Ticket.id)
    ).group_by(Ticket.priority).all()
    
    tickets_by_priority = {pri: count for pri, count in priority_counts}
    
    # Sentiment distribution
    sentiment_counts = db.query(
        Ticket.sentiment,
        func.count(Ticket.id)
    ).group_by(Ticket.sentiment).all()
    
    sentiment_distribution = {sent: count for sent, count in sentiment_counts if sent}
    
    # Average resolution time
    resolved_tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.RESOLVED,
        Ticket.resolved_at.isnot(None)
    ).all()
    
    if resolved_tickets:
        resolution_times = [
            (t.resolved_at - t.created_at).total_seconds() / 3600  # in hours
            for t in resolved_tickets
        ]
        avg_resolution_time = sum(resolution_times) / len(resolution_times)
    else:
        avg_resolution_time = 0.0
    
    # Agent statistics
    total_agents = db.query(Agent).filter(Agent.is_active == True).count()
    available_agents = db.query(Agent).filter(
        Agent.is_active == True,
        Agent.is_available == True
    ).count()
    
    # Top performing agents
    agents = db.query(Agent).filter(Agent.is_active == True).all()
    top_performers = sorted(
        [
            {
                "id": agent.id,
                "name": agent.name,
                "tickets_handled": agent.total_tickets_handled,
                "avg_resolution_time": agent.average_resolution_time,
                "satisfaction_score": agent.customer_satisfaction_score
            }
            for agent in agents
        ],
        key=lambda x: x["satisfaction_score"],
        reverse=True
    )[:5]
    
    return {
        "ticket_stats": {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress,
            "resolved_tickets": resolved,
            "closed_tickets": closed,
            "average_resolution_time": round(avg_resolution_time, 2),
            "tickets_by_category": tickets_by_category,
            "tickets_by_priority": tickets_by_priority,
            "sentiment_distribution": sentiment_distribution
        },
        "agent_stats": {
            "total_agents": total_agents,
            "available_agents": available_agents,
            "busy_agents": total_agents - available_agents,
            "average_tickets_per_agent": round(total_tickets / total_agents, 2) if total_agents > 0 else 0,
            "top_performers": top_performers
        },
        "trends": get_ticket_trends(db)
    }


def get_ticket_trends(db: Session):
    """Get ticket trends over time"""
    
    # Get tickets from last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_tickets = db.query(Ticket).filter(
        Ticket.created_at >= thirty_days_ago
    ).all()
    
    # Group by day
    daily_counts = defaultdict(int)
    for ticket in recent_tickets:
        day = ticket.created_at.date()
        daily_counts[str(day)] += 1
    
    # Sort by date
    sorted_trends = dict(sorted(daily_counts.items()))
    
    # Category trends
    category_trends = defaultdict(lambda: defaultdict(int))
    for ticket in recent_tickets:
        if ticket.category:
            day = ticket.created_at.date()
            category_trends[ticket.category][str(day)] += 1
    
    return {
        "daily_ticket_count": sorted_trends,
        "category_trends": dict(category_trends),
        "total_last_30_days": len(recent_tickets)
    }


@router.get("/trends")
def get_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get ticket trends for specified number of days"""
    
    start_date = datetime.now() - timedelta(days=days)
    tickets = db.query(Ticket).filter(Ticket.created_at >= start_date).all()
    
    # Daily trends
    daily_counts = defaultdict(int)
    for ticket in tickets:
        day = ticket.created_at.date()
        daily_counts[str(day)] += 1
    
    return {
        "period_days": days,
        "total_tickets": len(tickets),
        "daily_breakdown": dict(sorted(daily_counts.items()))
    }


@router.get("/top-issues")
def get_top_issues(limit: int = 10, db: Session = Depends(get_db)):
    """Get most common issues based on ticket categories and keywords"""
    
    # Category-based issues
    category_counts = db.query(
        Ticket.category,
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.category.isnot(None)
    ).group_by(
        Ticket.category
    ).order_by(
        func.count(Ticket.id).desc()
    ).limit(limit).all()
    
    return {
        "top_categories": [
            {"category": cat, "count": count}
            for cat, count in category_counts
        ]
    }


@router.get("/performance")
def get_performance_metrics(db: Session = Depends(get_db)):
    """Get overall system performance metrics"""
    
    # Response time metrics
    total_tickets = db.query(Ticket).count()
    
    # First response time (time to first agent assignment)
    assigned_tickets = db.query(Ticket).filter(
        Ticket.assigned_to.isnot(None)
    ).all()
    
    # Resolution metrics
    resolved_tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.RESOLVED
    ).all()
    
    resolution_rate = (len(resolved_tickets) / total_tickets * 100) if total_tickets > 0 else 0
    
    # Agent utilization
    agents = db.query(Agent).filter(Agent.is_active == True).all()
    total_capacity = sum(agent.max_tickets for agent in agents)
    current_load = sum(agent.current_ticket_count for agent in agents)
    utilization_rate = (current_load / total_capacity * 100) if total_capacity > 0 else 0
    
    return {
        "resolution_rate": round(resolution_rate, 2),
        "total_tickets": total_tickets,
        "resolved_tickets": len(resolved_tickets),
        "agent_utilization": round(utilization_rate, 2),
        "total_capacity": total_capacity,
        "current_load": current_load
    }
