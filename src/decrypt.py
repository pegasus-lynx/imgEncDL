import argparse
from pathlib import Path

from src.schemes import SchemeRegistry, SchemeFactory
from src.utils import ensure_dir, ensure_path, log
from src.utils.dataset import Image
from src import Filepath

def parse_args():
    parser = argparse.ArgumentParser(prog='decrypt', description='Script for \
                                    decrypting images from a dir / files')
    parser.add_argument('-i', '--img_dir', type=Path, help='Path to the image directory')
    parser.add_argument('-f', '--img_files', type=Path, nargs='+' help='Path to an image files')
    parser.add_argument('-w', '--work_dir', type=Path, help='Path for saving the encrypted images')
    parser.add_argument('-k', '--key_file', type=Path, help='Path to the key file')

def validate_args(args):
    assert args.key_file.exists()
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

def decrypt_image(fname:Filepath, scheme, work_dir:Filepath):
    assert scheme, 'No scheme found.'
    work_dir = ensure_path(work_dir)
    img = Image(fname)
    dec_img = scheme.decrypt(img)
    fname = ensure_path(img.fname)
    Image.save(dec_img, work_dir / fname.with_suffix(f'.dec.jpg'))

def main():
    args = parse_args()
    validate_args(args)

    log(f'Loading Scheme : {args.enc_scheme} from {args.key_file.name} ...')
    scheme = SchemeFactory.load_scheme(scheme=args.enc_scheme,
                                        key_file=args.key_file)
    work_dir = ensure_dir(args.work_dir)

    if args.img_files:
        log('Decrypting Image Files ...')
        for img_file in args.img_files:
            log(str(img_file.name), 2)
            decrypt_image(img_file, scheme, work_dir)

    if args.img_dir:
        img_dir = ensure_dir(work_dir / Path(args.img_dir.name))
        log(f'Decrypting Images from dir {args.img_dir} ...')
        images = args.img_dir.glob('*.jpg')
        for image in images:
            log(str(image.name), 2)
            decrypt_image(image, scheme, img_dir)

    log('Decryption Complete.')

if __name__ == '__main__':
    main()