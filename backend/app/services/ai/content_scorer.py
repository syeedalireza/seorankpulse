"""
AI-powered content quality scoring using GPT-4/Claude.

Evaluates content for:
- Readability and clarity
- SEO optimization
- User engagement
- E-A-T (Expertise, Authoritativeness, Trustworthiness)
- Content completeness
"""

from typing import Dict, List, Optional
import openai
from openai import AsyncOpenAI


class ContentQualityScorer:
    """
    Score content quality using AI (GPT-4/Claude).
    
    Provides:
    - Overall quality score
    - Detailed analysis
    - Improvement suggestions
    - Competitor comparison
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize content quality scorer.
        
        Args:
            api_key: OpenAI API key.
            model: Model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo).
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def score_content(
        self,
        content: str,
        url: str,
        target_keyword: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Score content quality using AI.
        
        Args:
            content: Page content to analyze.
            url: Page URL for context.
            target_keyword: Optional target keyword.
            context: Additional context (industry, audience, etc.).
        
        Returns:
            dict: Content quality analysis.
        """
        # Build prompt
        prompt = self._build_scoring_prompt(content, url, target_keyword, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SEO content analyst with deep knowledge of "
                                   "content quality, readability, E-A-T principles, and search engine "
                                   "optimization. Provide detailed, actionable analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse AI response (structured format)
            return self._parse_ai_response(analysis_text)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def _build_scoring_prompt(
        self,
        content: str,
        url: str,
        target_keyword: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """
        Build prompt for AI content scoring.
        
        Args:
            content: Content to analyze.
            url: Page URL.
            target_keyword: Target keyword.
            context: Additional context.
        
        Returns:
            str: Formatted prompt.
        """
        # Truncate content if too long
        max_content_length = 3000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... [truncated]"
        
        prompt = f"""Analyze the following web page content for SEO and quality:

URL: {url}
{f"Target Keyword: {target_keyword}" if target_keyword else ""}
{f"Industry: {context.get('industry')}" if context and context.get('industry') else ""}

CONTENT:
{content}

Please provide a comprehensive analysis in the following structured format:

1. OVERALL SCORE (0-100):
   - Provide a numerical score

2. READABILITY ANALYSIS:
   - Grade level and clarity
   - Sentence structure
   - Use of jargon

3. SEO OPTIMIZATION:
   - Keyword usage and density
   - Content structure (headings, paragraphs)
   - Internal linking opportunities
   - Meta information assessment

4. E-A-T ASSESSMENT (Expertise, Authoritativeness, Trustworthiness):
   - Evidence of expertise
   - Credibility signals
   - Trust factors

5. ENGAGEMENT POTENTIAL:
   - Hook and introduction quality
   - Content depth and value
   - Call-to-action effectiveness

6. CONTENT COMPLETENESS:
   - Topic coverage
   - Missing elements
   - Information gaps

7. TOP 3 STRENGTHS:
   - List specific strengths

8. TOP 5 IMPROVEMENTS:
   - Prioritized, actionable recommendations

9. CONTENT TYPE CLASSIFICATION:
   - Identify content type (informational, commercial, transactional, etc.)

Provide the analysis in a clear, structured format."""

        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Parse AI response into structured format.
        
        Args:
            response_text: Raw AI response.
        
        Returns:
            dict: Structured analysis.
        """
        # This is a simplified parser
        # In production, you'd use more robust parsing or structured output
        
        lines = response_text.split('\n')
        
        # Extract overall score (basic regex)
        import re
        score_match = re.search(r'(\d+)\s*(?:/100|out of 100)?', response_text[:500])
        overall_score = int(score_match.group(1)) if score_match else 70
        
        return {
            'success': True,
            'overall_score': min(100, max(0, overall_score)),
            'analysis': response_text,
            'recommendations': self._extract_recommendations(response_text),
            'strengths': self._extract_strengths(response_text),
        }
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from AI response."""
        recommendations = []
        
        # Look for numbered lists or bullet points
        import re
        patterns = [
            r'(?:TOP \d+ IMPROVEMENTS|IMPROVEMENTS|RECOMMENDATIONS):\s*\n((?:[-•*]\s*.+\n?)+)',
            r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                for match in matches[:5]:  # Limit to top 5
                    recommendations.append(match.strip())
                break
        
        return recommendations or ["Review AI analysis for detailed recommendations"]
    
    def _extract_strengths(self, text: str) -> List[str]:
        """Extract strengths from AI response."""
        strengths = []
        
        import re
        pattern = r'(?:TOP \d+ STRENGTHS|STRENGTHS):\s*\n((?:[-•*]\s*.+\n?)+)'
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        
        if match:
            items = re.findall(r'[-•*]\s*(.+)', match.group(1))
            strengths = [item.strip() for item in items[:3]]
        
        return strengths or ["Content has good structure"]
    
    async def compare_with_competitors(
        self,
        your_content: str,
        competitor_contents: List[Dict]
    ) -> Dict:
        """
        Compare your content with competitors using AI.
        
        Args:
            your_content: Your page content.
            competitor_contents: List of competitor content dicts with 'url' and 'content'.
        
        Returns:
            dict: Competitive analysis.
        """
        prompt = f"""Compare the following content with competitor content and identify gaps:

YOUR CONTENT:
{your_content[:2000]}

COMPETITOR CONTENT:
"""
        
        for i, comp in enumerate(competitor_contents[:3], 1):  # Limit to 3 competitors
            prompt += f"\nCompetitor {i} ({comp.get('url', 'N/A')}):\n{comp.get('content', '')[:1500]}\n"
        
        prompt += """
Provide analysis:
1. Content gaps (topics/information they cover that you don't)
2. Your unique advantages
3. Opportunities to improve and outrank competitors
4. Recommended content additions
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an SEO competitor analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            
            return {
                'success': True,
                'analysis': response.choices[0].message.content,
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    async def generate_content_brief(
        self,
        topic: str,
        target_keyword: str,
        competitors: List[str]
    ) -> Dict:
        """
        Generate a content brief based on topic and competitors.
        
        Args:
            topic: Content topic.
            target_keyword: Target keyword.
            competitors: List of competitor URLs.
        
        Returns:
            dict: Content brief with outline and recommendations.
        """
        prompt = f"""Create a comprehensive content brief for:

Topic: {topic}
Target Keyword: {target_keyword}
Competitors: {', '.join(competitors[:5])}

Provide:
1. Recommended word count
2. Content outline with H2 and H3 headings
3. Key points to cover
4. Questions to answer
5. Recommended media (images, videos, etc.)
6. Internal linking suggestions
7. Call-to-action recommendations

Format as an actionable brief for a content writer."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an SEO content strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
            )
            
            return {
                'success': True,
                'brief': response.choices[0].message.content,
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }


async def score_content_quality(
    content: str,
    url: str,
    api_key: str,
    target_keyword: Optional[str] = None
) -> Dict:
    """
    Convenience function to score content quality.
    
    Args:
        content: Page content.
        url: Page URL.
        api_key: OpenAI API key.
        target_keyword: Optional target keyword.
    
    Returns:
        dict: Quality analysis.
    """
    scorer = ContentQualityScorer(api_key=api_key)
    return await scorer.score_content(content, url, target_keyword)
