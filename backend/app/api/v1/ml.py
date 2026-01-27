from fastapi import APIRouter, HTTPException
from app.schemas import ClassificationRequest, ClassificationResponse, SentimentResponse

router = APIRouter()


@router.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    """Classify ticket text into categories"""
    
    text_lower = request.text.lower()
    
    # Simple keyword-based classification
    categories = {
        "billing": ["payment", "charge", "invoice", "bill", "refund", "subscription"],
        "technical": ["error", "bug", "not working", "broken", "crash", "issue", "problem"],
        "account": ["password", "login", "access", "account", "sign in", "username"],
        "complaint": ["disappointed", "upset", "angry", "terrible", "worst", "complaint"],
        "feature_request": ["feature", "would like", "suggestion", "add", "implement", "wish"],
        "general": ["question", "help", "how to", "what", "when", "where"]
    }
    
    # Calculate scores
    scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[category] = score
    
    # Get best category
    if max(scores.values()) > 0:
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 5.0, 1.0)
    else:
        best_category = "general"
        confidence = 0.5
    
    # Normalize scores
    total_score = sum(scores.values()) if sum(scores.values()) > 0 else 1
    all_predictions = {cat: score / total_score for cat, score in scores.items()}
    
    return ClassificationResponse(
        category=best_category,
        confidence=confidence,
        all_predictions=all_predictions
    )


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: ClassificationRequest):
    """Analyze sentiment and urgency of ticket text"""
    
    text_lower = request.text.lower()
    
    # Simple sentiment analysis
    negative_words = ['angry', 'terrible', 'worst', 'disappointed', 'frustrated', 'broken', 'upset']
    positive_words = ['great', 'good', 'thanks', 'appreciate', 'helpful', 'excellent', 'amazing']
    
    neg_count = sum(1 for word in negative_words if word in text_lower)
    pos_count = sum(1 for word in positive_words if word in text_lower)
    
    if neg_count > pos_count:
        sentiment = "negative"
        score = 0.3
    elif pos_count > neg_count:
        sentiment = "positive"
        score = 0.8
    else:
        sentiment = "neutral"
        score = 0.5
    
    # Calculate urgency
    urgency_keywords = {
        "urgent": 1.0,
        "asap": 0.9,
        "immediately": 0.9,
        "critical": 0.95,
        "emergency": 1.0,
        "broken": 0.7,
        "not working": 0.7,
        "down": 0.8,
    }
    
    urgency_score = 0.3  # Base
    for keyword, weight in urgency_keywords.items():
        if keyword in text_lower:
            urgency_score = max(urgency_score, weight)
    
    # Adjust for sentiment
    if sentiment == "negative":
        urgency_score = min(urgency_score + 0.2, 1.0)
    
    return SentimentResponse(
        sentiment=sentiment,
        score=score,
        urgency_score=round(urgency_score, 2)
    )


@router.post("/suggest-response")
async def suggest_response(request: ClassificationRequest, category: str = None):
    """Get AI-suggested response for ticket text"""
    
    # Classify first if no category
    if not category:
        classification = await classify_text(request)
        category = classification.category
    
    suggestions = {
        "account": "Thank you for contacting support. I can help you with your account issue. Please verify your email address and I'll send you a password reset link.",
        "billing": "I apologize for the billing concern. I've reviewed your account and will process a refund within 3-5 business days.",
        "technical": "Thank you for reporting this issue. Our technical team is investigating. Please try clearing your cache and let us know if the problem persists.",
        "complaint": "I sincerely apologize for your experience. Your feedback is important to us. I'd like to understand the issue better - could you provide more details?",
        "feature_request": "Thank you for your suggestion! I've forwarded your feature request to our product team. We appreciate customer feedback.",
        "general": "Thank you for reaching out. I'm here to help. Could you provide more details about your inquiry?"
    }
    
    suggestion_text = suggestions.get(category, suggestions["general"])
    
    return {
        "suggested_text": suggestion_text,
        "confidence": 0.8,
        "source_tickets": [],
        "reasoning": f"Based on category: {category}"
    }


@router.get("/models/status")
async def get_models_status():
    """Get status of loaded ML models"""
    
    return {
        "classification_model": True,
        "sentiment_model": True,
        "embedding_model": False,
        "rag_system": False,
        "note": "Using rule-based classification for now"
    }


@router.post("/models/reload")
async def reload_models():
    """Reload ML models (useful after training)"""
    
    return {
        "status": "success", 
        "message": "Models reloaded successfully (using rule-based system)"
    }