"""
Database seeding script for AutoSupport

This script populates the database with sample data for testing

Run: python scripts/seed_data.py
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from models.ticket import Agent, Ticket, KnowledgeBase, TicketStatus, TicketPriority, TicketCategory
from datetime import datetime, timedelta
import random

def seed_agents():
    """Create sample agents"""
    db = SessionLocal()
    
    agents = [
        {
            "name": "Alice Johnson",
            "email": "alice@autosupport.com",
            "expertise": "technical,general",
            "max_tickets": 15,
            "is_available": True,
            "total_tickets_handled": 45,
            "average_resolution_time": 2.5,
            "customer_satisfaction_score": 4.7
        },
        {
            "name": "Bob Smith",
            "email": "bob@autosupport.com",
            "expertise": "billing,account",
            "max_tickets": 12,
            "is_available": True,
            "total_tickets_handled": 38,
            "average_resolution_time": 1.8,
            "customer_satisfaction_score": 4.9
        },
        {
            "name": "Carol Williams",
            "email": "carol@autosupport.com",
            "expertise": "technical,feature_request",
            "max_tickets": 10,
            "is_available": True,
            "total_tickets_handled": 52,
            "average_resolution_time": 3.2,
            "customer_satisfaction_score": 4.5
        },
        {
            "name": "David Brown",
            "email": "david@autosupport.com",
            "expertise": "complaint,general",
            "max_tickets": 8,
            "is_available": False,
            "total_tickets_handled": 29,
            "average_resolution_time": 4.1,
            "customer_satisfaction_score": 4.3
        }
    ]
    
    for agent_data in agents:
        agent = Agent(**agent_data)
        db.add(agent)
    
    db.commit()
    print(f"✅ Created {len(agents)} agents")
    db.close()


def seed_tickets():
    """Create sample tickets"""
    db = SessionLocal()
    
    # Get agents
    agents = db.query(Agent).all()
    
    sample_tickets = [
        {
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "subject": "Cannot login to my account",
            "description": "I've been trying to login for the past hour but keep getting an 'invalid credentials' error even though I'm sure my password is correct.",
            "category": TicketCategory.ACCOUNT,
            "priority": TicketPriority.HIGH,
            "status": TicketStatus.IN_PROGRESS,
            "sentiment": "negative",
            "urgency_score": 0.75
        },
        {
            "customer_name": "Jane Smith",
            "customer_email": "jane@example.com",
            "subject": "App crashes when uploading files",
            "description": "Every time I try to upload a PDF file larger than 5MB, the application crashes. This is very frustrating as I need to upload important documents.",
            "category": TicketCategory.TECHNICAL,
            "priority": TicketPriority.URGENT,
            "status": TicketStatus.OPEN,
            "sentiment": "negative",
            "urgency_score": 0.85
        },
        {
            "customer_name": "Mike Johnson",
            "customer_email": "mike@example.com",
            "subject": "Double charged for subscription",
            "description": "I noticed I was charged twice for my monthly subscription. Can you please refund the duplicate charge?",
            "category": TicketCategory.BILLING,
            "priority": TicketPriority.HIGH,
            "status": TicketStatus.RESOLVED,
            "sentiment": "neutral",
            "urgency_score": 0.6,
            "resolved_at": datetime.now() - timedelta(hours=3)
        },
        {
            "customer_name": "Sarah Williams",
            "customer_email": "sarah@example.com",
            "subject": "How to export data to CSV?",
            "description": "I'd like to export all my data to a CSV file. Could you guide me through the process?",
            "category": TicketCategory.GENERAL,
            "priority": TicketPriority.LOW,
            "status": TicketStatus.RESOLVED,
            "sentiment": "positive",
            "urgency_score": 0.3,
            "resolved_at": datetime.now() - timedelta(hours=1)
        },
        {
            "customer_name": "Tom Brown",
            "customer_email": "tom@example.com",
            "subject": "Disappointed with recent changes",
            "description": "The recent update has made the interface much more confusing. I'm seriously considering switching to a competitor. This is very disappointing.",
            "category": TicketCategory.COMPLAINT,
            "priority": TicketPriority.MEDIUM,
            "status": TicketStatus.IN_PROGRESS,
            "sentiment": "negative",
            "urgency_score": 0.5
        },
        {
            "customer_name": "Emily Davis",
            "customer_email": "emily@example.com",
            "subject": "Feature request: Dark mode",
            "description": "Would love to see a dark mode option added to the application. It would be much easier on the eyes during nighttime use.",
            "category": TicketCategory.FEATURE_REQUEST,
            "priority": TicketPriority.LOW,
            "status": TicketStatus.OPEN,
            "sentiment": "positive",
            "urgency_score": 0.2
        }
    ]
    
    for idx, ticket_data in enumerate(sample_tickets):
        # Generate ticket number
        ticket_data["ticket_number"] = f"TKT-{datetime.now().strftime('%Y%m%d')}-{idx+1:04d}"
        
        # Assign to random agent if in progress or resolved
        if ticket_data["status"] in [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED] and agents:
            ticket_data["assigned_to"] = random.choice(agents).id
        
        # Add created_at
        days_ago = random.randint(0, 7)
        ticket_data["created_at"] = datetime.now() - timedelta(days=days_ago)
        
        ticket = Ticket(**ticket_data)
        db.add(ticket)
    
    db.commit()
    print(f"✅ Created {len(sample_tickets)} tickets")
    db.close()


def seed_knowledge_base():
    """Create sample knowledge base articles"""
    db = SessionLocal()
    
    articles = [
        {
            "title": "How to Reset Your Password",
            "content": "To reset your password: 1) Click on 'Forgot Password' on the login page, 2) Enter your email address, 3) Check your email for the reset link, 4) Click the link and create a new password, 5) Login with your new password.",
            "category": TicketCategory.ACCOUNT,
            "tags": "password,reset,login,account",
            "view_count": 250,
            "helpful_count": 230
        },
        {
            "title": "Understanding Your Bill",
            "content": "Your monthly bill includes: base subscription fee, any add-on services, taxes, and previous balance. Charges appear on the 1st of each month. Contact support if you notice any discrepancies.",
            "category": TicketCategory.BILLING,
            "tags": "billing,payment,invoice,charges",
            "view_count": 180,
            "helpful_count": 165
        },
        {
            "title": "Troubleshooting Upload Issues",
            "content": "If you're having trouble uploading files: 1) Check file size (max 10MB), 2) Ensure file format is supported, 3) Clear browser cache, 4) Try a different browser, 5) Disable browser extensions temporarily.",
            "category": TicketCategory.TECHNICAL,
            "tags": "upload,file,error,troubleshooting",
            "view_count": 320,
            "helpful_count": 295
        }
    ]
    
    for article_data in articles:
        article = KnowledgeBase(**article_data)
        db.add(article)
    
    db.commit()
    print(f"✅ Created {len(articles)} knowledge base articles")
    db.close()


def main():
    """Run all seeding functions"""
    print("🌱 Seeding database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Seed data
    seed_agents()
    seed_tickets()
    seed_knowledge_base()
    
    print("\n🎉 Database seeding complete!")


if __name__ == "__main__":
    main()
