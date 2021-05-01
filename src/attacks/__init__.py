from src import Filepath

from src.schemes.etc import EtCScheme
from src.schemes.tanaka import TanakaScheme
from src.schemes.skk import SkkScheme

class AttackRegistry(object):
    attacks = ['skk_basic_co', 'skk_plaintext']

class AttackFactory(object):

    @classmethod
    def get_attack():
        pass