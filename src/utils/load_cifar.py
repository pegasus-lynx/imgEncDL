import pickle
from pathlib import Path
from typing import Union, ByteString
import numpy as np
from typing import Union, Tuple, Dict
from src import Filepath
from src.utils import maybe_to_path, decode_list, make_dir, _load_file
from src.utils.dataset import Image, Dataset

def load_cifar(name:str, dir_path:Filepath=None):
    assert name in ['cifar-10', 'cifar-100']
    if name == 'cifar-10':
        if not dir_path:
            dir_path = Path('../../data/cifar-10-batches-py')
        return load_cifar_10(dir_path)
    if name == 'cifar-100':
        if not dir_path:
            dir_path = Path('../../data/cifar-100-python')
        return load_cifar_100(dir_path)

def load_cifar_10(dir_path:Filepath):
    dir_path = maybe_to_path(dir_path)
    assert dir_path.exists(), f'Given path  {dir_path} does not exist'

    # img_dir = make_dir(dir_path / Path('images'))

    meta_file = dir_path / Path('batches.meta')
    meta = _load_file(meta_file)
    label_names = decode_list(meta[b'label_names'])

    keys = {
        'fnames': b'filenames',
        'datas': b'data',
        'labels': b'labels'
    }

    train_files = dir_path.glob('data_batch*')
    train_ds = Dataset(name='cifar-10-train', img_size=(32,32,3), 
                        label_names=label_names)
    for train_file in train_files:
        ds = _load_cifar_datafile(train_file, keys)
        train_ds.add(ds)

    test_file = dir_path / Path('test_batch')
    test_ds = Dataset(name='cifar-10-test', img_size=(32,32,3), 
                        label_names=label_names)
    test_ds.add(_load_cifar_datafile(test_file, keys))

    return train_ds, test_ds

def load_cifar_100(dir_path:Filepath, label_type:str='fine'):
    dir_path = maybe_to_path(dir_path)
    assert dir_path.exists(), f'Given path  {dir_path} does not exist'

    # img_dir = make_dir(dir_path / Path('images'))

    meta_file = dir_path / Path('meta')
    meta = _load_file(meta_file)
    label_names = decode_list(meta[f'{label_type}_label_names'.encode()])

    keys = {
        'fnames': b'filenames',
        'datas': b'data',
        'labels': f'{label_type}_labels'.encode()
    }

    train_file = dir_path / Path('train')
    train_ds = Dataset(name='cifar-100-train', img_size=(32,32,3), 
                        label_names=label_names)
    train_ds.add(_load_cifar_datafile(train_file, keys))

    test_file = dir_path / Path('test')
    test_ds = Dataset(name='cifar-100-test', img_size=(32,32,3), 
                        label_names=label_names)
    test_ds.add(_load_cifar_datafile(test_file, keys))

    return train_ds, test_ds

def _load_cifar_datafile(fpath:Filepath, keys:Dict[str,ByteString], 
                        shape:Tuple[int]=(32,32,3)):
    data = _load_file(fpath)
    length = len(data[keys[b'labels']])
    dataset = Dataset()
    for p in range(length):
        fname = data[keys['fnames']][p].decode('utf-8')
        imgarr = data[keys['datas']][p]
        label = data[keys['labels']][p]

        imgarr = np.reshape(imgarr, shape)
        img = Image(Path(fname),imgarr)
        dataset.append(img,label)
    return dataset
