from .abstract import AbstractScheme
from ..utils.random import RandomGen
from typing import Union, Tuple
from ..utils.dataset import Image
from ..utils import _load_file
from ..utils.functionals import Transformer
import numpy as np
import pickle

from pathlib import Path

class EtCScheme(AbstractScheme):

    def __init__(self, block_shape:Union[int, Tuple[int,int]], nblocks:int):
        self.name = 'etc'
        self.nblocks = nblocks
        if isinstance(block_shape, int):
            block_shape = (block_shape, block_shape)
        self.block_shape = block_shape
        self.keys = self._generate_keys()
        print(max(self.keys['perm']))

    def _generate_keys(self, nblocks:int=None):
        keys = dict()
        keys['perm'] = RandomGen.permutation(self.nblocks)
        keys['roti'] = RandomGen.choicelist(self.nblocks, list(range(0,8)))
        keys['negi'] = RandomGen.choicelist(self.nblocks, list(range(0,2)))
        keys['chperm'] = RandomGen.choicelist(self.nblocks, list(range(0,6)))
        return keys

    def encrypt(self, img):
        blocks, shape = self._make_blocks(img.array)
        blocks = self._permute(blocks)
        blocks = self._roti(blocks)
        blocks = self._negi(blocks)
        blocks = self._shuffle_color(blocks)
        arr = self._merge_blocks(blocks, shape)
        return Image(filepath=img.filepath.with_suffix('.etc.jpeg'), nparray=arr)

    def decrypt(self, img):
        blocks, shape = self._make_blocks(img.array)
        blocks = self._rev_shuffle_color(blocks)
        blocks = self._rev_negi(blocks)
        blocks = self._rev_roti(blocks)
        blocks = self._rev_permute(blocks)
        arr = self._merge_blocks(blocks, shape)
        return Image(nparray=arr)

    def save(self, work_dir):
        data = {
            'name' : self.name,
            'nblocks' : self.nblocks,
            'block_shape' : self.block_shape,
            'keys' : self.keys 
        }
        filepath = work_dir / Path(f'{self.name}.key.file')
        with open(filepath, 'wb') as fw:
            pickle.dump(data, fw)

    @classmethod
    def load(cls, load_file):
        data = _load_file(load_file)
        scheme = cls(data[b'block_shape'], data[b'nblocks'])
        scheme.keys = data[b'keys']
        return scheme

    def _make_blocks(self, nparr):
        img_shape = nparr.shape
        bshape = self.block_shape
        
        rows = img_shape[0] // bshape[0]
        cols = img_shape[1] // bshape[1]
        shape = (rows, cols)
        
        blocks = []
        for r in range(rows):
            for c in range(cols):
                blocks.append(nparr[r*bshape[0]:(r+1)*bshape[0], c*bshape[1]:(c+1)*bshape[1], :])
        return blocks, shape        

    def _merge_blocks(self, blocks, shape):
        rows, cols = shape
        strips = []
        for r in range(rows):
            strip = np.concatenate(blocks[r*cols:(r+1)*cols], axis=1)
            strips.append(strip)
        arr = np.concatenate(strips, axis=0)
        return arr

    def _permute(self, blocks, perm=None):
        if perm is None:
            perm = self.keys['perm']
        return [blocks[p] for p in perm]

    def _roti(self, blocks):
        tblocks = []
        for key, block in zip(self.keys['roti'], blocks):
            rot, inv = key % 4, key >= 4
            block = Transformer.rotate(block, angle=rot*90)
            block = Transformer.reverse(block)
            tblocks.append(block)
        return tblocks

    def _negi(self, blocks):
        tblocks = []
        for key, block in zip(self.keys['negi'], blocks):
            if key == 1:
                block = Transformer.negate(block)
            tblocks.append(block)
        return tblocks

    def _shuffle_color(self, blocks):
        tblocks = []
        for key, block in zip(self.keys['chperm'], blocks):
            block = Transformer.channel_permute(block, permute=key)
            tblocks.append(block)
        return tblocks

    def _rev_permute(self, blocks):
        rev_perm = [0] * self.nblocks
        for ix, p in enumerate(self.keys['perm']):
            rev_perm[p] = ix
        return self._permute(blocks, rev_perm)

    def _rev_roti(self, blocks):
        tblocks = []
        for key, block in zip(self.keys['roti'], blocks):
            rot, inv = 4 - (key % 4), key >= 4
            block = Transformer.reverse(block)
            block = Transformer.rotate(block, angle=rot*90)
            tblocks.append(block)
        return tblocks

    def _rev_negi(self, blocks):
        tblocks = []
        for key, block in zip(self.keys['negi'], blocks):
            if key == 1:
                block = Transformer.negate(block)
            tblocks.append(block)
        return tblocks

    def _rev_shuffle_color(self, blocks):
        tblocks = []
        for key, block in zip(self.keys['chperm'], blocks):
            if key == 4:
                block = Transformer.channel_permute(block, permute=key)
            block = Transformer.channel_permute(block, permute=key)
            tblocks.append(block)
        return tblocks
        