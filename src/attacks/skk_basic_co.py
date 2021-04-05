from src.utils.dataset import Image

class SKKCipherOnlyBasic(object):

    @classmethod
    def attack(cls, img, leading_bit:int=0, nbits:int=8):
        shape = img.shape()
        array = img.array
        xor_val = (2**nbits) - 1
        rows, cols, channels = shape
        for r in range(rows):
            for c in range(cols):
                for ch in range(channels):
                    cell = array[r,c,ch]
                    if not cls.check_leading(cell, leading_bit, nbits):
                        cell = cell ^ xor_val
                    array[r,c,ch] = cell
        nimg = Image(nparray=array)
        return nimg

    @classmethod
    def check_leading(cls, val, leading_bit, nbits):
        curr_bit = cls.get_leading(val, nbits)
        if curr_bit == leading_bit:
            return True
        return False
        
    @classmethod
    def get_leading(cls, val, nbits):
        text = bin(val).replace('0b', '')
        if len(text) < nbits:
            return 0
        return 1
