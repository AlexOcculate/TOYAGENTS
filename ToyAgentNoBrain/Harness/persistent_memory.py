# Import json for serialization (pure stdlib).
import json

# Import os to check if the file exists (pure stdlib).
import os


# PersistentMemory stores key-value pairs in a JSON file on disk.
# This simulates what a real agent might use (SQLite, Redis, etc.)
class PersistentMemory:

    # Constructor — takes the path to the memory file.
    def __init__(self, filepath="agent_memory.json"):

        self.filepath = filepath

        # Load existing data if the file already exists.
        self._data = self._load()

    # Load JSON from disk. Returns empty dict if file doesn't exist or is corrupt.
    def _load(self):

        # If file doesn't exist, start fresh.
        if not os.path.exists(self.filepath):
            return {}
        try:

            # Open and parse the JSON file.
            with open(self.filepath, "r") as f:
                return json.load(f)

        except (json.JSONDecodeError, IOError):

            # If file is corrupt, start fresh (recovery-friendly).
            return {}

    # Save current data to disk.
    def _save(self):

        with open(self.filepath, "w") as f:
            json.dump(self._data, f, indent=2)

    # Store a key-value pair and persist immediately.
    def store(self, key, value):

        self._data[key] = value
        self._save()

    # Recall a value by key. Returns None if not found.
    def recall(self, key):

        return self._data.get(key, None)

    # Return a copy of all stored data.
    def get_all(self):

        return dict(self._data)

    # Remove a key if it exists.
    def delete(self, key):

        if key in self._data:
            del self._data[key]
            self._save()
