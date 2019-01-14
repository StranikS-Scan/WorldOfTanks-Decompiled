# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/__init__.py
from gui.impl.gen_utils import DynAccessor
from .animations import Animations
from .areas import Areas
from .atlases import Atlases
from .entries import Entries
from .images import Images
from .sounds import Sounds
from .strings import Strings
from .styles import Styles
from .videos import Videos
from .views import Views

class Resources(object):
    __slots__ = ()
    invalid = DynAccessor(0)
    animations = Animations()
    areas = Areas()
    atlases = Atlases()
    entries = Entries()
    images = Images()
    sounds = Sounds()
    strings = Strings()
    styles = Styles()
    videos = Videos()
    views = Views()


R = Resources()
