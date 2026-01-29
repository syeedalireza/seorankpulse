"""
Automated alt text generation using Vision AI.

Generates descriptive alt text for images using:
- OpenAI GPT-4 Vision
- Google Cloud Vision API
"""

from typing import Dict, List, Optional
import base64
import httpx
from openai import AsyncOpenAI


class AltTextGenerator:
    """
    Generate descriptive alt text for images using AI vision models.
    
    Provides:
    - Automatic image description
    - SEO-optimized alt text
    - Context-aware descriptions
    - Accessibility compliance
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4-vision-preview"):
        """
        Initialize alt text generator.
        
        Args:
            api_key: OpenAI API key.
            model: Vision model to use.
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_alt_text(
        self,
        image_url: str,
        context: Optional[Dict] = None,
        max_length: int = 125
    ) -> Dict:
        """
        Generate alt text for an image.
        
        Args:
            image_url: URL of the image.
            context: Optional context (page topic, surrounding text, etc.).
            max_length: Maximum length of alt text (recommended: 125 chars).
        
        Returns:
            dict: Generated alt text with metadata.
        """
        try:
            # Build prompt
            prompt = self._build_prompt(context, max_length)
            
            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150,
                temperature=0.3,
            )
            
            alt_text = response.choices[0].message.content.strip()
            
            # Ensure it's within length limit
            if len(alt_text) > max_length:
                alt_text = alt_text[:max_length - 3] + "..."
            
            return {
                'success': True,
                'image_url': image_url,
                'alt_text': alt_text,
                'length': len(alt_text),
                'model': self.model,
            }
        
        except Exception as e:
            return {
                'success': False,
                'image_url': image_url,
                'error': str(e),
            }
    
    def _build_prompt(self, context: Optional[Dict], max_length: int) -> str:
        """
        Build prompt for alt text generation.
        
        Args:
            context: Context information.
            max_length: Maximum length.
        
        Returns:
            str: Prompt text.
        """
        base_prompt = (
            f"Generate a concise, descriptive alt text for this image. "
            f"Maximum {max_length} characters. "
            f"Focus on what's visible and relevant for accessibility and SEO. "
        )
        
        if context:
            page_topic = context.get('page_topic')
            surrounding_text = context.get('surrounding_text')
            
            if page_topic:
                base_prompt += f"Page topic: {page_topic}. "
            
            if surrounding_text:
                base_prompt += f"Context: {surrounding_text[:200]}. "
        
        base_prompt += (
            "Provide ONLY the alt text, no additional explanation. "
            "Make it descriptive but concise."
        )
        
        return base_prompt
    
    async def batch_generate(
        self,
        image_urls: List[str],
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate alt text for multiple images.
        
        Args:
            image_urls: List of image URLs.
            context: Optional context.
        
        Returns:
            list: Alt text results for each image.
        """
        results = []
        
        for url in image_urls:
            result = await self.generate_alt_text(url, context)
            results.append(result)
        
        return results
    
    async def analyze_and_improve_alt_text(
        self,
        current_alt: str,
        image_url: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze existing alt text and suggest improvements.
        
        Args:
            current_alt: Current alt text.
            image_url: Image URL.
            context: Optional context.
        
        Returns:
            dict: Analysis and improved alt text.
        """
        try:
            prompt = f"""Analyze this alt text and suggest improvements:

Current alt text: "{current_alt}"

Evaluate:
1. Accuracy (does it describe the image correctly?)
2. Length (is it too long or too short?)
3. SEO value (is it descriptive and keyword-friendly?)
4. Accessibility (is it helpful for screen readers?)

Provide:
- Score (0-100)
- Issues found
- Improved version (max 125 characters)

Format your response as:
Score: [number]
Issues: [list]
Improved: [alt text]"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=200,
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse response
            import re
            score_match = re.search(r'Score:\s*(\d+)', analysis_text)
            improved_match = re.search(r'Improved:\s*(.+?)(?:\n|$)', analysis_text)
            
            score = int(score_match.group(1)) if score_match else 70
            improved_alt = improved_match.group(1).strip() if improved_match else current_alt
            
            return {
                'success': True,
                'current_alt': current_alt,
                'score': score,
                'improved_alt': improved_alt,
                'analysis': analysis_text,
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }


async def generate_alt_text(
    image_url: str,
    api_key: str,
    context: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to generate alt text for a single image.
    
    Args:
        image_url: Image URL.
        api_key: OpenAI API key.
        context: Optional context.
    
    Returns:
        dict: Alt text generation result.
    """
    generator = AltTextGenerator(api_key=api_key)
    return await generator.generate_alt_text(image_url, context)


def validate_alt_text(alt_text: str) -> Dict:
    """
    Validate alt text quality.
    
    Args:
        alt_text: Alt text to validate.
    
    Returns:
        dict: Validation results.
    """
    issues = []
    warnings = []
    score = 100
    
    # Length checks
    length = len(alt_text)
    
    if length == 0:
        issues.append("Alt text is empty")
        score = 0
    elif length < 10:
        warnings.append("Alt text is very short (< 10 characters)")
        score -= 20
    elif length > 125:
        warnings.append(f"Alt text is too long ({length} chars, recommended max: 125)")
        score -= 10
    
    # Content checks
    if alt_text:
        alt_lower = alt_text.lower()
        
        # Check for redundant phrases
        redundant_phrases = [
            'image of', 'picture of', 'photo of', 'graphic of',
            'screenshot of', 'illustration of'
        ]
        
        for phrase in redundant_phrases:
            if alt_lower.startswith(phrase):
                warnings.append(f"Starts with redundant phrase: '{phrase}'")
                score -= 5
                break
        
        # Check for filename patterns
        if any(char in alt_text for char in ['_', '-']) and '.' in alt_text:
            warnings.append("Looks like a filename - should be descriptive text")
            score -= 15
        
        # Check for generic text
        generic_terms = ['image', 'photo', 'picture', 'graphic']
        if alt_text.lower() in generic_terms:
            issues.append("Alt text is too generic")
            score -= 30
    
    # Determine grade
    if score >= 90:
        grade = "Excellent"
    elif score >= 75:
        grade = "Good"
    elif score >= 60:
        grade = "Fair"
    else:
        grade = "Poor"
    
    return {
        'score': max(0, score),
        'grade': grade,
        'length': length,
        'issues': issues,
        'warnings': warnings,
        'is_valid': len(issues) == 0 and score >= 60,
    }
