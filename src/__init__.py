from typing import List, Tuple, Dict, Union
from pathlib import Path

Filepath = Union[Path,str]

def ensure_path(path:Filepath):
    if isinstance(path, Path):
        return path
    return Path(path)