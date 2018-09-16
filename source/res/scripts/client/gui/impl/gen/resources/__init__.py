# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/__init__.py
from .atlases import Atlases
from .images import Images
from .sounds import Sounds
from .strings import Strings
from .views import Views

class Resources(object):
    __slots__ = ('__atlases', '__images', '__sounds', '__strings', '__views')

    def __init__(self):
        super(Resources, self).__init__()
        self.__atlases = Atlases()
        self.__images = Images()
        self.__sounds = Sounds()
        self.__strings = Strings()
        self.__views = Views()

    @property
    def atlases(self):
        return self.__atlases

    @property
    def images(self):
        return self.__images

    @property
    def sounds(self):
        return self.__sounds

    @property
    def strings(self):
        return self.__strings

    @property
    def views(self):
        return self.__views


R = Resources()
