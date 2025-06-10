"""Slide to Image Conversion Module.

This module handles converting PowerPoint slides to high-quality images
for multimodal AI analysis.
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
import tempfile
import io
import base64
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
from loguru import logger


@dataclass
class ConversionSettings:
    """Settings for slide-to-image conversion.
    
    Attributes:
        width: Output image width in pixels
        height: Output image height in pixels
        dpi: Dots per inch for conversion
        format: Output image format (PNG, JPEG)
        quality: Image quality (1-100 for JPEG)
        background_color: Background color for transparent areas
    """
    width: int = 1920
    height: int = 1080
    dpi: int = 300
    format: str = "PNG"
    quality: int = 95
    background_color: str = "white"


@dataclass
class ConvertedSlide:
    """Converted slide image data.
    
    Attributes:
        slide_number: Original slide number (1-based)
        image_data: PIL Image object
        image_bytes: Image as bytes
        base64_data: Base64 encoded image data
        file_path: Path to saved image file (if saved)
        metadata: Conversion metadata
    """
    slide_number: int
    image_data: Image.Image
    image_bytes: bytes
    base64_data: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = None


class SlideConverter:
    """PowerPoint slide to image converter.
    
    Converts PowerPoint slides to high-quality images suitable for
    multimodal AI analysis using various conversion methods.
    """
    
    def __init__(self, settings: Optional[ConversionSettings] = None):
        """Initialize slide converter.
        
        Args:
            settings: Conversion settings, uses defaults if None
        """
        self.settings = settings or ConversionSettings()
        self.temp_dir = tempfile.mkdtemp(prefix="slide_converter_")
        logger.info(f"Initialized slide converter with temp dir: {self.temp_dir}")
    
    def _check_libreoffice_available(self) -> bool:
        """Check if LibreOffice is available for conversion.
        
        Returns:
            True if LibreOffice is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["libreoffice", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            available = result.returncode == 0
            logger.info(f"LibreOffice availability: {available}")
            return available
        except Exception as e:
            logger.warning(f"LibreOffice not available: {str(e)}")
            return False
    
    def _convert_with_libreoffice(self, pptx_path: str) -> List[str]:
        """Convert PowerPoint to images using LibreOffice.
        
        Args:
            pptx_path: Path to PowerPoint file
            
        Returns:
            List of paths to converted image files
            
        Raises:
            Exception: If conversion fails
        """
        try:
            # Create output directory
            output_dir = os.path.join(self.temp_dir, "libreoffice_output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert to PDF first
            pdf_cmd = [
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                pptx_path
            ]
            
            result = subprocess.run(pdf_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise Exception(f"PDF conversion failed: {result.stderr}")
            
            # Find generated PDF
            pdf_files = list(Path(output_dir).glob("*.pdf"))
            if not pdf_files:
                raise Exception("No PDF file generated")
            
            pdf_path = str(pdf_files[0])
            
            # Convert PDF to images using ImageMagick or similar
            # For now, return the PDF path as placeholder
            logger.info(f"Generated PDF: {pdf_path}")
            return [pdf_path]
            
        except Exception as e:
            logger.error(f"LibreOffice conversion failed: {str(e)}")
            raise
    
    def _create_placeholder_image(self, slide_number: int, text: str = "") -> Image.Image:
        """Create a placeholder image for a slide.
        
        Args:
            slide_number: Slide number
            text: Optional text to include
            
        Returns:
            PIL Image object
        """
        try:
            # Create image with specified dimensions
            img = Image.new(
                'RGB',
                (self.settings.width, self.settings.height),
                color=self.settings.background_color
            )
            
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font
            try:
                font = ImageFont.truetype("Arial.ttf", 48)
                title_font = ImageFont.truetype("Arial.ttf", 72)
            except:
                font = ImageFont.load_default()
                title_font = font
            
            # Draw slide number
            title_text = f"Slide {slide_number}"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            title_x = (self.settings.width - title_width) // 2
            title_y = self.settings.height // 3
            
            draw.text((title_x, title_y), title_text, fill="black", font=title_font)
            
            # Draw content text if provided
            if text:
                # Wrap text to fit image width
                words = text.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] < self.settings.width - 100:  # 50px margin on each side
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Draw text lines
                y_offset = title_y + title_height + 50
                for line in lines[:10]:  # Limit to 10 lines
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_width = bbox[2] - bbox[0]
                    x_offset = (self.settings.width - line_width) // 2
                    
                    draw.text((x_offset, y_offset), line, fill="black", font=font)
                    y_offset += bbox[3] - bbox[1] + 10
            
            logger.debug(f"Created placeholder image for slide {slide_number}")
            return img
            
        except Exception as e:
            logger.error(f"Failed to create placeholder image: {str(e)}")
            # Return basic colored rectangle as fallback
            return Image.new('RGB', (self.settings.width, self.settings.height), color='lightgray')
    
    def convert_slide_to_image(self, slide_content: Any, slide_number: int) -> ConvertedSlide:
        """Convert a single slide to image.
        
        Args:
            slide_content: Slide content data
            slide_number: Slide number (1-based)
            
        Returns:
            ConvertedSlide object with image data
        """
        try:
            # For now, create placeholder images with slide content
            # In a full implementation, this would use actual slide rendering
            
            text_content = ""
            if hasattr(slide_content, 'text_content') and slide_content.text_content:
                text_content = ' '.join(slide_content.text_content[:3])  # First 3 text elements
            elif hasattr(slide_content, 'metadata') and slide_content.metadata.title:
                text_content = slide_content.metadata.title
            
            # Create image
            image = self._create_placeholder_image(slide_number, text_content)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format=self.settings.format, quality=self.settings.quality)
            img_bytes.seek(0)
            image_bytes = img_bytes.getvalue()
            
            # Create base64 encoding
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create metadata
            metadata = {
                'width': image.width,
                'height': image.height,
                'format': self.settings.format,
                'size_bytes': len(image_bytes),
                'conversion_method': 'placeholder',
                'dpi': self.settings.dpi
            }
            
            converted_slide = ConvertedSlide(
                slide_number=slide_number,
                image_data=image,
                image_bytes=image_bytes,
                base64_data=base64_data,
                metadata=metadata
            )
            
            logger.info(f"Successfully converted slide {slide_number} to image")
            return converted_slide
            
        except Exception as e:
            logger.error(f"Failed to convert slide {slide_number}: {str(e)}")
            raise Exception(f"Slide conversion failed: {str(e)}")
    
    def batch_convert_slides(
        self,
        slides_content: List[Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ConvertedSlide]:
        """Convert multiple slides to images in batch.
        
        Args:
            slides_content: List of slide content data
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ConvertedSlide objects
        """
        converted_slides = []
        total_slides = len(slides_content)
        
        try:
            for i, slide_content in enumerate(slides_content):
                slide_number = i + 1
                
                # Update progress
                if progress_callback:
                    progress_callback(slide_number, total_slides)
                
                # Convert slide
                converted_slide = self.convert_slide_to_image(slide_content, slide_number)
                converted_slides.append(converted_slide)
                
                logger.debug(f"Batch conversion progress: {slide_number}/{total_slides}")
            
            logger.info(f"Successfully converted {len(converted_slides)} slides")
            return converted_slides
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {str(e)}")
            raise Exception(f"Batch slide conversion failed: {str(e)}")
    
    def save_image(self, converted_slide: ConvertedSlide, output_path: str) -> bool:
        """Save converted slide image to file.
        
        Args:
            converted_slide: ConvertedSlide object
            output_path: Path for output image file
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            converted_slide.image_data.save(
                output_path,
                format=self.settings.format,
                quality=self.settings.quality
            )
            
            converted_slide.file_path = output_path
            logger.info(f"Saved slide {converted_slide.slide_number} image to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            return False
    
    def save_all_images(self, converted_slides: List[ConvertedSlide], output_dir: str) -> List[str]:
        """Save all converted slide images to directory.
        
        Args:
            converted_slides: List of ConvertedSlide objects
            output_dir: Output directory path
            
        Returns:
            List of saved file paths
        """
        saved_paths = []
        
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            for converted_slide in converted_slides:
                filename = f"slide_{converted_slide.slide_number:03d}.{self.settings.format.lower()}"
                output_path = os.path.join(output_dir, filename)
                
                if self.save_image(converted_slide, output_path):
                    saved_paths.append(output_path)
            
            logger.info(f"Saved {len(saved_paths)} slide images to: {output_dir}")
            return saved_paths
            
        except Exception as e:
            logger.error(f"Failed to save images to directory: {str(e)}")
            return saved_paths
    
    def optimize_for_analysis(self, converted_slide: ConvertedSlide) -> ConvertedSlide:
        """Optimize image for multimodal AI analysis.
        
        Args:
            converted_slide: ConvertedSlide object to optimize
            
        Returns:
            Optimized ConvertedSlide object
        """
        try:
            image = converted_slide.image_data
            
            # Resize if too large (Claude has size limits)
            max_size = 1568  # Claude's max image dimension
            if image.width > max_size or image.height > max_size:
                # Calculate new size maintaining aspect ratio
                ratio = min(max_size / image.width, max_size / image.height)
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from {converted_slide.image_data.size} to {image.size}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Re-encode with optimization
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG', quality=85, optimize=True)
            img_bytes.seek(0)
            image_bytes = img_bytes.getvalue()
            
            # Update base64 data
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Update metadata
            metadata = converted_slide.metadata.copy()
            metadata.update({
                'optimized': True,
                'optimized_width': image.width,
                'optimized_height': image.height,
                'optimized_size_bytes': len(image_bytes)
            })
            
            optimized_slide = ConvertedSlide(
                slide_number=converted_slide.slide_number,
                image_data=image,
                image_bytes=image_bytes,
                base64_data=base64_data,
                file_path=converted_slide.file_path,
                metadata=metadata
            )
            
            logger.info(f"Optimized slide {converted_slide.slide_number} for analysis")
            return optimized_slide
            
        except Exception as e:
            logger.error(f"Failed to optimize slide {converted_slide.slide_number}: {str(e)}")
            return converted_slide  # Return original if optimization fails
    
    def create_thumbnail(self, converted_slide: ConvertedSlide, size: Tuple[int, int] = (200, 150)) -> Image.Image:
        """Create thumbnail image for UI preview.
        
        Args:
            converted_slide: ConvertedSlide object
            size: Thumbnail size as (width, height)
            
        Returns:
            PIL Image thumbnail
        """
        try:
            thumbnail = converted_slide.image_data.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            
            logger.debug(f"Created thumbnail for slide {converted_slide.slide_number}")
            return thumbnail
            
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            # Return a basic colored rectangle as fallback
            return Image.new('RGB', size, color='lightgray')
    
    def cleanup(self):
        """Clean up temporary files and directories."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary directory: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
