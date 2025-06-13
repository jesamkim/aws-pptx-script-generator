"""Prompt Cache Manager for Claude 3.7 Sonnet.

This module implements caching strategies for Claude 3.7 Sonnet prompts
to optimize performance and reduce costs.
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class CacheConfig:
    """Configuration for prompt caching.
    
    Attributes:
        type: Cache type ('ephemeral' or 'persistent')
        namespace: Custom namespace for cache segmentation
        version: Cache version for schema changes
        ttl: Time-to-live in seconds (for ephemeral cache)
    """
    type: str = "ephemeral"
    namespace: Optional[str] = None
    version: str = "1.0.0"
    ttl: int = 300  # 5 minutes


class PromptCacheManager:
    """Manages prompt caching for Claude 3.7 Sonnet."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache manager.
        
        Args:
            config: Optional cache configuration
        """
        self.config = config or CacheConfig()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0
        }
        
        # In-memory cache for testing
        self._cache_store = {}
        self._cache_timestamps = {}
        
        logger.info(f"Initialized prompt cache manager with type: {self.config.type}")
    
    def get_cache_key(self, content: str, slide_number: Optional[int] = None) -> str:
        """Generate cache key for content.
        
        Args:
            content: Content to generate key for
            slide_number: Optional slide number for slide-specific caching
            
        Returns:
            Cache key string
        """
        # Generate deterministic cache key
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        namespace = self.config.namespace or "default"
        
        # Include slide number in cache key if provided
        if slide_number is not None:
            return f"{namespace}:{self.config.version}:slide{slide_number}:{content_hash}"
        
        return f"{namespace}:{self.config.version}:{content_hash}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self._cache_timestamps:
            return False
        
        timestamp = self._cache_timestamps[cache_key]
        return (time.time() - timestamp) < self.config.ttl
    
    def get_cached_response(self, static_content: str, dynamic_content: str, slide_number: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get cached response if available.
        
        Args:
            static_content: Static content
            dynamic_content: Dynamic content
            slide_number: Optional slide number for slide-specific caching
            
        Returns:
            Cached response or None if not found
        """
        # Create cache key from combined content and slide number
        combined_content = f"{static_content}\n{dynamic_content}"
        cache_key = self.get_cache_key(combined_content, slide_number)
        
        if cache_key in self._cache_store and self._is_cache_valid(cache_key):
            self.cache_stats['hits'] += 1
            logger.debug(f"Cache hit for key: {cache_key}")
            return self._cache_store[cache_key]
        
        self.cache_stats['misses'] += 1
        logger.debug(f"Cache miss for key: {cache_key}")
        return None
    
    def store_response(self, static_content: str, dynamic_content: str, response: Dict[str, Any], slide_number: Optional[int] = None):
        """Store response in cache.
        
        Args:
            static_content: Static content
            dynamic_content: Dynamic content
            response: Response to cache
            slide_number: Optional slide number for slide-specific caching
        """
        # Create cache key from combined content and slide number
        combined_content = f"{static_content}\n{dynamic_content}"
        cache_key = self.get_cache_key(combined_content, slide_number)
        
        # Store response and timestamp
        self._cache_store[cache_key] = response.copy()
        self._cache_timestamps[cache_key] = time.time()
        
        self.cache_stats['writes'] += 1
        logger.debug(f"Cached response for key: {cache_key}")
    
    def create_cache_control(self, 
                           static_content: str,
                           breakpoints: Optional[list[int]] = None) -> Dict[str, Any]:
        """Create cache control configuration.
        
        Args:
            static_content: Static content to cache
            breakpoints: Optional list of token breakpoints
            
        Returns:
            Cache control configuration
        """
        cache_key = self.get_cache_key(static_content)
        
        cache_control = {
            "type": self.config.type,
            "namespace": self.config.namespace or cache_key,
            "version": self.config.version
        }
        
        # Add breakpoints if specified
        if breakpoints:
            cache_control["breakpoints"] = breakpoints
        
        return cache_control
    
    def prepare_cached_prompt(self,
                            static_content: str,
                            dynamic_content: str,
                            breakpoints: Optional[list[int]] = None) -> Dict[str, Any]:
        """Prepare prompt with caching configuration.
        
        Args:
            static_content: Static content to cache (system prompt, tools, etc)
            dynamic_content: Dynamic content (user input, etc)
            breakpoints: Optional list of token breakpoints
            
        Returns:
            Complete prompt configuration with cache control
        """
        # Check cache first
        cached_response = self.get_cached_response(static_content, dynamic_content)
        if cached_response:
            return cached_response
        
        cache_control = self.create_cache_control(static_content, breakpoints)
        
        # Structure prompt to optimize caching
        prompt = f"{static_content}\n\n{dynamic_content}"
        
        return {
            "prompt": prompt,
            "cache_control": cache_control
        }
    
    def update_cache_stats(self, response_metadata: Dict[str, Any]) -> None:
        """Update cache statistics from response metadata.
        
        Args:
            response_metadata: Response metadata from Claude
        """
        # Log cache performance
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests > 0:
            hit_rate = (self.cache_stats['hits'] / total_requests) * 100
            
            logger.info(f"Cache performance - Hit rate: {hit_rate:.1f}% " 
                       f"(Hits: {self.cache_stats['hits']}, "
                       f"Misses: {self.cache_stats['misses']}, "
                       f"Writes: {self.cache_stats['writes']})")
    
    def clear_expired_cache(self):
        """Clear expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, timestamp in self._cache_timestamps.items():
            if (current_time - timestamp) >= self.config.ttl:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            if key in self._cache_store:
                del self._cache_store[key]
            if key in self._cache_timestamps:
                del self._cache_timestamps[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get current cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        # Clear expired entries before returning stats
        self.clear_expired_cache()
        
        return self.cache_stats.copy()
