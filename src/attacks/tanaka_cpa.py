
import numpy as np
import pickle
import math

from copy import deepcopy
from itertools import product
from src.utils.dataset import Image
from src.utils.random import RandomGen as Rg
from src.utils import _load_file
from pathlib import Path
from src.schemes.tanaka import TanakaScheme

class TanakaAttack():

    def cpa_attack(self, img):
        n = len(img.array)
        m = len(img.array[0])
        self.key =  3#int(img.fname.split('.')[-2])

        for i in range(16):
            help_img,abc = self.create_helper_image(i)
            a,b,c = abc
            ts_obj = TanakaScheme()
            enc_himg = ts_obj.encrypt(help_img)
            arr = deepcopy(enc_himg.array)
            arr2 = deepcopy(img.array)
            print(arr.shape, arr2.shape)


            for j,k in product(range(4),range(4)): # Each Pixel
                for rgb in range(3):  # RGB
                    if (arr[j][k][rgb] == 256 - a ) or (arr[j][k][rgb] == 256 - b) or (arr[j][k][rgb] == 256 - c):
                        arr[j][k][rgb] = 255 - arr[j][k][rgb]
                        for ii,jj in product(range(n//4),range(m//4)):
                            for b1,b2 in product(range(4), range(4)):
                                arr2[ii*4 + b1][jj*4 + b2][rgb] = 255 - arr2[ii*4 + b1][jj*4 + b2][rgb]


            attack_dec = arr2
            helpers_dec = arr

            for helper_ind in range(16): 
                for value in range(3):
                    i_match = 0
                    j_match = 0
                    rgb_match = 0

                    for i in range(4):
                        for j in range (3):
                            for rgb in range(3):
                                if helpers_dec[i, j, rgb] == value:
                                    i_match = i
                                    j_match = j
                                    rgb_match = rgb

                    if i_match != 0:
                        i_spot = helper_ind // 4 
                        j_spot = helper_ind % 4
                        rgb_spot = value

                        for i_block in range(n//4):
                            for j_block in range(m//4):
                                attack_dec[4*i_block + i_spot, 4*j_block + j_spot, rgb_spot] = arr2[4*i_block + i_match, 4*j_block + j_match, rgb_match]

        return Image(nparray = attack_dec)
 
  
    @classmethod
    def create_helper_image(cls, fix_j, nbits:int=8):
        array = np.zeros([4,4,3], dtype=np.long)
        inits = np.asarray(cls.get_channel_inits(nbits))
        rows = 4
        cols = 4
        i = fix_j // 4
        j = fix_j % 4
        array[i][j] = inits
        himg = Image(nparray = array)
        return himg, inits
  
    @classmethod
    def get_channel_inits(cls, nbits:int=8):
        max_val = (2**nbits)-2
        nums = Rg.list(7, max_val, 1)
        chosen = [nums[0], nums[0], nums[0]]
        for r in [1, 2]:
            p = 0
            no_break = True
            inc_p = False
            while no_break:
                for k in range(r):
                    if cls.num_match(chosen[k],nums[p]):
                        inc_p = True                        
                        break
                if inc_p:
                    p += 1
                    inc_p = False
                    continue
                no_break = False
            chosen[r] = nums[p]
        return chosen
  
    @classmethod
    def num_match(cls, a, b, nbits:int=8):
        if a == b:
            return True
        max_val = (2**nbits)-1
        xor_a = max_val ^ a
        xor_b = max_val ^ b
        if a == xor_b or b == xor_a:
            return True
        return False