
class AbstractScheme(object):

    def __init__(self, name:str):
        self.name = name

    def encrypt(self):
        pass

    def decrypt(self):
        pass

    def save(self):
        pass

    def read(self):
        pass