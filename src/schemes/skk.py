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
class SkkScheme(AbstractScheme):
    def __init__(self):
        self.name='skk'
        self.key=np.random.randint(0,(1<<32))

    def encrypt(self,img):
        np.random.seed(self.key)
        n=len(img.array)
        m=len(img.array[0])
        flip=np.random.randint(0,8,n*m)
        permute=np.random.randint(0,6,n*m)
        arr=deepcopy(img.array)
        for i,j in product(range(n),range(m)):
            xr=flip[i+j*n]&4!=0
            xg=flip[i+j*n]&2!=0
            xb=flip[i+j*n]&1!=0
            xs=permute[i+j*n]
            if xr:
                arr[i][j][0]=255^(arr[i][j][0])
            if xg:
                arr[i][j][1]=255^(arr[i][j][1])
            if xb:
                arr[i][j][2]=255^(arr[i][j][2])
            arr[i][j]=np.array(list(permutations(arr[i][j]))[xs])
        
        suf = img.filepath.suffix
        efp = img.filepath.with_suffix(f'.skk{suf}')
        enc_img = Image(filepath=efp, nparray=arr)
        return enc_img


    def decrypt(self,img):
        np.random.seed(self.key)
        n=len(img.array)
        m=len(img.array[0])
        flip=np.random.randint(0,8,n*m)
        permute=np.random.randint(0,6,n*m)
        arr=deepcopy(img.array)
        for i,j in product(range(n),range(m)):
            xr=flip[i+j*n]&4!=0
            xg=flip[i+j*n]&2!=0
            xb=flip[i+j*n]&1!=0
            xs=permute[i+j*n]
            l=list(permutations(arr[i][j]))
            for k in l:
                if list(permutations(k))[xs]==l[0]:
                    arr[i][j]=np.array(k)
                    break
            if xr:
                arr[i][j][0]=255^(arr[i][j][0])
            if xg:
                arr[i][j][1]=255^(arr[i][j][1])
            if xb:
                arr[i][j][2]=255^(arr[i][j][2])
        return Image(nparray=arr)

    def save(self,work_dir):
        data={
            'name':self.name,
            'key':self.key
        }
        pickle.dump(data,work_dir / Path(f'{self.name}.scheme.file'))
        
    @classmethod
    def load(cls,load_file):
        data=_load_file(load_file)
        scheme=cls()
        scheme.key=data[b'key']
        
