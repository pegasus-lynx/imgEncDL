import pickle
from typing import ByteString, List

from src import Filepath
from pathlib import Path                                                                                                                                                                          

def ensure_path(path:Filepath):
    if isinstance(path, str):
        return Path(path)
    return path

def ensure_dir(path:Filepath):
    path = ensure_path(path)
    if not path.exists():
        path.mkdir()
    return path

def decode_list(array:List[ByteString]):
    return list(map(lambda x: x.decode('utf-8'), array))

def encode_list(array:List[str]):
    return list(map(lambda x: x.encode(), array))

def _load_file(fpath:Filepath):
    with open(fpath, 'rb') as fr:
        data = pickle.load(fr, encoding='bytes')
    return data

def _dump_file(data, fpath):
    with open(fpath, 'rb') as fw:
        pickle.dump(data, fw)

def log(text, tabs:int=0):
    print(f'{"    "*tabs}{text}')