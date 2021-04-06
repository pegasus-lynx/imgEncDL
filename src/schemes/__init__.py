from .etc import EtCScheme
from .tanaka import TanakaScheme
from .skk import SkkScheme
from src import Filepath

class SchemeRegistry(object):
    schemes = ['ele', 'etc', 'tanaka', 'skk', 'skkd']

class SchemeFactory(object):
    
    @classmethod
    def get_scheme(cls, scheme:str=None, **kwargs):
        if not scheme:
            print(f'No scheme set. Specify the scheme from the \
                    following : {" ".join(SchemeRegistry.schemes)}')
            return None
 
        if not cls.validate_scheme(scheme):
            print(f'Scheme {scheme} is not a valid option.')
            return None

        if scheme == 'ele':
            pass
        elif scheme == 'etc':
            assert kwargs.get('block_shape')
            assert kwargs.get('nblocks')
            return EtCScheme(kwargs.get('block_shape'), nblocks=kwargs.get('nblocks'))
        elif scheme == 'skk':
            pass
        elif scheme == 'skkd':
            pass
        elif scheme == 'tanaka':
            return TanakaScheme()

        return None

    @classmethod
    def load_scheme(cls, key_file:Filepath=None, scheme:str=None):
        if not scheme or not cls.validate_scheme(scheme):
            print(f'Scheme name {scheme} is not a valid option.')
        if not key_file.exists():
            print(f'Key file does not exist')

        if scheme == 'ele':
            pass
        elif scheme == 'etc':
            return EtCScheme.load(key_file)
        elif scheme == 'skk':
            pass
        elif scheme == 'skkd':
            pass
        elif scheme == 'tanaka':
            return TanakaScheme()

    @classmethod
    def validate_scheme(cls, scheme:str):
        if scheme not in SchemeRegistry.schemes:
            return False
        return True
