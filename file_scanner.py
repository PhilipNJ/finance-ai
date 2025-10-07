"""
File Scanner Module

Automatically scans a specified directory for new financial documents
and processes them using the AI agent workflow. Maintains persistent
memory of processed files to avoid duplicates.
"""
import json
import hashlib
from pathlib import Path
from typing import Set, List, Tuple
from datetime import datetime


class FileScanner:
    """Scans directories for new files and tracks processed files."""
    
    def __init__(self, watch_dir: Path, processed_file: Path):
        """
        Initialize the file scanner.
        
        Args:
            watch_dir: Directory to watch for new files
            processed_file: JSON file to store processed file hashes
        """
        self.watch_dir = Path(watch_dir)
        self.processed_file = Path(processed_file)
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        
        # Load processed files from persistent storage
        self.processed_hashes = self._load_processed_files()
    
    def _load_processed_files(self) -> Set[str]:
        """Load the set of processed file hashes from disk."""
        if self.processed_file.exists():
            try:
                with open(self.processed_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_hashes', []))
            except Exception as e:
                print(f"⚠️  Warning: Could not load processed files: {e}")
                return set()
        return set()
    
    def _save_processed_files(self):
        """Save the set of processed file hashes to disk."""
        try:
            data = {
                'processed_hashes': list(self.processed_hashes),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.processed_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save processed files: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex string of the file hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def scan_for_new_files(self) -> List[Tuple[Path, str]]:
        """
        Scan the watch directory for new files.
        
        Returns:
            List of tuples (file_path, file_hash) for new files
        """
        new_files = []
        
        # Supported file extensions
        supported_extensions = {'.csv', '.pdf', '.txt', '.text'}
        
        # Scan directory
        for file_path in self.watch_dir.iterdir():
            # Skip if not a file or not supported extension
            if not file_path.is_file():
                continue
            
            if file_path.suffix.lower() not in supported_extensions:
                continue
            
            # Calculate file hash
            try:
                file_hash = self._get_file_hash(file_path)
                
                # Check if already processed
                if file_hash not in self.processed_hashes:
                    new_files.append((file_path, file_hash))
            
            except Exception as e:
                print(f"⚠️  Warning: Could not process {file_path.name}: {e}")
                continue
        
        return new_files
    
    def mark_as_processed(self, file_hash: str):
        """
        Mark a file as processed.
        
        Args:
            file_hash: Hash of the processed file
        """
        self.processed_hashes.add(file_hash)
        self._save_processed_files()
    
    def get_stats(self) -> dict:
        """Get statistics about processed files."""
        return {
            'total_processed': len(self.processed_hashes),
            'watch_directory': str(self.watch_dir),
            'processed_file': str(self.processed_file)
        }
