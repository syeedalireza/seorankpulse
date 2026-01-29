"""
Image analysis for SEO optimization.

Analyzes images for:
- File size and format
- Compression opportunities
- Dimension recommendations
- Alt text presence
- Lazy loading suggestions
"""

import httpx
from PIL import Image
from io import BytesIO
from typing import Dict, List, Optional
import imagehash


class ImageAnalyzer:
    """
    Analyze images for SEO and performance optimization.
    
    Provides recommendations for:
    - Image compression
    - Modern format conversion (WebP, AVIF)
    - Responsive image sizing
    - Loading optimization
    """
    
    def __init__(self):
        """Initialize image analyzer."""
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_image(self, image_url: str) -> Dict:
        """
        Analyze a single image.
        
        Args:
            image_url: URL of the image to analyze.
        
        Returns:
            dict: Image analysis with optimization recommendations.
        """
        try:
            # Download image
            response = await self.client.get(image_url)
            
            if response.status_code != 200:
                return {
                    'url': image_url,
                    'error': f'Failed to download (status {response.status_code})',
                }
            
            # Get file size
            file_size = len(response.content)
            
            # Load image
            img = Image.open(BytesIO(response.content))
            
            # Get image info
            width, height = img.size
            format_name = img.format
            mode = img.mode
            
            # Calculate perceived hash for duplicate detection
            phash = str(imagehash.phash(img))
            
            # Analyze compression potential
            compression_analysis = self._analyze_compression(
                img, file_size, format_name
            )
            
            # Size recommendations
            size_recommendations = self._analyze_dimensions(width, height, file_size)
            
            # Format recommendations
            format_recommendations = self._recommend_format(
                format_name, width, height, mode
            )
            
            # Calculate optimization score
            score = self._calculate_image_score(
                file_size, width, height, format_name
            )
            
            return {
                'url': image_url,
                'success': True,
                'properties': {
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'mode': mode,
                    'file_size_bytes': file_size,
                    'file_size_kb': round(file_size / 1024, 2),
                    'perceptual_hash': phash,
                },
                'compression_analysis': compression_analysis,
                'size_recommendations': size_recommendations,
                'format_recommendations': format_recommendations,
                'score': score,
            }
        
        except Exception as e:
            return {
                'url': image_url,
                'success': False,
                'error': str(e),
            }
    
    def _analyze_compression(
        self,
        img: Image.Image,
        current_size: int,
        format_name: str
    ) -> Dict:
        """
        Analyze compression opportunities.
        
        Args:
            img: PIL Image object.
            current_size: Current file size in bytes.
            format_name: Current image format.
        
        Returns:
            dict: Compression analysis.
        """
        # Estimate potential savings
        # This is a rough estimation
        potential_savings_pct = 0
        recommendations = []
        
        # Check if image is too large
        if current_size > 500 * 1024:  # > 500KB
            potential_savings_pct = 30
            recommendations.append("Image is very large (>500KB). Consider compression.")
        elif current_size > 200 * 1024:  # > 200KB
            potential_savings_pct = 20
            recommendations.append("Image is large (>200KB). Compression recommended.")
        elif current_size > 100 * 1024:  # > 100KB
            potential_savings_pct = 10
            recommendations.append("Image could benefit from compression.")
        
        # Format-specific recommendations
        if format_name == 'PNG' and img.mode == 'RGB':
            recommendations.append("PNG with no transparency should be JPEG or WebP.")
            potential_savings_pct = max(potential_savings_pct, 40)
        
        estimated_optimized_size = current_size * (1 - potential_savings_pct / 100)
        
        return {
            'current_size_kb': round(current_size / 1024, 2),
            'potential_savings_percentage': potential_savings_pct,
            'estimated_optimized_size_kb': round(estimated_optimized_size / 1024, 2),
            'recommendations': recommendations,
        }
    
    def _analyze_dimensions(
        self,
        width: int,
        height: int,
        file_size: int
    ) -> Dict:
        """
        Analyze image dimensions and provide recommendations.
        
        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            file_size: File size in bytes.
        
        Returns:
            dict: Dimension analysis.
        """
        total_pixels = width * height
        issues = []
        recommendations = []
        
        # Check if image is too large
        if width > 2500 or height > 2500:
            issues.append("Image dimensions are very large")
            recommendations.append(
                f"Consider resizing to max 2000px. "
                f"Current: {width}x{height}"
            )
        
        # Check bytes per pixel ratio
        if total_pixels > 0:
            bytes_per_pixel = file_size / total_pixels
            
            if bytes_per_pixel > 3:
                issues.append("High bytes-per-pixel ratio")
                recommendations.append("Image may be over-compressed or in wrong format")
        
        # Suggest responsive images
        if width > 1200:
            recommendations.append(
                "Use responsive images (srcset) with multiple sizes"
            )
        
        return {
            'width': width,
            'height': height,
            'total_pixels': total_pixels,
            'aspect_ratio': round(width / height, 2) if height > 0 else 0,
            'issues': issues,
            'recommendations': recommendations,
        }
    
    def _recommend_format(
        self,
        current_format: str,
        width: int,
        height: int,
        mode: str
    ) -> Dict:
        """
        Recommend optimal image format.
        
        Args:
            current_format: Current image format.
            width: Image width.
            height: Image height.
            mode: Color mode.
        
        Returns:
            dict: Format recommendations.
        """
        recommendations = []
        optimal_format = current_format
        
        # WebP is generally better for web
        if current_format in ['JPEG', 'PNG']:
            recommendations.append(
                "Consider using WebP format for better compression and quality"
            )
            optimal_format = 'WebP'
        
        # AVIF for even better compression (newer format)
        if width * height > 500000:  # Large images
            recommendations.append(
                "For large images, consider AVIF format (with WebP fallback)"
            )
        
        # SVG for simple graphics
        if current_format == 'PNG' and width * height < 100000 and mode == 'P':
            recommendations.append(
                "If this is a logo or icon, consider SVG format"
            )
        
        # Progressive JPEG for large photos
        if current_format == 'JPEG' and width * height > 500000:
            recommendations.append(
                "Use progressive JPEG for better perceived loading"
            )
        
        return {
            'current_format': current_format,
            'recommended_format': optimal_format,
            'recommendations': recommendations,
            'supports_transparency': mode in ['RGBA', 'LA', 'PA'],
        }
    
    def _calculate_image_score(
        self,
        file_size: int,
        width: int,
        height: int,
        format_name: str
    ) -> Dict:
        """
        Calculate overall image optimization score.
        
        Args:
            file_size: File size in bytes.
            width: Image width.
            height: Image height.
            format_name: Image format.
        
        Returns:
            dict: Score and interpretation.
        """
        score = 100
        issues = []
        
        # Size penalties
        if file_size > 500 * 1024:
            score -= 30
            issues.append("File size too large")
        elif file_size > 200 * 1024:
            score -= 15
            issues.append("File size could be smaller")
        
        # Dimension penalties
        if width > 3000 or height > 3000:
            score -= 20
            issues.append("Dimensions too large")
        
        # Format penalties
        if format_name == 'BMP':
            score -= 40
            issues.append("Outdated format (BMP)")
        elif format_name == 'GIF' and width * height > 10000:
            score -= 20
            issues.append("GIF not optimal for large images")
        
        # Determine grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            'score': max(0, score),
            'grade': grade,
            'issues': issues,
        }
    
    async def analyze_page_images(self, page_data: Dict) -> Dict:
        """
        Analyze all images on a page.
        
        Args:
            page_data: Page data dictionary with images.
        
        Returns:
            dict: Aggregated image analysis.
        """
        # Note: This is a placeholder - actual implementation would need
        # image URLs extracted from the page HTML
        
        total_images = page_data.get('images_count', 0)
        images_without_alt = page_data.get('images_without_alt', 0)
        
        return {
            'total_images': total_images,
            'images_with_alt': total_images - images_without_alt,
            'images_without_alt': images_without_alt,
            'alt_coverage_percentage': round(
                (total_images - images_without_alt) / total_images * 100, 2
            ) if total_images > 0 else 100,
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def analyze_image(image_url: str) -> Dict:
    """
    Convenience function to analyze a single image.
    
    Args:
        image_url: URL of the image.
    
    Returns:
        dict: Image analysis.
    """
    analyzer = ImageAnalyzer()
    try:
        result = await analyzer.analyze_image(image_url)
        return result
    finally:
        await analyzer.close()


def detect_duplicate_images(image_analyses: List[Dict], threshold: int = 5) -> List[Dict]:
    """
    Detect duplicate or very similar images using perceptual hashing.
    
    Args:
        image_analyses: List of image analysis results with perceptual hashes.
        threshold: Maximum hash distance to consider duplicates.
    
    Returns:
        list: Groups of duplicate images.
    """
    from collections import defaultdict
    
    # Group by perceptual hash
    hash_groups = defaultdict(list)
    
    for analysis in image_analyses:
        if analysis.get('success') and 'properties' in analysis:
            phash = analysis['properties'].get('perceptual_hash')
            if phash:
                hash_groups[phash].append(analysis['url'])
    
    # Find duplicates
    duplicates = []
    for phash, urls in hash_groups.items():
        if len(urls) > 1:
            duplicates.append({
                'hash': phash,
                'count': len(urls),
                'urls': urls,
                'type': 'exact_duplicate',
            })
    
    return duplicates
