import numpy as np
from itertools import permutations

from src.utils.dataset import Image

class SKKCipherOnlyAdv(object):

    @classmethod
    def attack(cls, img):
        array = img.array
        shape = img.shape()
        rows, cols, _ = shape
        for r in range(rows):
            for c in range(cols):
                if r==0 and c==0:
                    continue
                p = array[r,c]
                q = array[r,c-1] if r==0 else array[r-1,c]
                min_diff = cls.cell_diff(p, q)
                min_diff_arg = p
                p_opts = cls.generate(p)
                for x in p_opts:
                    if cls.cell_diff(x,q) < min_diff:
                        min_diff = cls.cell_diff(x, q)
                        min_diff_arg = x
                array[r,c] = min_diff_arg
        dec_img = Image(nparray=array)
        return dec_img

    @classmethod
    def cell_diff(cls, a, b):
        return np.sum(np.absolute(a-b))

    @classmethod
    def generate(cls, cell, nbits:int=8):
        opts = []
        max_val = (2**nbits)-1
        perms = list(permutations(cell.tolist()))
        for cell_perm in perms:
            for mask in range(8):
                temp = list(cell_perm)
                if mask&1:
                    temp[2] = max_val ^ temp[2]
                if mask&2:
                    temp[1] = max_val ^ temp[1]
                if mask&4:
                    temp[0] = max_val ^ temp[0]
                opts.append(np.asarray(temp))
        return opts