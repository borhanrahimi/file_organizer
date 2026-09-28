import time
from pathlib import Path

def get_file_signature(file_path):
    """Return file identity, size, and modification time, or None."""
    path = Path(file_path)

    try: 
        if not path.is_file():
            return None
        
        info = path.stat()
    except OSError:
        return None
    
    return(
        info.st_dev,  # Device
        info.st_ino,  # Inode
        info.st_size,  # Size
        info.st_mtime_ns  # Modification time
    )

class FileReadinessTracker:
    def __init__(self, stable_seconds=3.0, clock=time.monotonic):
        self.stable_seconds = stable_seconds
        self.clock = clock
        self._observations = {}

    def is_ready(self, filepath):
        path = Path(filepath)
        signature = get_file_signature(path)

        if signature is None:
            self.forget(path)
            return False
        
        now = self.clock()
        previous = self._observations.get(path)

        if previous is None or previous[0] != signature:
            self._observations[path] = (signature, now)
            return False
        
        unchanged_since = previous[1]
        return now - unchanged_since >= self.stable_seconds
    
    def forget(self, filepath):
        self._observations.pop(Path(filepath), None)