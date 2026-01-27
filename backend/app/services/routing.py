from sqlalchemy.orm import Session
from models.ticket import Ticket, Agent, TicketStatus
import logging

logger = logging.getLogger(__name__)


async def route_ticket_to_agent(ticket_id: int, db: Session) -> bool:
    """
    Automatically route a ticket to the best available agent
    
    Routing algorithm considers:
    1. Agent expertise matching ticket category
    2. Current workload
    3. Agent availability
    4. Historical performance
    """
    
    try:
        # Get the ticket
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found")
            return False
        
        # Get all available agents
        available_agents = db.query(Agent).filter(
            Agent.is_active == True,
            Agent.is_available == True
        ).all()
        
        if not available_agents:
            logger.warning("No available agents for routing")
            return False
        
        # Score each agent
        agent_scores = []
        
        for agent in available_agents:
            score = 0.0
            
            # 1. Expertise matching (40% weight)
            if ticket.category and agent.expertise:
                expertise_list = [e.strip().lower() for e in agent.expertise.split(',')]
                if ticket.category.value in expertise_list:
                    score += 40
                elif 'general' in expertise_list:
                    score += 20
            else:
                score += 15  # Base score if no category
            
            # 2. Workload (30% weight)
            current_tickets = agent.current_ticket_count
            capacity_utilization = current_tickets / agent.max_tickets if agent.max_tickets > 0 else 1.0
            workload_score = (1.0 - capacity_utilization) * 30
            score += workload_score
            
            # 3. Check if agent has capacity
            if current_tickets >= agent.max_tickets:
                score = 0  # Agent at capacity, can't assign
                continue
            
            # 4. Historical performance (20% weight)
            if agent.customer_satisfaction_score > 0:
                performance_score = (agent.customer_satisfaction_score / 5.0) * 20
                score += performance_score
            else:
                score += 10  # Base score for new agents
            
            # 5. Resolution time (10% weight) - faster is better
            if agent.average_resolution_time > 0:
                # Normalize resolution time (assuming 24 hours is poor, <1 hour is excellent)
                time_score = max(0, (24 - agent.average_resolution_time) / 24 * 10)
                score += time_score
            else:
                score += 5  # Base score
            
            agent_scores.append((agent, score))
        
        # Sort by score and select best agent
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        if agent_scores and agent_scores[0][1] > 0:
            best_agent = agent_scores[0][0]
            
            # Assign ticket
            ticket.assigned_to = best_agent.id
            ticket.status = TicketStatus.IN_PROGRESS
            
            db.commit()
            
            logger.info(f"Ticket {ticket_id} routed to agent {best_agent.name} (score: {agent_scores[0][1]:.2f})")
            return True
        else:
            logger.warning(f"No suitable agent found for ticket {ticket_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error routing ticket {ticket_id}: {str(e)}", exc_info=True)
        db.rollback()
        return False


def calculate_routing_metrics(db: Session) -> dict:
    """Calculate routing performance metrics"""
    
    try:
        # Get all assigned tickets
        assigned_tickets = db.query(Ticket).filter(
            Ticket.assigned_to.isnot(None)
        ).all()
        
        if not assigned_tickets:
            return {
                "total_assigned": 0,
                "average_time_to_assign": 0,
                "routing_accuracy": 0
            }
        
        # Calculate average time to assignment
        assignment_times = []
        for ticket in assigned_tickets:
            if ticket.updated_at and ticket.created_at:
                time_diff = (ticket.updated_at - ticket.created_at).total_seconds() / 60  # in minutes
                assignment_times.append(time_diff)
        
        avg_assignment_time = sum(assignment_times) / len(assignment_times) if assignment_times else 0
        
        # Calculate routing accuracy (tickets resolved by assigned agent)
        resolved_by_assigned = len([
            t for t in assigned_tickets 
            if t.status == TicketStatus.RESOLVED
        ])
        
        routing_accuracy = (resolved_by_assigned / len(assigned_tickets) * 100) if assigned_tickets else 0
        
        return {
            "total_assigned": len(assigned_tickets),
            "average_time_to_assign": round(avg_assignment_time, 2),
            "routing_accuracy": round(routing_accuracy, 2)
        }
        
    except Exception as e:
        logger.error(f"Error calculating routing metrics: {str(e)}")
        return {
            "total_assigned": 0,
            "average_time_to_assign": 0,
            "routing_accuracy": 0
        }
