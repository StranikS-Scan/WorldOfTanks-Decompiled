# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/catalog/rewards_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class DogTagType(IntEnum):
    ENGRAVING = 0
    BACKGROUND = 1


class RewardsModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(RewardsModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(9)

    def setId(self, value):
        self._setNumber(9, value)

    def getPurpose(self):
        return self._getString(10)

    def setPurpose(self, value):
        self._setString(10, value)

    def getDogTagType(self):
        return DogTagType(self._getNumber(11))

    def setDogTagType(self, value):
        self._setNumber(11, value.value)

    def getBackgroundId(self):
        return self._getNumber(12)

    def setBackgroundId(self, value):
        self._setNumber(12, value)

    def getEngravingId(self):
        return self._getNumber(13)

    def setEngravingId(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(RewardsModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('purpose', '')
        self._addNumberProperty('dogTagType')
        self._addNumberProperty('backgroundId', 0)
        self._addNumberProperty('engravingId', 0)
