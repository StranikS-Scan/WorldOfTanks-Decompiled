# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/matrix_branch.py
import typing
from items import _xml
if typing.TYPE_CHECKING:
    import ResMgr

class PerkMatrixBranch(object):
    __slots__ = ('_id', '_index', '_ultimateThreshold', '_name', '_description', '_icon', '_maxPoints')

    def __init__(self, xmlCtx, section, maxPointsDict):
        self._id = _xml.readPositiveInt(xmlCtx, section, 'id')
        self._index = _xml.readInt(xmlCtx, section, 'index', minVal=0)
        self._ultimateThreshold = _xml.readInt(xmlCtx, section, 'ultimatesThreshold')
        self._name = _xml.readString(xmlCtx, section, 'name')
        self._description = _xml.readString(xmlCtx, section, 'description')
        self._icon = _xml.readString(xmlCtx, section, 'icon')
        self._maxPoints = maxPointsDict[self._id]

    @property
    def id(self):
        return self._id

    @property
    def index(self):
        return self._index

    @property
    def ultimate_threshold(self):
        return self._ultimateThreshold

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def icon(self):
        return self._icon

    @property
    def maxPoints(self):
        return self._maxPoints
