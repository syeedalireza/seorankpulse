"""
Elasticsearch client for content indexing and search.

This module provides a client for indexing page content in Elasticsearch
and performing full-text searches.
"""

from typing import Dict, List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from app.core.config import settings


class ElasticsearchClient:
    """
    Async Elasticsearch client for content operations.
    
    Handles indexing page content and performing searches.
    """
    
    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client: Optional[AsyncElasticsearch] = None
        self.index_name = "seo_pages"
    
    async def connect(self) -> None:
        """Establish connection to Elasticsearch."""
        if self.client is None:
            self.client = AsyncElasticsearch(
                [f"http://{settings.ELASTICSEARCH_HOST}"],
                verify_certs=False,
            )
    
    async def close(self) -> None:
        """Close Elasticsearch connection."""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def create_index(self) -> None:
        """Create index with proper mappings if it doesn't exist."""
        if not self.client:
            await self.connect()
        
        index_body = {
            "mappings": {
                "properties": {
                    "url": {"type": "keyword"},
                    "url_hash": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "english"},
                    "content": {"type": "text", "analyzer": "english"},
                    "meta_description": {"type": "text"},
                    "h1": {"type": "text"},
                    "crawl_job_id": {"type": "integer"},
                    "timestamp": {"type": "date"},
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            }
        }
        
        try:
            await self.client.indices.create(
                index=self.index_name,
                body=index_body,
            )
        except Exception:
            # Index might already exist
            pass
    
    async def index_page(
        self,
        url_hash: str,
        url: str,
        title: str,
        content: str,
        meta_description: Optional[str] = None,
        h1: Optional[str] = None,
        crawl_job_id: Optional[int] = None,
    ) -> bool:
        """
        Index a page in Elasticsearch.
        
        Args:
            url_hash: Unique hash of URL.
            url: Page URL.
            title: Page title.
            content: Page text content.
            meta_description: Meta description.
            h1: H1 heading.
            crawl_job_id: Associated crawl job ID.
        
        Returns:
            bool: True if successful.
        """
        if not self.client:
            await self.connect()
        
        doc = {
            "url": url,
            "url_hash": url_hash,
            "title": title,
            "content": content[:50000],  # Limit content size
            "meta_description": meta_description,
            "h1": h1,
            "crawl_job_id": crawl_job_id,
            "timestamp": "now",
        }
        
        try:
            await self.client.index(
                index=self.index_name,
                id=url_hash,
                document=doc,
            )
            return True
        except Exception:
            return False
    
    async def search(
        self,
        query: str,
        size: int = 10,
        crawl_job_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Search indexed pages.
        
        Args:
            query: Search query.
            size: Number of results.
            crawl_job_id: Optional filter by crawl job.
        
        Returns:
            list: Search results.
        """
        if not self.client:
            await self.connect()
        
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content", "meta_description^2"],
                            }
                        }
                    ]
                }
            },
            "size": size,
        }
        
        # Add crawl job filter if provided
        if crawl_job_id:
            search_body["query"]["bool"]["filter"] = [
                {"term": {"crawl_job_id": crawl_job_id}}
            ]
        
        try:
            response = await self.client.search(
                index=self.index_name,
                body=search_body,
            )
            
            hits = response.get("hits", {}).get("hits", [])
            return [
                {
                    "url": hit["_source"]["url"],
                    "title": hit["_source"]["title"],
                    "score": hit["_score"],
                }
                for hit in hits
            ]
        except NotFoundError:
            return []
        except Exception:
            return []


# Global client instance
es_client = ElasticsearchClient()
