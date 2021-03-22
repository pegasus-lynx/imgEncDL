from typing import List, Union
import random
import numpy as np

class RandomGen(object):

    @classmethod
    def permutation(cls, n:int):
        return np.array(random.sample([x for x in range(n)], n))

    @classmethod
    def choicelist(cls, n:int, choices:List[Union[str,int]]):
        return np.array(random.choices(population=choices, k=n))