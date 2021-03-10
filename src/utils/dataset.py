from skimage import io as imgio
from skimage.viewer import ImageViewer
import numpy as np
import pickle
from pathlib import Path
from typing import Union, Dict, List, Tuple

class Dataset(object):
    
    def __init__(self, name:str='irec', img_size:Tuple[int]=(), label_names:List[str]=[]):
        self.name = name
        self.images = []
        self.labels = []
        
        self.image_size = ()
        self.label_names = []

    def __len__(self):
        return len(self.images)

    def __iter__(self):
        for p in range(len(self)):
            img, label = self._get_row(p)
            yield (img, label)

    def append(self, img, label:Union[str,int]):
        if not isinstance(img, Image):
            img = Image.load(img)
        if isinstance(label, str):
            lebel = self._get_label(label)
        self.images.append(img)
        self.labels.append(label)

    def add(self, dataset):
        for row in dataset:
            img, label = row
            self.append(img, label)

    def _get_label(self, label:str):
        for p, x in enumerate(self.label_names):
            if x == label:
                return p
        return 0

    def _get_label_name(self, img_cls:int):
        if len(self.label_names) <= img_cls:
            return None
        return self.label_names[img_cls]

    def _get_row(self, index:int):
        img = self.images[index] if index < len(self) else Image()
        img_cls = self.labels[index] if index < len(self.labels) else 0
        return (img, img_cls)

class Image(object):
    def __init__(self, filepath:Path=None, nparray=None):
        self.filepath = filepath
        self.array = nparray
        self.transforms = []
        if filepath and not nparray:
            self._read()

    def shape(self):
        if self.array:
            return self.array.shape
        return ()

    def _read(self):
        self.array = imgio.imread(fname=self.filepath)        

    def view(self):
        viewer = ImageViewer(self.array)
        viewer.show()

    @classmethod
    def load(cls, img):
        if isinstance(img, str):
            img = Path(img)
        if isinstance(img, Path):
            return Image(filepath=img)
        if isinstance(img, np.ndarray):
            return Image(nparray=img)

    @classmethod
    def save(cls, img, save_path:Path=None):
        if not save_path:
            save_path = img.filepath
        imgio.imsave(fname=save_path, arr=img.array)

    def rescale(self, scale_factor:float=1.0):
        self.transforms.append(f'rescale {scale_factor}')
        self.array = rescale(self.array, scale_factor, anti_aliasing=False)

    def resize(self, shape:Tuple[int]):
        self.transforms.append(f'resize {shape}')
        self.array = resize(self.array, shape, anti_aliasing=True)

    def downscale(self, downscale_factor:Tuple[int]):
        self.transforms.append(f'downscale {downscale_factor}')
        self.array = downscale_local_mean(self.array, downscale_factor)

    def togray(self):
        self.transforms.append('togray')
        self.array = color.rgb2gray(self.array)
