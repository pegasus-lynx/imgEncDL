import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(prog='decrypt', description='Script for \
                                    decrypting images from a dir / files')
    parser.add_argument('-i', '--img_dir', type=Path, help='Path to the image directory')
    parser.add_argument('-f', '--img_files', type=Path, nargs='+' help='Path to an image files')
    parser.add_argument('-n', '--nparray_file', type=Path, help='If images are stored as nparrays')
    parser.add_argument('-w', '--work_dir', type=Path, help='Path for saving the encrypted images')
    parser.add_argument('-k', '--key_file', type=Path, help='Path to the key file')

def validate_args(args):
    assert args.key_file.exists()

def main():
    args = parse_args()
    validate_args(args)

if __name__ == '__main__':
    main()