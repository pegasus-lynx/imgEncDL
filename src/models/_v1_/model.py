import torch.nn as nn

class ShakeDropResNet(nn.Module):

    def __init__(self, channels, init_block_channels, bottleneck, 
                life_probs, in_channels:int=3, in_size=(32, 32), 
                num_classes:int=10):
        super(ShakeDropResNet, self).__init__()
        self.in_size = in_size
        self.num_classes = num_classes

        self.features = nn.Sequential()
        self.features.add_module("init_block", )

        in_channels = init_block_channels
        k = 0
        for i, channels_per_stage in enumerate(channels):
            stage = nn.Sequential()
            for j, out_channels in enumerate(channels_per_stage):
                stride = 2 if (j == 0) and (i != 0) else 1
                stage.add_module(f"unit{j+1}", ShakeDropResUnit(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    stride=stride, 
                    bottleneck=bottleneck,
                    life_prob=life_probs[k]))
                in_channels = out_channels
                k += 1
            self.features.add_module(f"stage{i+1}", stage)
        
        self.features.add_module("final_pool", nn.AvgPool2d(
            kernel_size=8, stride=1))

        self.output = nn.Linear(in_features=in_channels, out_features=num_classes)

        self._init_params()

    def _init_params(self):
        for name, module in self.named_modules():
            if isinstance(module, nn.Conv2d):
                init.kaiming_uniform_(module.weight)
                if module.bias is not None:
                    init.constant_(module.bias, 0)

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.output(x)
        return x