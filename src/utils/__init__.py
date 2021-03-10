from src import Filepath
from typing import List, ByteString

def maybe_to_path(path:Filepath):
    if isinstance(path, str):
        return Path(path)
    return path

def make_dir(path:Filepath):
    path = maybe_to_path(path)
    if not path.exists():
        path.mkdir()
    return path

def decode_list(array:List[ByteString]):
    return list(map(lambda x: x.decode('utf-8'), array))

def encode_list(array:List[str]):
    return list(map(labmbda x: x.encode(), array))