from skimage import color
from skimage.transform import rescale, resize, downscale_local_mean
from typing import Tuple
import numpy as np

class Transformer(object):
    @classmethod
    def rescale(cls, array, scale_factor:float=1.0, anti_aliasing:bool=True):
        array = rescale(array, scale_factor, anti_aliasing=anti_aliasing)
        return array

    @classmethod
    def resize(cls, array, shape:Tuple[int], anti_aliasing:bool=True):
        array = resize(array, shape, anti_aliasing=anti_aliasing)
        return array

    @classmethod
    def downscale(cls, img, downscale_factor:Tuple[int]):
        array = downscale_local_mean(array, downscale_factor)
        return array

    @classmethod
    def togray(cls, array):
        array = color.rgb2gray(array)
        return array

    @classmethod
    def rotate(cls, array, angle:int=0):
        if angle not in [0, 90, 180, 270]:
            angle = 0
        if angle == 0:
            pass
        elif angle == 90:
            array = np.rot90(array)
        elif angle == 180:
            array = np.rot90(array, 2)
        elif angle == 270:
            array = np.rot90(array, 3)
        return array

    @classmethod
    def reverse(cls, array, mode:str='h'):
        if mode == 'h':
            array = np.flip(array, axis=0)
        elif mode == 'r':
            array = np.flip(array, axis=1)
        return array

    @classmethod
    def channel_permute(cls, array, permute:int=0):
        shape = array.shape
        rows, cols, _ = shape
        perumtation = cls._get_permute(permute=permute)
        arrays = [np.reshape(array[:,:,ch], (rows, cols, 1)) for ch in perumtation]
        array = np.concatenate(arrays, axis=2)
        return array        

    @staticmethod
    def _get_permute(permute:int=0):
        if permute == 0:
            return [0, 1, 2]
        elif permute == 1:
            return [0, 2, 1]
        elif permute == 2:
            return [1, 0, 2]
        elif permute == 3:
            return [0, 2, 1]
        elif permute == 4:
            return [2, 0, 1]
        elif permute == 5:
            return [2, 1, 0]

    @staticmethod
    def _channel_permute(arr, permute:int=0):
        narr = np.zeros((3,))
        if permute == 0:
            narr[0] = arr[0]
            narr[1] = arr[1]
            narr[2] = arr[2]    
        elif permute == 1:
            narr[0] = arr[0]
            narr[1] = arr[2]
            narr[2] = arr[1]    
        elif permute == 2:
            narr[0] = arr[1]
            narr[1] = arr[0]
            narr[2] = arr[2]    
        elif permute == 3:
            narr[0] = arr[1]
            narr[1] = arr[2]
            narr[2] = arr[0]    
        elif permute == 4:
            narr[0] = arr[2]
            narr[1] = arr[0]
            narr[2] = arr[1]    
        elif permute == 5:
            narr[0] = arr[2]
            narr[1] = arr[1]
            narr[2] = arr[0]
        return narr    

    @classmethod
    def negate(cls, array, bits:int=8):
        array = np.bitwise_xor(array, (2**bits) - 1)
        return array                                                                                              