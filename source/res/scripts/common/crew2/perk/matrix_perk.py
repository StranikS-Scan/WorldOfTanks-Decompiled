# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/matrix_perk.py
import typing
from items import _xml
if typing.TYPE_CHECKING:
    import ResMgr

class PerkMatrixPerk(object):
    __slots__ = ('_id', '_branch', '_index', '_maxPoints', '_ultimate')

    def __init__(self, xmlCtx, section):
        self._id = _xml.readPositiveInt(xmlCtx, section, 'id')
        self._branch = _xml.readPositiveInt(xmlCtx, section, 'branch')
        self._index = _xml.readInt(xmlCtx, section, 'index', minVal=0)
        self._maxPoints = section.readInt('maxPoints', 1)
        self._ultimate = section.readBool('ultimate', False)

    @property
    def id(self):
        return self._id

    @property
    def branch(self):
        return self._branch

    @property
    def index(self):
        return self._index

    @property
    def max_points(self):
        return self._maxPoints

    @property
    def ultimate(self):
        return self._ultimate
