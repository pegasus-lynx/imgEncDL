from skimage import color
from skimage import rescale, resize, downscale_local_mean
from typing import Tuple

class Transformer():
    
    @classmethod
    def rescale(cls, img, scale_factor:float=1.0):
        img.array = rescale(img.array, scale_factor, anti_aliasing=False)
        return img

    @classmethod
    def resize(cls, img, shape:Tuple[int]):
        img.array = resize(img.array, shape, anti_aliasing=True)
        return img

    @classmethod
    def downscale(cls, img, downscale_factor:Tuple[int]):
        img.array = downscale_local_mean(img.array, downscale_factor)
        return img

    @classmethod
    def togray(cls, img):
        img.array = color.rgb2gray(img.array)
        return img