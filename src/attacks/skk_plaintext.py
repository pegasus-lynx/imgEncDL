from src.utils.dataset import Image
from src.utils.random import RandomGen as Rg
import numpy as np
from pathlib import Path

class SKKPlainText(object):

    @classmethod
    def attack(cls, img, scheme, nbits:int=8):
        shape = img.shape()
        rows, cols, channels = shape

        max_val = (2**nbits)-1

        himg = cls.get_helper_image(shape)
        enc_himg = scheme.encrypt(himg)
        
        chosen = himg.array[0,0]
        chosen_xor = chosen ^ ((2**nbits)-1)

        for r in range(rows):
            for c in range(cols):
                for ch in range(channels):
                    val = enc_himg.array[r,c,ch]
                    if cls.match_with_arr(val, chosen_xor):
                        val = enc_himg.array[r,c,ch]
                        enc_himg.array[r,c,ch] = val ^ max_val
                        val = img.array[r,c,ch]
                        img.array[r,c,ch] = val ^ max_val
                cell = enc_himg.array[r,c]
                pos = cls.get_pos(cell, chosen)
                img.array[r,c] = cls.permute_cell(img.array[r,c], pos)
        return img

    @classmethod
    def get_helper_image(cls, shape, nbits:int=8):
        array = np.zeros(shape, dtype=np.long)
        inits = np.asarray(cls.get_channel_inits(nbits))
        rows, cols, _ = shape
        for r in range(rows):
            for c in range(cols):
                array[r,c] = inits
        himg = Image(filepath=Path('helper_image.jpg'), nparray=array)
        return himg

    @classmethod
    def get_channel_inits(cls, nbits:int=8):
        max_val = (2**nbits)-1
        nums = Rg.list(7, max_val, 0)
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

    @classmethod
    def match_with_arr(cls, val, arr):
        for x in arr:
            if val == x:
                return True
        return False

    @classmethod
    def get_pos(cls, cell, chosen):
        pos = [-1, -1, -1]
        for x in range(3):
            for i,c in enumerate(chosen):
                if cell[x] == c:
                    pos[x] = i
                    break
        return pos

    @classmethod
    def permute_cell(cls, cell, pos):
        temp = [0,0,0]
        for i,p in enumerate(pos):
            temp[i] = cell[p]
        for i in range(3):
            cell[i] = temp[i]
        return cell
