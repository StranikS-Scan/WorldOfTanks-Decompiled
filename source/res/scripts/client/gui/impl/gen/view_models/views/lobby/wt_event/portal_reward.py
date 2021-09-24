# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/portal_reward.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TooltipType(Enum):
    HUNTER_COLLECTION = 'hunterCollection'
    STYLE_3D = 'randomStyle3d'
    DEFAULT = 'default'


class PortalReward(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PortalReward, self).__init__(properties=properties, commands=commands)

    def getTooltipType(self):
        return TooltipType(self._getString(0))

    def setTooltipType(self, value):
        self._setString(0, value.value)

    def getIndex(self):
        return self._getNumber(1)

    def setIndex(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsCollected(self):
        return self._getBool(3)

    def setIsCollected(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PortalReward, self)._initialize()
        self._addStringProperty('tooltipType')
        self._addNumberProperty('index', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isCollected', False)
