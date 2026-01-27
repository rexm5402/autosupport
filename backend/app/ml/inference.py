import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer
import pickle
import os
import logging
from typing import Dict, List
import re

from app.core.config import settings
from app.ml.rag_system import RAGSystem

logger = logging.getLogger(__name__)


class MLService:
    """Machine Learning service for ticket classification and analysis"""
    
    def __init__(self):
        self.classification_model = None
        self.classification_tokenizer = None
        self.sentiment_pipeline = None
        self.embedding_model = None
        self.rag_system = None
        self.label_mapping = {
            0: "technical",
            1: "billing",
            2: "account",
            3: "general",
            4: "complaint",
            5: "feature_request"
        }
        self.urgency_keywords = {
            "urgent": 1.0,
            "asap": 0.9,
            "immediately": 0.9,
            "critical": 0.95,
            "emergency": 1.0,
            "broken": 0.7,
            "not working": 0.7,
            "down": 0.8,
            "error": 0.6,
            "failed": 0.6,
            "cannot": 0.5,
            "unable": 0.5
        }
    
    async def load_models(self):
        """Load all ML models"""
        try:
            logger.info("Loading ML models...")
            
            # Load classification model
            model_path = os.path.join(settings.MODEL_PATH, "classifier.pkl")
            
            if os.path.exists(model_path):
                # Load fine-tuned model
                logger.info("Loading fine-tuned classification model...")
                with open(model_path, 'rb') as f:
                    self.classification_model = pickle.load(f)
                
                tokenizer_path = os.path.join(settings.MODEL_PATH, "tokenizer")
                if os.path.exists(tokenizer_path):
                    self.classification_tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
                else:
                    self.classification_tokenizer = AutoTokenizer.from_pretrained(settings.CLASSIFICATION_MODEL)
            else:
                # Use simple sklearn model as fallback
                logger.info("Using fallback classification model...")
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.naive_bayes import MultinomialNB
                
                self.classification_model = MultinomialNB()
                self.classification_tokenizer = TfidfVectorizer(max_features=1000)
            
            # Load sentiment analysis pipeline
            logger.info("Loading sentiment model...")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=settings.SENTIMENT_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Load embedding model for RAG
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Initialize RAG system
            logger.info("Initializing RAG system...")
            self.rag_system = RAGSystem(self.embedding_model)
            await self.rag_system.initialize()
            
            logger.info("All models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}", exc_info=True)
            raise
    
    def is_ready(self) -> bool:
        """Check if ML service is ready"""
        return (
            self.classification_model is not None and
            self.sentiment_pipeline is not None and
            self.embedding_model is not None
        )
    
    async def classify_ticket(self, text: str) -> Dict:
        """Classify ticket into categories"""
        if not self.is_ready():
            raise Exception("ML models not loaded")
        
        try:
            # Simple keyword-based classification as fallback
            text_lower = text.lower()
            
            # Category keywords
            categories = {
                "billing": ["payment", "charge", "invoice", "bill", "refund", "subscription"],
                "technical": ["error", "bug", "not working", "broken", "crash", "issue", "problem"],
                "account": ["password", "login", "access", "account", "sign in", "username"],
                "complaint": ["disappointed", "upset", "angry", "terrible", "worst", "complaint"],
                "feature_request": ["feature", "would like", "suggestion", "add", "implement", "wish"],
                "general": ["question", "help", "how to", "what", "when", "where"]
            }
            
            # Calculate scores for each category
            scores = {}
            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[category] = score
            
            # Get best category
            if max(scores.values()) > 0:
                best_category = max(scores, key=scores.get)
                confidence = min(scores[best_category] / 5.0, 1.0)  # Normalize to 0-1
            else:
                best_category = "general"
                confidence = 0.5
            
            # Normalize all scores
            total_score = sum(scores.values()) if sum(scores.values()) > 0 else 1
            all_predictions = {cat: score / total_score for cat, score in scores.items()}
            
            return {
                "category": best_category,
                "confidence": confidence,
                "all_predictions": all_predictions
            }
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return {
                "category": "general",
                "confidence": 0.5,
                "all_predictions": {"general": 1.0}
            }
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment and calculate urgency score"""
        if not self.is_ready():
            raise Exception("ML models not loaded")
        
        try:
            # Get sentiment from model
            sentiment_result = self.sentiment_pipeline(text[:512])[0]  # Truncate to model max length
            
            sentiment_label = sentiment_result['label'].lower()
            sentiment_score = sentiment_result['score']
            
            # Map LABEL_0/LABEL_1 to sentiment
            if 'negative' in sentiment_label or sentiment_label == 'label_0':
                sentiment = "negative"
            elif 'positive' in sentiment_label or sentiment_label == 'label_1':
                sentiment = "positive"
            else:
                sentiment = "neutral"
            
            # Calculate urgency score based on keywords
            text_lower = text.lower()
            urgency_score = 0.3  # Base urgency
            
            for keyword, weight in self.urgency_keywords.items():
                if keyword in text_lower:
                    urgency_score = max(urgency_score, weight)
            
            # Adjust urgency based on sentiment
            if sentiment == "negative":
                urgency_score = min(urgency_score + 0.2, 1.0)
            
            # Check for exclamation marks and caps
            if text.count('!') > 2:
                urgency_score = min(urgency_score + 0.1, 1.0)
            
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
            if caps_ratio > 0.3:
                urgency_score = min(urgency_score + 0.15, 1.0)
            
            return {
                "sentiment": sentiment,
                "score": sentiment_score,
                "urgency_score": round(urgency_score, 2)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "urgency_score": 0.5
            }
    
    async def suggest_response(self, ticket_text: str, category: str = None) -> Dict:
        """Generate suggested response using RAG system"""
        if not self.rag_system:
            return {
                "suggested_text": "Thank you for contacting support. We are looking into your issue and will get back to you shortly.",
                "confidence": 0.5,
                "source_tickets": [],
                "reasoning": "RAG system not initialized, using default response"
            }
        
        try:
            return await self.rag_system.generate_response(ticket_text, category)
        except Exception as e:
            logger.error(f"Response suggestion error: {str(e)}")
            return {
                "suggested_text": "Thank you for contacting support. We are looking into your issue and will get back to you shortly.",
                "confidence": 0.3,
                "source_tickets": [],
                "reasoning": f"Error generating response: {str(e)}"
            }
