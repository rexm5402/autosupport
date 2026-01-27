import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import logging
from typing import Dict, List
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGSystem:
    """Retrieval-Augmented Generation system for response suggestions"""
    
    def __init__(self, embedding_model: SentenceTransformer):
        self.embedding_model = embedding_model
        self.client = None
        self.collection = None
        
    async def initialize(self):
        """Initialize ChromaDB and collection"""
        try:
            logger.info("Initializing RAG system...")
            
            # Create ChromaDB client
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=settings.CHROMA_COLLECTION_NAME
                )
                logger.info(f"Loaded existing collection: {settings.CHROMA_COLLECTION_NAME}")
            except:
                self.collection = self.client.create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"description": "Support ticket responses"}
                )
                logger.info(f"Created new collection: {settings.CHROMA_COLLECTION_NAME}")
                
                # Add some sample responses
                await self.add_sample_responses()
            
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {str(e)}", exc_info=True)
            raise
    
    async def add_sample_responses(self):
        """Add sample ticket responses to the knowledge base"""
        
        sample_responses = [
            {
                "ticket": "My password is not working and I cannot login to my account",
                "response": "Thank you for reaching out. I can help you reset your password. Please click on the 'Forgot Password' link on the login page and follow the instructions sent to your registered email. If you don't receive the email within 5 minutes, please check your spam folder or contact us again.",
                "category": "account",
                "metadata": {"resolution_time": "5min", "satisfaction": "high"}
            },
            {
                "ticket": "I was charged twice for my subscription this month",
                "response": "I apologize for the inconvenience. I can see the duplicate charge on your account. We'll process a refund for the extra charge within 3-5 business days. You should see it reflected in your account shortly. Is there anything else I can help you with?",
                "category": "billing",
                "metadata": {"resolution_time": "10min", "satisfaction": "high"}
            },
            {
                "ticket": "The application keeps crashing when I try to upload files",
                "response": "Thank you for reporting this issue. This appears to be related to file size limits. Please try the following: 1) Ensure your files are under 10MB, 2) Clear your browser cache, 3) Try using a different browser. If the issue persists, please send us the error logs and we'll investigate further.",
                "category": "technical",
                "metadata": {"resolution_time": "15min", "satisfaction": "medium"}
            },
            {
                "ticket": "I would like to suggest a feature for the mobile app",
                "response": "Thank you for your valuable feedback! We really appreciate customers who take the time to suggest improvements. I've forwarded your feature request to our product team. While I can't guarantee it will be implemented, all suggestions are carefully reviewed. We'll keep you updated if this feature is added to our roadmap.",
                "category": "feature_request",
                "metadata": {"resolution_time": "5min", "satisfaction": "high"}
            },
            {
                "ticket": "I am very disappointed with the service quality lately",
                "response": "I sincerely apologize that we haven't met your expectations. Your satisfaction is very important to us. I'd like to understand the specific issues you've encountered so we can make this right. Could you please provide more details about what happened? I'm here to help and will do everything I can to resolve this for you.",
                "category": "complaint",
                "metadata": {"resolution_time": "10min", "satisfaction": "medium"}
            },
            {
                "ticket": "How do I export my data from the platform?",
                "response": "Great question! You can export your data by following these steps: 1) Go to Settings > Data Management, 2) Click on 'Export Data', 3) Select the data types you want to export, 4) Click 'Generate Export'. You'll receive an email with a download link within 24 hours. The export will be in CSV format. Let me know if you need any other assistance!",
                "category": "general",
                "metadata": {"resolution_time": "5min", "satisfaction": "high"}
            }
        ]
        
        # Add responses to collection
        for idx, item in enumerate(sample_responses):
            # Create embedding
            embedding = self.embedding_model.encode(item["ticket"]).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[item["response"]],
                metadatas=[{
                    "category": item["category"],
                    "ticket_text": item["ticket"],
                    **item["metadata"]
                }],
                ids=[f"sample_{idx}"]
            )
        
        logger.info(f"Added {len(sample_responses)} sample responses to knowledge base")
    
    async def add_ticket_response(self, ticket_text: str, response: str, category: str, ticket_id: str):
        """Add a resolved ticket and its response to the knowledge base"""
        try:
            # Create embedding
            embedding = self.embedding_model.encode(ticket_text).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[response],
                metadatas=[{
                    "category": category,
                    "ticket_text": ticket_text,
                    "ticket_id": ticket_id
                }],
                ids=[f"ticket_{ticket_id}"]
            )
            
            logger.info(f"Added ticket {ticket_id} to knowledge base")
            
        except Exception as e:
            logger.error(f"Error adding ticket to knowledge base: {str(e)}")
    
    async def generate_response(self, ticket_text: str, category: str = None) -> Dict:
        """Generate response suggestion based on similar tickets"""
        try:
            # Create embedding for the query
            query_embedding = self.embedding_model.encode(ticket_text).tolist()
            
            # Build where clause for category filtering
            where_clause = {"category": category} if category else None
            
            # Query similar tickets
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=3,
                where=where_clause
            )
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    "suggested_text": "Thank you for contacting support. We are reviewing your request and will respond shortly.",
                    "confidence": 0.3,
                    "source_tickets": [],
                    "reasoning": "No similar tickets found in knowledge base"
                }
            
            # Get the most relevant response
            top_response = results['documents'][0][0]
            top_distance = results['distances'][0][0] if results['distances'] else 1.0
            
            # Calculate confidence based on similarity (lower distance = higher confidence)
            confidence = max(0.0, min(1.0, 1.0 - top_distance))
            
            # Get source ticket information
            source_tickets = []
            for idx, metadata in enumerate(results['metadatas'][0][:3]):
                source_tickets.append({
                    "ticket_text": metadata.get("ticket_text", ""),
                    "category": metadata.get("category", ""),
                    "similarity": round(1.0 - results['distances'][0][idx], 2)
                })
            
            # Generate reasoning
            reasoning = f"Found {len(source_tickets)} similar resolved tickets. "
            reasoning += f"Best match has {round(confidence * 100)}% similarity. "
            if category:
                reasoning += f"Filtered by category: {category}."
            
            return {
                "suggested_text": top_response,
                "confidence": round(confidence, 2),
                "source_tickets": source_tickets,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "suggested_text": "Thank you for contacting support. We are looking into your issue.",
                "confidence": 0.2,
                "source_tickets": [],
                "reasoning": f"Error: {str(e)}"
            }
    
    async def search_knowledge_base(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            knowledge_items = []
            for idx, doc in enumerate(results['documents'][0]):
                knowledge_items.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][idx],
                    "similarity": round(1.0 - results['distances'][0][idx], 2)
                })
            
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
