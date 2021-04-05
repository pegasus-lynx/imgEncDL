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

    @classmethod
    def list(cls, length:int, max_val:int, min_val:int, unique:bool=True):
        num_list = []
        for _ in range(length):
            x = np.random.randint(min_val, max_val)
            if unique and x in num_list:
                continue
            num_list.append(x)
        return num_list