"""PowerPoint Processing Package.

This package provides comprehensive PowerPoint file processing capabilities
including slide extraction, content analysis, and image conversion.
"""

from .pptx_processor import PowerPointProcessor, PresentationData, SlideContent, SlideMetadata
from .slide_converter import SlideConverter, ConvertedSlide, ConversionSettings
from .content_extractor import ContentExtractor, TextElement, ImageElement, ChartElement, TableElement, AWSService

__all__ = [
    "PowerPointProcessor",
    "PresentationData", 
    "SlideContent",
    "SlideMetadata",
    "SlideConverter",
    "ConvertedSlide",
    "ConversionSettings",
    "ContentExtractor",
    "TextElement",
    "ImageElement", 
    "ChartElement",
    "TableElement",
    "AWSService",
]
