from src.utils.dataset import Image, Dataset
import random
from src.utils.functionals import Converter as Cr

class DataLoader(object):

    def __init__(self, dataset, batch_size:int, shuffle:bool=False, gpu:int=-1):
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.dataset = dataset
        self.permutation = list(range(len(dataset)))

        if shuffle:
            self.shuffle = True
            self.permutation = self._permute()
        self.gpu = gpu

    def __len__(self):
        try:
            return len(self.dataset) // self.batch_size
        except Exception:
            return 0

    def __iter__(self):
        images, classes = [], []
        curr = 0
        for p in self.permutation:
            if curr == self.batch_size:
                # print(len(images), images[0].shape)
                img_tensor = Cr.list2tensor(images, dtype='float', gpu=self.gpu)
                cls_tensor = Cr.list2tensor(classes, gpu=self.gpu)
                yield (img_tensor, cls_tensor)
                curr = 0
                images, classes = [], []        
            img, label = self.dataset._get_row(p)
            images.append(img.array)
            classes.append(label)
            curr += 1
        if curr != 0:
            img_tensor = Cr.list2tensor(imgs, dtype='float', gpu=self.gpu)
            cls_tensor = Cr.list2tensor(classes, gpu=self.gpu)
            yield (imgs, classes)

    def _permute(self):
        permutation = random.sample([x for x in range(len(self.dataset))], len(self.dataset))
        return permutation

    def normalize(self, means, stds):
        pass