# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/comp7_bonus_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class DogTagType(IntEnum):
    ENGRAVING = 0
    BACKGROUND = 1


class Comp7BonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(Comp7BonusModel, self).__init__(properties=properties, commands=commands)

    def getDogTagType(self):
        return DogTagType(self._getNumber(8))

    def setDogTagType(self, value):
        self._setNumber(8, value.value)

    def getIsPeriodic(self):
        return self._getBool(9)

    def setIsPeriodic(self, value):
        self._setBool(9, value)

    def getOverlayType(self):
        return self._getString(10)

    def setOverlayType(self, value):
        self._setString(10, value)

    def getItem(self):
        return self._getString(11)

    def setItem(self, value):
        self._setString(11, value)

    def getGroupName(self):
        return self._getString(12)

    def setGroupName(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(Comp7BonusModel, self)._initialize()
        self._addNumberProperty('dogTagType')
        self._addBoolProperty('isPeriodic', False)
        self._addStringProperty('overlayType', '')
        self._addStringProperty('item', '')
        self._addStringProperty('groupName', '')
