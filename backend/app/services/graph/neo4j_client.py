"""
Neo4j client for graph database operations.

This module provides a client for interacting with Neo4j graph database
to store and analyze website link structures.
"""

from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable

from app.core.config import settings


class Neo4jClient:
    """
    Async Neo4j client for link graph operations.
    
    Manages connections to Neo4j and provides methods for:
    - Creating page nodes
    - Creating link relationships
    - Running PageRank algorithm
    - Querying graph structure
    """
    
    def __init__(self):
        """Initialize Neo4j client."""
        self.driver: Optional[AsyncDriver] = None
        self._uri = settings.NEO4J_URI
        self._user = settings.NEO4J_USER
        self._password = settings.NEO4J_PASSWORD
    
    async def connect(self) -> None:
        """
        Establish connection to Neo4j database.
        
        Raises:
            ServiceUnavailable: If cannot connect to Neo4j.
        """
        if self.driver is None:
            self.driver = AsyncGraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
            )
    
    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None
    
    @asynccontextmanager
    async def session(self):
        """
        Context manager for Neo4j session.
        
        Usage:
            async with client.session() as session:
                result = await session.run(query)
        """
        if not self.driver:
            await self.connect()
        
        async with self.driver.session() as session:
            yield session
    
    async def create_indexes(self) -> None:
        """Create indexes for better query performance."""
        async with self.session() as session:
            # Index on URL for fast lookups
            await session.run(
                "CREATE INDEX page_url_index IF NOT EXISTS FOR (p:Page) ON (p.url)"
            )
            
            # Index on URL hash
            await session.run(
                "CREATE INDEX page_hash_index IF NOT EXISTS FOR (p:Page) ON (p.url_hash)"
            )
    
    async def create_page_node(
        self,
        url: str,
        url_hash: str,
        title: Optional[str] = None,
        status_code: int = 200,
        depth: int = 0,
        **properties
    ) -> Dict:
        """
        Create or update a page node in the graph.
        
        Args:
            url: Page URL.
            url_hash: Hash of URL for uniqueness.
            title: Page title.
            status_code: HTTP status code.
            depth: Crawl depth.
            **properties: Additional properties.
        
        Returns:
            dict: Created/updated node properties.
        """
        async with self.session() as session:
            query = """
            MERGE (p:Page {url_hash: $url_hash})
            ON CREATE SET 
                p.url = $url,
                p.title = $title,
                p.status_code = $status_code,
                p.depth = $depth,
                p.created_at = datetime()
            ON MATCH SET
                p.title = $title,
                p.status_code = $status_code,
                p.depth = $depth,
                p.updated_at = datetime()
            RETURN p
            """
            
            result = await session.run(
                query,
                url_hash=url_hash,
                url=url,
                title=title,
                status_code=status_code,
                depth=depth,
                **properties
            )
            
            record = await result.single()
            return dict(record["p"]) if record else {}
    
    async def create_link_relationship(
        self,
        from_url_hash: str,
        to_url_hash: str,
        link_type: str = "LINKS_TO",
    ) -> bool:
        """
        Create a link relationship between two pages.
        
        Args:
            from_url_hash: Source page URL hash.
            to_url_hash: Target page URL hash.
            link_type: Type of relationship (default: LINKS_TO).
        
        Returns:
            bool: True if relationship created.
        """
        async with self.session() as session:
            query = f"""
            MATCH (from:Page {{url_hash: $from_hash}})
            MATCH (to:Page {{url_hash: $to_hash}})
            MERGE (from)-[r:{link_type}]->(to)
            ON CREATE SET r.created_at = datetime()
            RETURN r
            """
            
            result = await session.run(
                query,
                from_hash=from_url_hash,
                to_hash=to_url_hash,
            )
            
            record = await result.single()
            return record is not None
    
    async def calculate_pagerank(
        self,
        project_id: Optional[int] = None,
        iterations: int = 20,
        damping_factor: float = 0.85,
    ) -> Dict[str, float]:
        """
        Calculate PageRank for all pages in the graph.
        
        Uses Neo4j Graph Data Science library if available,
        otherwise uses a custom implementation.
        
        Args:
            project_id: Optional project ID to filter pages.
            iterations: Number of PageRank iterations.
            damping_factor: Damping factor (usually 0.85).
        
        Returns:
            dict: URL hash to PageRank score mapping.
        """
        async with self.session() as session:
            # Try using GDS library first
            try:
                query = """
                CALL gds.pageRank.stream({
                    nodeProjection: 'Page',
                    relationshipProjection: 'LINKS_TO',
                    maxIterations: $iterations,
                    dampingFactor: $damping
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).url_hash AS url_hash, score
                ORDER BY score DESC
                """
                
                result = await session.run(
                    query,
                    iterations=iterations,
                    damping=damping_factor,
                )
                
                pageranks = {}
                async for record in result:
                    pageranks[record["url_hash"]] = record["score"]
                
                return pageranks
                
            except Exception:
                # Fallback to custom implementation
                return await self._calculate_pagerank_custom(iterations, damping_factor)
    
    async def _calculate_pagerank_custom(
        self,
        iterations: int = 20,
        damping: float = 0.85,
    ) -> Dict[str, float]:
        """
        Custom PageRank implementation without GDS library.
        
        Args:
            iterations: Number of iterations.
            damping: Damping factor.
        
        Returns:
            dict: PageRank scores.
        """
        async with self.session() as session:
            # Get all pages and their links
            query = """
            MATCH (p:Page)
            OPTIONAL MATCH (p)-[:LINKS_TO]->(target:Page)
            WITH p, count(target) as outbound_count, collect(target.url_hash) as targets
            RETURN p.url_hash as url_hash, outbound_count, targets
            """
            
            result = await session.run(query)
            
            # Build graph structure
            pages = {}
            async for record in result:
                url_hash = record["url_hash"]
                pages[url_hash] = {
                    "outbound": record["targets"],
                    "outbound_count": record["outbound_count"],
                    "pagerank": 1.0,
                }
            
            # PageRank iterations
            num_pages = len(pages)
            if num_pages == 0:
                return {}
            
            for _ in range(iterations):
                new_ranks = {}
                
                for url_hash in pages:
                    rank = (1 - damping) / num_pages
                    
                    # Sum contributions from inbound links
                    for other_hash, other_data in pages.items():
                        if url_hash in other_data["outbound"]:
                            if other_data["outbound_count"] > 0:
                                rank += damping * (
                                    other_data["pagerank"] / other_data["outbound_count"]
                                )
                    
                    new_ranks[url_hash] = rank
                
                # Update ranks
                for url_hash in pages:
                    pages[url_hash]["pagerank"] = new_ranks[url_hash]
            
            # Return just the scores
            return {url_hash: data["pagerank"] for url_hash, data in pages.items()}
    
    async def get_page_stats(self, url_hash: str) -> Dict:
        """
        Get statistics for a specific page.
        
        Args:
            url_hash: Page URL hash.
        
        Returns:
            dict: Page statistics including inbound/outbound links.
        """
        async with self.session() as session:
            query = """
            MATCH (p:Page {url_hash: $url_hash})
            OPTIONAL MATCH (p)-[:LINKS_TO]->(outbound:Page)
            OPTIONAL MATCH (inbound:Page)-[:LINKS_TO]->(p)
            WITH p, count(DISTINCT outbound) as out_count, count(DISTINCT inbound) as in_count
            RETURN p.url as url, p.title as title, out_count, in_count
            """
            
            result = await session.run(query, url_hash=url_hash)
            record = await result.single()
            
            if record:
                return {
                    "url": record["url"],
                    "title": record["title"],
                    "outbound_links": record["out_count"],
                    "inbound_links": record["in_count"],
                }
            return {}
    
    async def find_orphan_pages(self) -> List[Dict]:
        """
        Find pages with no inbound links (orphan pages).
        
        Returns:
            list: List of orphan pages.
        """
        async with self.session() as session:
            query = """
            MATCH (p:Page)
            WHERE NOT (:Page)-[:LINKS_TO]->(p)
            RETURN p.url_hash as url_hash, p.url as url, p.title as title
            ORDER BY p.url
            """
            
            result = await session.run(query)
            
            orphans = []
            async for record in result:
                orphans.append({
                    "url_hash": record["url_hash"],
                    "url": record["url"],
                    "title": record["title"],
                })
            
            return orphans
    
    async def get_link_depth_distribution(self) -> Dict[int, int]:
        """
        Get distribution of pages by depth.
        
        Returns:
            dict: Depth to page count mapping.
        """
        async with self.session() as session:
            query = """
            MATCH (p:Page)
            RETURN p.depth as depth, count(p) as count
            ORDER BY depth
            """
            
            result = await session.run(query)
            
            distribution = {}
            async for record in result:
                distribution[record["depth"]] = record["count"]
            
            return distribution
    
    async def clear_all_data(self) -> None:
        """Delete all nodes and relationships. Use with caution!"""
        async with self.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")


# Global client instance
neo4j_client = Neo4jClient()
