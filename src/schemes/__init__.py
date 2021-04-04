from .etc import EtCScheme
from .tanaka import TanakaScheme

class SchemeRegistry(object):
    schemes = ['ele', 'etc', 'tanaka', 'skk', 'skkd']

class SchemeFactory(object):
    
    @classmethod
    def get_scheme(cls, scheme:str=None, **kwargs):
        if not scheme:
            print(f'No scheme set. Specify the scheme from the \
                    following : {" ".join(SchemeRegistry.schemes)}')
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
    def validate_scheme(cls, scheme:str):
        if scheme not in SchemeRegistry.schemes:
            return False
        return True
