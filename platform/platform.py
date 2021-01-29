from .project import *

class Platform(object):

    def __init__(self, data: dict) -> None:
        self.data: dict = data
