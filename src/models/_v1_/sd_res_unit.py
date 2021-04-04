
import os
import torch
import torch.nn as nn
import torch.nn.init as init

class ShakeDrop(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, b, alpha):
        y = (b + alpha - b*alpha) * x
        ctx.save_for_backward(b)
        return y

    @staticmethod
    def backward(ctx, dy):
        beta = torch.rand(dy.size(0), dtype=dy.dtype, device=dy.device).view(-1,1,1,1)
        b, _ = ctx.saved_tensors
        return (b + beta - b*beta) * dy, None, None

class ShakeDropResUnit(nn.Module):

    def __init__(self, in_channels, out_channels,
                stride, bottleneck, life_prob):
        super(ShakeDropResUnit, self).__init__()
        self.life_prob = life_prob
        self.resize_identity = (in_channels != out_channels) or (stride != 1)
        body_class = ResBottleneck if bottleneck else ResBlock

        self.body = body_class(in_channels=in_channels,
                                out_channels=out_channels,
                                stride=stride)
        if self.resize_identity:
            self.identity_conv = None

        self.activ = nn.ReLU(inplace=True)
        self.shake_drop = ShakeDrop.apply

    def forward(self, x):
        if self.resize_identity:
            identity = self.identity_conv(x)
        else:
            identity = x
        x = self.body(x)
        if self.training:
            b = torch.bernoulli(torch.full((1,), self.life_prob, dtype=x.dtype, device=x.device))
            alpha = torch.empty(x.size(0), dtype=x.dtype, device=x.device).view(-1,1,1,1).uniform_(-1.0,1.0)
            x = self.shake_drop(x, b, alpha)
        else:
            x = self.life_prob * x
        x = x + identity
        x = self.activ(x)
        return x