# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/perk_short_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_base_model import PerkBaseModel

class PerkShortModel(PerkBaseModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PerkShortModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(3)

    def setPoints(self, value):
        self._setNumber(3, value)

    def getMaxPoints(self):
        return self._getNumber(4)

    def setMaxPoints(self, value):
        self._setNumber(4, value)

    def getInstructorPoints(self):
        return self._getNumber(5)

    def setInstructorPoints(self, value):
        self._setNumber(5, value)

    def getBoosterPoints(self):
        return self._getNumber(6)

    def setBoosterPoints(self, value):
        self._setNumber(6, value)

    def getInstructorsAmount(self):
        return self._getNumber(7)

    def setInstructorsAmount(self, value):
        self._setNumber(7, value)

    def getIsOvercapped(self):
        return self._getBool(8)

    def setIsOvercapped(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(PerkShortModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addNumberProperty('instructorPoints', 0)
        self._addNumberProperty('boosterPoints', 0)
        self._addNumberProperty('instructorsAmount', 0)
        self._addBoolProperty('isOvercapped', False)
