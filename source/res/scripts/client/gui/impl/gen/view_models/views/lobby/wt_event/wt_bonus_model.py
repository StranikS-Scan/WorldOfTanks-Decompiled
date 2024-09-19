# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class TypeIcon(Enum):
    PROJECTIONDECAL = 'projectionDecal'
    STYLE = 'style'
    DECAL = 'decal'
    CAMOUFLAGE = 'camouflage'
    EMBLEM = 'emblem'
    INSCRIPTION = 'inscription'


class WtBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(WtBonusModel, self).__init__(properties=properties, commands=commands)

    def getSpecialId(self):
        return self._getNumber(9)

    def setSpecialId(self, value):
        self._setNumber(9, value)

    def getTypeIcon(self):
        return TypeIcon(self._getString(10))

    def setTypeIcon(self, value):
        self._setString(10, value.value)

    def _initialize(self):
        super(WtBonusModel, self)._initialize()
        self._addNumberProperty('specialId', 0)
        self._addStringProperty('typeIcon')
