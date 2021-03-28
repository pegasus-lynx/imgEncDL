import numpy as np
from typing import Union
from .abstract import AbstractScheme
from copy import deepcopy
import math
from itertools import permutations,product
from ..utils.dataset import Image
from tqdm import tqdm
class SkkScheme(AbstractScheme):
    def __init__(self,key:Union[int,None]):
        self.name='skk'
        if isinstance(key,int):
            self.key=key
    def encrypt(self,img,key:Union[int,None]):
        if isinstance(key,int):
            np.random.seed(key)
        elif hasattr(self,'key'):
            np.random.seed(self.key)
        else:
            raise Exception("no key provided")
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
        return Image(filepath=img.filepath.with_suffix('.skk.jpeg'), nparray=arr)
    def decrypt(self,img,key:Union[int,None]):
        if isinstance(key,int):
            np.random.seed(key)
        elif hasattr(self,'key'):
            np.random.seed(self.key)
        else:
            raise Exception("no key provided")
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
