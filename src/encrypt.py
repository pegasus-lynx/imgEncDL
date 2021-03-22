import argparse
from pathlib import Path

from src.schemes import SchemeRegistry, SchemeFactory
from src.utils import make_dir
from src.utils.dataset import Image, Dataset
from src import Filepath

def parse_args():
    parser = argparse.ArgumentParser(prog='encrypt', description='Script for \
                                    encrypting images from a dir')
    parser.add_argument('-i', '--img_dir', type=Path, help='Path to the image directory')
    parser.add_argument('-f', '--img_files', type=Path, nargs='+', help='Path to an image files')
    parser.add_argument('-nf', '--nparray_file', type=Path, help='If images are stored as nparrays')
    parser.add_argument('-w', '--work_dir', type=Path, help='Path for saving the encrypted images')
    parser.add_argument('-e', '--enc_scheme', type=str, choices=['skk', 'skkd', 'etc', 'ele', 'tanaka'],
                        help='Scheme for encrypting the images')
    parser.add_argument('-b', '--block_shape', type=int, nargs='+', default=(4, 4))
    parser.add_argument('-n', '--nblocks', type=int, default=64)
    return parser.parse_args()

def validate_args(args):
    assert args.work_dir
    assert args.enc_scheme in SchemeRegistry.schemes
    
    inp_flag = False
    if args.img_files:
        inp_flag = True
        for img_file in args.img_files:
            assert img_file.exists()
    if args.nparray_file:
        inp_flag = True
        assert args.nparray_file.exists()
    if args.img_dir:
        inp_flag = True
        assert args.img_dir.exists()
    if not inp_flag:
        raise ValueError('Input Values not provided. Provide either img_files, nparray_file or img_dir')

def encrypt_image(fname:Filepath, scheme, work_dir:Path):
    assert scheme, 'No scheme found.'
    img = Image(fname)
    enc_img = scheme.encrypt(img)
    fname = Path(img.fname)
    # img.save(work_dir / fname.with_suffix('.jpg'))
    Image.save(enc_img, work_dir / fname.with_suffix(f'.{scheme.name}.jpg'))

def main():
    args = parse_args()
    validate_args(args)

    scheme = SchemeFactory.get_scheme(scheme=args.enc_scheme, 
                                        block_shape=args.block_shape, 
                                        nblocks=args.nblocks)
    work_dir = make_dir(args.work_dir) 

    if args.img_files:
        for img_file in args.img_files:
            encrypt_image(img_file, scheme, work_dir)

    if args.nparray_file:
        pass

    if args.img_dir:
        img_dir = make_dir(work_dir / Path(args.img_dir.name))
        images = args.img_dir.glob('*.jpg')
        for image in images:
            encrypt_image(image, scheme, img_dir)

    print('Saving the encryption keys')
    # scheme.save(work_dir / Path('key.file'))

if __name__ == '__main__':
    main()