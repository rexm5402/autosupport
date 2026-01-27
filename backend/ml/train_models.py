"""
Training script for AutoSupport ML models

This script trains:
1. Ticket classification model
2. Saves models for inference

Run: python ml/train_models.py
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_dataset():
    """Create sample training data if no dataset is provided"""
    
    data = {
        'text': [
            # Technical issues
            "The app crashes every time I try to upload a file",
            "I'm getting an error message when logging in",
            "The website is not loading properly on my browser",
            "My data is not syncing across devices",
            "The search feature is not working",
            
            # Billing issues
            "I was charged twice this month",
            "I want to cancel my subscription",
            "The payment didn't go through",
            "I need a refund for the last charge",
            "My credit card was declined",
            
            # Account issues
            "I forgot my password and can't reset it",
            "Cannot access my account",
            "Need to update my email address",
            "How do I delete my account?",
            "My account is locked",
            
            # General inquiries
            "How do I export my data?",
            "What are the different pricing plans?",
            "Do you have a mobile app?",
            "Is there a way to customize the dashboard?",
            "How long does it take to process requests?",
            
            # Complaints
            "I'm very disappointed with the service",
            "This is the worst experience I've had",
            "Your customer support is terrible",
            "I'm canceling because of poor quality",
            "The service has been down too often",
            
            # Feature requests
            "Can you add dark mode to the app?",
            "I would like to see integration with Slack",
            "Please add export to PDF feature",
            "Could you implement two-factor authentication?",
            "I suggest adding a mobile notification system"
        ],
        'category': [
            # Technical
            'technical', 'technical', 'technical', 'technical', 'technical',
            # Billing
            'billing', 'billing', 'billing', 'billing', 'billing',
            # Account
            'account', 'account', 'account', 'account', 'account',
            # General
            'general', 'general', 'general', 'general', 'general',
            # Complaints
            'complaint', 'complaint', 'complaint', 'complaint', 'complaint',
            # Feature requests
            'feature_request', 'feature_request', 'feature_request', 
            'feature_request', 'feature_request'
        ]
    }
    
    return pd.DataFrame(data)


def train_classification_model(data_path=None):
    """Train the ticket classification model"""
    
    logger.info("Starting model training...")
    
    # Load data
    if data_path and os.path.exists(data_path):
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
    else:
        logger.info("Using sample dataset")
        df = create_sample_dataset()
    
    logger.info(f"Dataset size: {len(df)} samples")
    logger.info(f"Categories: {df['category'].unique()}")
    
    # Prepare data
    X = df['text']
    y = df['category']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        stop_words='english'
    )
    
    # Transform data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train model
    logger.info("Training Naive Bayes classifier...")
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"\nModel Accuracy: {accuracy:.4f}")
    logger.info("\nClassification Report:")
    logger.info(classification_report(y_test, y_pred))
    
    # Save models
    os.makedirs('./models', exist_ok=True)
    
    logger.info("Saving models...")
    
    # Save classifier
    with open('./models/classifier.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Save vectorizer
    with open('./models/vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    logger.info("Models saved successfully!")
    
    return model, vectorizer, accuracy


def test_model():
    """Test the trained model with sample inputs"""
    
    logger.info("\nTesting model with sample inputs...")
    
    # Load models
    with open('./models/classifier.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('./models/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    
    # Test samples
    test_samples = [
        "I can't login to my account, forgot password",
        "The app keeps freezing when I upload files",
        "I was charged three times for the same purchase",
        "How do I change my subscription plan?",
        "Your service is terrible and I want my money back",
        "Can you add a feature to export data to Excel?"
    ]
    
    for sample in test_samples:
        sample_tfidf = vectorizer.transform([sample])
        prediction = model.predict(sample_tfidf)[0]
        probabilities = model.predict_proba(sample_tfidf)[0]
        confidence = max(probabilities)
        
        logger.info(f"\nText: {sample}")
        logger.info(f"Predicted Category: {prediction}")
        logger.info(f"Confidence: {confidence:.2f}")


if __name__ == "__main__":
    import sys
    
    # Check if data path provided
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Train model
    model, vectorizer, accuracy = train_classification_model(data_path)
    
    # Test model
    test_model()
    
    logger.info("\n✅ Training complete!")
    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info("Models saved to ./models/")
