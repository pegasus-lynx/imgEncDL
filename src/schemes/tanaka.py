import numpy as np
from typing import Union
from .abstract import AbstractScheme
from copy import deepcopy
import math
from itertools import permutations,product
from ..utils.dataset import Image
import pickle
from ..utils import _load_file
from pathlib import Path

class TanakaScheme(AbstractScheme):

    def __init__(self):
        self.name = 'tanaka'
        self.key = np.random.randint(0,(1<<16))
    
    def encrypt(self,img):
        key = np.random.randint(0,(1<<16))
        return self.encrypt_fn(img, key)

    def encrypt_uk(self, img, key):
        return self.encrypt_fn(img, key)

    def encrypt_fn(self, img, key):
        np.random.seed(self.key)
        n = len(img.array)
        m = len(img.array[0])
        block_size = [16,16]
        sz = 16
        #Generating the pixel color exchange key
        pi_exc_map_x = np.random.randint(0, sz, block_size)
        pi_exc_map_y = np.random.randint(0, sz, block_size)

        #Generating the pixels to be flipped in a box.
        flip = np.random.randint(0, 3, block_size)
        colour_flip = np.random.randint(0, 3, block_size)
        choose_colour_flip = np.random.randint(0, 5, block_size)
        arr = deepcopy(img.array)
        for i,j in product(range(n//sz),range(m//sz)):
            for k,l in product(range(sz),range(sz)):        
                a = arr[i*sz + k][j*sz + l][flip[k][l]]
                b = arr[i*sz + pi_exc_map_x[k][l]][j*sz + pi_exc_map_y[k][l]][flip[k][l]]
                arr[i*sz + pi_exc_map_x[k][l]][j*sz + pi_exc_map_y[k][l]][flip[k][l]] = a
                arr[i*sz + k][j*sz + l][flip[k][l]] = b
                if(choose_colour_flip[k][l] == 0):
                    arr[i*sz + k][j*sz + l][colour_flip[k][l]] = 255 - arr[i*sz + k][j*sz + l][colour_flip[k][l]]
        return Image(nparray = arr)

    def decrypt(self,img):
        np.random.seed(self.key)
        n = len(img.array)
        m = len(img.array[0])

        #Generating the pixel color exchange key
        pi_exc_map_x = np.random.randint(0, 4, size  =  [4,4])
        pi_exc_map_y = np.random.randint(0, 4, size  =  [4,4])


        #Generating the pixels to be flipped in a box
        flip = np.random.randint(0, 3, size  =  [4,4])

        arr=deepcopy(img.array)

        for i,j in product(range(n//4),range(m//4)):
            for k,l in product(range(3, -1, -1),range(3, -1, -1)):
                temp = arr[i*4 + k][j*4 + l][flip[k][l]]
                arr[i*4 + k][j*4 + l][flip[k][l]] = arr[i*4 + pi_exc_map_x[k][l]][j*4 + pi_exc_map_y[k][l]][flip[k][l]]
                arr[i*4 + pi_exc_map_x[k][l]][j*4 + pi_exc_map_y[k][l]][flip[k][l]] = temp
        return Image(nparray = arr)

    def save(self,work_dir):
        data = {
            'name':self.name,
            'key':self.key
        }
        #pickle.dump(data,work_dir / Path(f"{self.name}.scheme.file"))

    @classmethod
    def load(cls,load_file):
        data = _load_file(load_file)
        scheme = cls()
        scheme.key = data[b'key']
        
