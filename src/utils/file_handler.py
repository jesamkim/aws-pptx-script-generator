"""File Handler Utilities.

This module provides utilities for safe file operations, temporary file management,
and resource cleanup.
"""

import os
import tempfile
import shutil
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import hashlib
from loguru import logger


class FileHandler:
    """Handles file operations with safety and cleanup features."""
    
    def __init__(self, temp_prefix: str = "sa_script_gen_"):
        """Initialize file handler.
        
        Args:
            temp_prefix: Prefix for temporary files and directories
        """
        self.temp_prefix = temp_prefix
        self.temp_files: List[str] = []
        self.temp_dirs: List[str] = []
        logger.info(f"Initialized file handler with prefix: {temp_prefix}")
    
    def create_temp_file(self, suffix: str = "", content: Optional[bytes] = None) -> str:
        """Create a temporary file.
        
        Args:
            suffix: File suffix/extension
            content: Optional content to write to file
            
        Returns:
            Path to temporary file
        """
        try:
            fd, temp_path = tempfile.mkstemp(
                suffix=suffix,
                prefix=self.temp_prefix
            )
            
            # Write content if provided
            if content:
                with os.fdopen(fd, 'wb') as f:
                    f.write(content)
            else:
                os.close(fd)
            
            self.temp_files.append(temp_path)
            logger.debug(f"Created temporary file: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create temporary file: {str(e)}")
            raise
    
    def create_temp_dir(self) -> str:
        """Create a temporary directory.
        
        Returns:
            Path to temporary directory
        """
        try:
            temp_dir = tempfile.mkdtemp(prefix=self.temp_prefix)
            self.temp_dirs.append(temp_dir)
            logger.debug(f"Created temporary directory: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to create temporary directory: {str(e)}")
            raise
    
    def save_uploaded_file(self, uploaded_file: Any, target_dir: Optional[str] = None) -> str:
        """Save uploaded file to temporary location.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            target_dir: Optional target directory, uses temp dir if None
            
        Returns:
            Path to saved file
        """
        try:
            if target_dir is None:
                target_dir = self.create_temp_dir()
            
            # Create safe filename
            safe_filename = self.sanitize_filename(uploaded_file.name)
            file_path = os.path.join(target_dir, safe_filename)
            
            # Write file content
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            logger.info(f"Saved uploaded file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {str(e)}")
            raise
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        sanitized = f"{name}{ext}"
        logger.debug(f"Sanitized filename: {filename} -> {sanitized}")
        return sanitized
    
    def validate_file_type(self, file_path: str, allowed_extensions: List[str]) -> bool:
        """Validate file type by extension.
        
        Args:
            file_path: Path to file
            allowed_extensions: List of allowed extensions (e.g., ['.pptx', '.pdf'])
            
        Returns:
            True if file type is allowed, False otherwise
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            is_valid = file_ext in [ext.lower() for ext in allowed_extensions]
            
            logger.debug(f"File type validation: {file_ext} -> {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to validate file type: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            
            file_info = {
                'name': path.name,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'extension': path.suffix.lower(),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'exists': path.exists(),
                'is_file': path.is_file(),
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
            }
            
            # Calculate file hash for integrity checking
            if path.exists() and path.is_file():
                file_info['md5_hash'] = self.calculate_file_hash(file_path)
            
            logger.debug(f"Retrieved file info for: {file_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to get file info: {str(e)}")
            return {'error': str(e)}
    
    def calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """Calculate file hash for integrity checking.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('md5', 'sha256', etc.)
            
        Returns:
            File hash as hexadecimal string
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            logger.debug(f"Calculated {algorithm} hash for {file_path}: {file_hash[:16]}...")
            return file_hash
            
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {str(e)}")
            return ""
    
    def backup_file(self, file_path: str, backup_dir: Optional[str] = None) -> str:
        """Create backup copy of a file.
        
        Args:
            file_path: Path to file to backup
            backup_dir: Optional backup directory, uses temp dir if None
            
        Returns:
            Path to backup file
        """
        try:
            if backup_dir is None:
                backup_dir = self.create_temp_dir()
            
            source_path = Path(file_path)
            backup_name = f"{source_path.stem}_backup_{int(time.time())}{source_path.suffix}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Created backup: {file_path} -> {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise
    
    def safe_file_operation(self, file_path: str, operation: callable, *args, **kwargs):
        """Perform file operation with automatic backup and rollback.
        
        Args:
            file_path: Path to file
            operation: Function to perform on file
            *args, **kwargs: Arguments for operation function
            
        Returns:
            Result of operation
        """
        backup_path = None
        
        try:
            # Create backup
            backup_path = self.backup_file(file_path)
            
            # Perform operation
            result = operation(file_path, *args, **kwargs)
            
            logger.info(f"Safe file operation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"File operation failed, attempting rollback: {str(e)}")
            
            # Attempt rollback
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, file_path)
                    logger.info(f"Successfully rolled back file: {file_path}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {str(rollback_error)}")
            
            raise
    
    def cleanup_temp_files(self):
        """Clean up all temporary files and directories."""
        cleaned_files = 0
        cleaned_dirs = 0
        
        # Clean up temporary files
        for temp_file in self.temp_files[:]:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    cleaned_files += 1
                self.temp_files.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {str(e)}")
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs[:]:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    cleaned_dirs += 1
                self.temp_dirs.remove(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to remove temp dir {temp_dir}: {str(e)}")
        
        logger.info(f"Cleaned up {cleaned_files} temp files and {cleaned_dirs} temp directories")
    
    @contextmanager
    def temp_file_context(self, suffix: str = "", content: Optional[bytes] = None):
        """Context manager for temporary file with automatic cleanup.
        
        Args:
            suffix: File suffix/extension
            content: Optional content to write to file
            
        Yields:
            Path to temporary file
        """
        temp_path = None
        try:
            temp_path = self.create_temp_file(suffix, content)
            yield temp_path
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    if temp_path in self.temp_files:
                        self.temp_files.remove(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_path}: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup_temp_files()


# Global file handler instance
file_handler = FileHandler()
