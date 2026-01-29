"""
Semantic analysis using AI/ML APIs.

This module provides semantic content analysis using external APIs
like Hugging Face and Google Cloud NLP.
"""

from typing import Dict, List, Optional
import httpx

from app.core.config import settings


class HuggingFaceClient:
    """
    Client for Hugging Face Inference API.
    
    Provides methods for semantic analysis, NER, and other NLP tasks
    without requiring local model downloads.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hugging Face client.
        
        Args:
            api_key: Optional API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.HUGGINGFACE_API_KEY
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    async def semantic_similarity(
        self,
        source_text: str,
        target_text: str,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Uses sentence transformers to compute cosine similarity.
        
        Args:
            source_text: First text (e.g., page content).
            target_text: Second text (e.g., target keyword).
            model: Hugging Face model to use.
        
        Returns:
            float: Similarity score (0-1).
        """
        if not self.api_key:
            return 0.0
        
        url = f"{self.base_url}/{model}"
        
        payload = {
            "inputs": {
                "source_sentence": source_text[:500],  # Limit length
                "sentences": [target_text[:500]],
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return results[0] if isinstance(results, list) else 0.5
                
                return 0.0
        except Exception:
            return 0.0
    
    async def extract_entities(
        self,
        text: str,
        model: str = "dbmdz/bert-large-cased-finetuned-conll03-english",
    ) -> List[Dict]:
        """
        Extract named entities from text.
        
        Identifies persons, locations, organizations, etc.
        
        Args:
            text: Text to analyze.
            model: NER model to use.
        
        Returns:
            list: List of entities with type and score.
        """
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/{model}"
        
        payload = {"inputs": text[:1000]}  # Limit text length
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                )
                
                if response.status_code == 200:
                    entities = response.json()
                    
                    # Group consecutive tokens of same entity
                    grouped = []
                    current_entity = None
                    
                    for entity in entities:
                        if not isinstance(entity, dict):
                            continue
                        
                        entity_type = entity.get("entity_group") or entity.get("entity")
                        word = entity.get("word", "")
                        score = entity.get("score", 0.0)
                        
                        if current_entity and current_entity["type"] == entity_type:
                            current_entity["text"] += " " + word.strip("#")
                            current_entity["score"] = max(current_entity["score"], score)
                        else:
                            if current_entity:
                                grouped.append(current_entity)
                            current_entity = {
                                "text": word.strip("#"),
                                "type": entity_type,
                                "score": score,
                            }
                    
                    if current_entity:
                        grouped.append(current_entity)
                    
                    return grouped
                
                return []
        except Exception:
            return []
    
    async def classify_text(
        self,
        text: str,
        model: str = "facebook/bart-large-mnli",
        candidate_labels: Optional[List[str]] = None,
    ) -> Dict:
        """
        Classify text into categories.
        
        Args:
            text: Text to classify.
            model: Classification model.
            candidate_labels: Possible categories.
        
        Returns:
            dict: Classification results with scores.
        """
        if not self.api_key:
            return {}
        
        if candidate_labels is None:
            candidate_labels = [
                "technology",
                "business",
                "health",
                "education",
                "entertainment",
                "sports",
            ]
        
        url = f"{self.base_url}/{model}"
        
        payload = {
            "inputs": text[:1000],
            "parameters": {"candidate_labels": candidate_labels},
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "labels": result.get("labels", []),
                        "scores": result.get("scores", []),
                        "top_category": result.get("labels", ["unknown"])[0],
                    }
                
                return {}
        except Exception:
            return {}


class GoogleNLPClient:
    """
    Client for Google Cloud Natural Language API.
    
    Provides sentiment analysis, entity analysis, and content classification.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google NLP client.
        
        Args:
            api_key: Optional API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.GOOGLE_CLOUD_API_KEY
        self.base_url = "https://language.googleapis.com/v1/documents"
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze.
        
        Returns:
            dict: Sentiment analysis results with score and magnitude.
        """
        if not self.api_key:
            return {"score": 0.0, "magnitude": 0.0, "sentiment": "neutral"}
        
        url = f"{self.base_url}:analyzeSentiment?key={self.api_key}"
        
        payload = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": text[:1000],
            },
            "encodingType": "UTF8",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    sentiment = result.get("documentSentiment", {})
                    score = sentiment.get("score", 0.0)
                    
                    # Classify sentiment
                    if score > 0.25:
                        sentiment_label = "positive"
                    elif score < -0.25:
                        sentiment_label = "negative"
                    else:
                        sentiment_label = "neutral"
                    
                    return {
                        "score": score,
                        "magnitude": sentiment.get("magnitude", 0.0),
                        "sentiment": sentiment_label,
                    }
                
                return {"score": 0.0, "magnitude": 0.0, "sentiment": "neutral"}
        except Exception:
            return {"score": 0.0, "magnitude": 0.0, "sentiment": "neutral"}
    
    async def extract_entities_google(self, text: str) -> List[Dict]:
        """
        Extract entities using Google Cloud NLP.
        
        Args:
            text: Text to analyze.
        
        Returns:
            list: List of entities with metadata.
        """
        if not self.api_key:
            return []
        
        url = f"{self.base_url}:analyzeEntities?key={self.api_key}"
        
        payload = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": text[:1000],
            },
            "encodingType": "UTF8",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    entities = result.get("entities", [])
                    
                    return [
                        {
                            "name": entity.get("name"),
                            "type": entity.get("type"),
                            "salience": entity.get("salience", 0.0),
                            "wikipedia_url": entity.get("metadata", {}).get("wikipedia_url"),
                        }
                        for entity in entities
                    ]
                
                return []
        except Exception:
            return []


# Global client instances
hf_client = HuggingFaceClient()
google_nlp_client = GoogleNLPClient()


async def analyze_content_semantics(
    content: str,
    target_keyword: Optional[str] = None,
) -> Dict:
    """
    Perform comprehensive semantic analysis on content.
    
    Combines multiple AI services to provide insights about content quality,
    relevance, and characteristics.
    
    Args:
        content: The text content to analyze.
        target_keyword: Optional target keyword for relevance scoring.
    
    Returns:
        dict: Complete semantic analysis results.
    """
    results = {
        "semantic_similarity": 0.0,
        "entities": [],
        "sentiment": {},
        "categories": {},
    }
    
    # Calculate semantic similarity if target keyword provided
    if target_keyword and settings.HUGGINGFACE_API_KEY:
        results["semantic_similarity"] = await hf_client.semantic_similarity(
            content,
            target_keyword,
        )
    
    # Extract named entities
    if settings.HUGGINGFACE_API_KEY:
        results["entities"] = await hf_client.extract_entities(content)
    
    # Analyze sentiment
    if settings.GOOGLE_CLOUD_API_KEY:
        results["sentiment"] = await google_nlp_client.analyze_sentiment(content)
    
    # Classify content
    if settings.HUGGINGFACE_API_KEY:
        results["categories"] = await hf_client.classify_text(content)
    
    return results
