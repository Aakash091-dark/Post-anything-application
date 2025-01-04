# storage.py
import os
import json
import shutil
from datetime import datetime
import time

class StorageManager:
    def __init__(self):
        # Create necessary directories
        self.data_dir = "data"
        self.files_dir = os.path.join(self.data_dir, "files")
        self.posts_file = os.path.join(self.data_dir, "posts.json")
        
        self._initialize_storage()

    def _initialize_storage(self):
        """Create necessary directories and files if they don't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.files_dir, exist_ok=True)
        
        if not os.path.exists(self.posts_file):
            with open(self.posts_file, 'w') as f:
                json.dump([], f)

    def add_post(self, content):
        """Add a new text post."""
        posts = self._read_posts()
        
        new_post = {
            'type': 'text',
            'content': content,
            'timestamp': time.time()
        }
        
        posts.append(new_post)
        self._write_posts(posts)

    def add_file(self, file_path):
        """
        Add a new file post.
        Copies the file to the data directory and creates a post entry.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File does not exist")
        
        # Create a unique filename
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        new_filename = timestamp + filename
        new_file_path = os.path.join(self.files_dir, new_filename)
        
        # Copy file to data directory
        shutil.copy2(file_path, new_file_path)
        
        # Add post entry
        posts = self._read_posts()
        new_post = {
            'type': 'file',
            'file_path': new_file_path,
            'file_type': os.path.splitext(filename)[1].lower(),
            'timestamp': time.time()
        }
        
        posts.append(new_post)
        self._write_posts(posts)

    def get_posts(self):
        """Retrieve all posts, sorted by timestamp (newest first)."""
        posts = self._read_posts()
        return sorted(posts, key=lambda x: x['timestamp'], reverse=True)

    def _read_posts(self):
        """Read posts from the JSON file."""
        try:
            with open(self.posts_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write_posts(self, posts):
        """Write posts to the JSON file."""
        with open(self.posts_file, 'w') as f:
            json.dump(posts, f, indent=4)