import argparse
from pathlib import Path

from src.schemes import SchemeRegistry, SchemeFactory
from src.utils import ensure_dir, ensure_path, log, _dump_file, _load_file, decode_list
from src.utils.load_cifar import _load_cifar_datafile
from src.utils.dataset import Dataset, Image
from src import Filepath
import shutil

def parse_args():
    parser = argparse.ArgumentParser(prog='encrypt_cifar', description='Script for \
                                    encrypting cifar data files')
    parser.add_argument('-cn', '--cifar_type', type=int, choices=[10, 100])
    parser.add_argument('-cd', '--cifar_dir', type=Path, help='Path to the cifar directory')
    parser.add_argument('-e', '--enc_scheme', type=str, choices=['skk', 'skkd', 'etc', 'ele', 'tanaka'],
                        help='Scheme for encrypting the images')
    parser.add_argument('-b', '--block_shape', type=int, nargs='+', default=(4, 4))
    parser.add_argument('-i', '--image_shape', type=int, nargs='+', default=(32, 32))
    parser.add_argument('-n', '--nblocks', type=int, default=64)
    return parser.parse_args()

def validate_args(args):
    assert args.enc_scheme in SchemeRegistry.schemes
    assert args.cifar_dir.exists()    

def encrypt_cifar_dataset(dataset, scheme, work_dir:Filepath):
    enc_dataset = Dataset()
    for row in dataset:
        image, label = row
        enc_image = scheme.encrypt(image)
        enc_image.filepath = image.filepath
        enc_dataset.append(enc_image, label)
    return enc_dataset

def encrypt_cifar_10(dir_path, scheme, work_dir):
    meta_file = dir_path / Path('batches.meta')
    meta = _load_file(meta_file)
    label_names = decode_list(meta[b'label_names'])
    shutil.copy(meta_file, work_dir / Path('batches.meta'))
    keys = {
        'fnames': b'filenames',
        'datas': b'data',
        'labels': b'labels'
    }

    files = [x for x in dir_path.glob('data_batch*')]
    files.append(dir_path / Path('test_batch'))
    for file in files:
        ds = _load_cifar_datafile(file, keys)
        enc_ds = encrypt_cifar_dataset(ds, scheme, work_dir)
        save_encrypted_dataset(enc_ds, work_dir / file.name, keys)

def encrypt_cifar_100(dir_path, scheme, work_dir):
    meta_file = dir_path / Path('meta')
    meta = _load_file(meta_file)
    label_names = decode_list(meta[f'{label_type}_label_names'.encode()])
    shutil.copy(meta_file, work_dir / Path('meta'))

    keys = {
        'fnames': b'filenames',
        'datas': b'data',
        'labels': f'{label_type}_labels'.encode()
    }

    files = [ dir_path / Path('train'), dir_path / Path('test') ]
    for file in files:
        ds = _load_cifar_datafile(file, keys)
        enc_ds = encrypt_cifar_dataset(ds, scheme, work_dir)
        save_encrypted_dataset(enc_ds, work_dir / file.name, keys)

def save_encrypted_dataset(dataset, work_file, keys):
    data = {
        keys['fnames'] : [str(x.filepath.name) for x in dataset.images],
        keys['datas'] : [x.array for x in dataset.images],
        keys['labels'] : dataset.labels
    }
    _dump_file(data, work_file)

def encrypt_cifar(cifar_type, data_dir, scheme, work_dir):
    if cifar_type == 10:
        encrypt_cifar_10(data_dir, scheme, work_dir)
    elif cifar_type == 100:
        encrypt_cifar_100(data_dir, scheme, work_dir)

def main():
    args = parse_args()
    validate_args(args)

    log(f'Initializing Scheme : {args.enc_scheme} ...')
    scheme = SchemeFactory.get_scheme(scheme=args.enc_scheme, 
                                        block_shape=args.block_shape, 
                                        nblocks=args.nblocks)
    work_dir = ensure_dir(args.cifar_dir / 'enc.etc.2') 

    log(f'Encrypting CIFAR - {args.cifar_type} ...')
    encrypt_cifar(args.cifar_type, args.cifar_dir, scheme, work_dir)

    log('Saving the encryption keys')
    scheme.save(work_dir)

if __name__ == '__main__':
    main()