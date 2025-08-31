# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_reward.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class TooltipType(Enum):
    STYLE_3D = 'randomStyle3d'
    STYLE_2D = 'randomStyle2d'
    DECAL = 'randomDecal'
    GROUPED = 'grouped'
    DEFAULT = 'default'


class PortalReward(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(PortalReward, self).__init__(properties=properties, commands=commands)

    def getTooltipType(self):
        return TooltipType(self._getString(8))

    def setTooltipType(self, value):
        self._setString(8, value.value)

    def getIsCollected(self):
        return self._getBool(9)

    def setIsCollected(self, value):
        self._setBool(9, value)

    def getIsCustom(self):
        return self._getBool(10)

    def setIsCustom(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(PortalReward, self)._initialize()
        self._addStringProperty('tooltipType')
        self._addBoolProperty('isCollected', False)
        self._addBoolProperty('isCustom', False)
