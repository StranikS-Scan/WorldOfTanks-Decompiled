# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/__init__.py
from .animations import Animations
from .atlases import Atlases
from .images import Images
from .sounds import Sounds
from .strings import Strings
from .styles import Styles
from .videos import Videos
from .views import Views

class Resources(object):
    __slots__ = ('__animations', '__atlases', '__images', '__sounds', '__strings', '__styles', '__videos', '__views')

    def __init__(self):
        super(Resources, self).__init__()
        self.__animations = Animations()
        self.__atlases = Atlases()
        self.__images = Images()
        self.__sounds = Sounds()
        self.__strings = Strings()
        self.__styles = Styles()
        self.__videos = Videos()
        self.__views = Views()

    @property
    def animations(self):
        return self.__animations

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
    def styles(self):
        return self.__styles

    @property
    def videos(self):
        return self.__videos

    @property
    def views(self):
        return self.__views


R = Resources()
