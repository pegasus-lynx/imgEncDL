import argparse
from pathlib import Path

from src.schemes import SchemeRegistry, SchemeFactory
from src.utils import ensure_dir, ensure_path, log
from src.utils.dataset import Image
from src import Filepath

def parse_args():
    parser = argparse.ArgumentParser(prog='encrypt', description='Script for \
                                    encrypting images from a dir')
    parser.add_argument('-id', '--img_dir', type=Path, help='Path to the image directory')
    parser.add_argument('-if', '--img_files', type=Path, nargs='+', help='Path to an image files')
    parser.add_argument('-w', '--work_dir', type=Path, help='Path for saving the encrypted images')
    parser.add_argument('-e', '--enc_scheme', type=str, choices=['skk', 'skkd', 'etc', 'ele', 'tanaka'],
                        help='Scheme for encrypting the images')
    parser.add_argument('-b', '--block_shape', type=int, nargs='+', default=(4, 4))
    parser.add_argument('-i', '--image_shape', type=int, nargs='+', default=(32, 32))
    parser.add_argument('-n', '--nblocks', type=int, default=64)
    return parser.parse_args()

def validate_args(args):
    assert args.enc_scheme in SchemeRegistry.schemes
    
    inp_flag = False
    if args.img_files:
        inp_flag = True
        for img_file in args.img_files:
            assert img_file.exists()
    if args.img_dir:
        inp_flag = True
        assert args.img_dir.exists()
    if not inp_flag:
        raise ValueError('Input Values not provided. Provide either img_files or img_dir')

def encrypt_image(fname:Filepath, scheme, work_dir:Path):
    assert scheme, 'No scheme found.'
    img = Image(fname)
    enc_img = scheme.encrypt(img)
    fname = ensure_path(img.fname)
    Image.save(enc_img, work_dir / fname.with_suffix(f'.{scheme.name}.jpg'))

def main():
    args = parse_args()
    validate_args(args)

    log(f'Initializing Scheme : {args.enc_scheme} ...')
    
    # nblocks = (image_shape[0] // )
    scheme = SchemeFactory.get_scheme(scheme=args.enc_scheme, 
                                        block_shape=args.block_shape, 
                                        nblocks=args.nblocks)
    work_dir = ensure_dir(args.work_dir) 

    if args.img_files:
        log('Encrypting Image Files ...')
        for img_file in args.img_files:
            log(str(img_file.name), 2)
            encrypt_image(img_file, scheme, work_dir)

    if args.img_dir:
        img_dir = ensure_dir(work_dir / Path(args.img_dir.name))
        log(f'Encrypting Images from dir {args.img_dir} ...')
        images = args.img_dir.glob('*.jpg')
        for image in images:
            log(str(image.name), 2)
            encrypt_image(image, scheme, img_dir)

    log('Saving the encryption keys')
    scheme.save(work_dir)

if __name__ == '__main__':
    main()