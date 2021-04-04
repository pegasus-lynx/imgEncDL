
import chainer.functions as F
import chainer.links import L
from chainer import Chain
from functools import partial
from chainer.serializer import load_npz

class ResBlock(Chain):
    
    def __init__(self, in_channels, out_channels, stride, 
                use_bias:bool=False, use_bn:bool=True):
        super(ResBlock, self).__init__()
        with self.init_scope():
            self.conv1 = None
            self.conv2 = None

    def __call__(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        return x


class ResBottleneck(Chain):
    
    def __init__(self, in_channels, out_channels, stride, pad:int=1,
                dilate:int=1, conv1_stride=False, bottleneck_factor=4):
        super(ResBottleneck, self).__init__()
        mid_channels = out_channels // bottleneck_factor
        