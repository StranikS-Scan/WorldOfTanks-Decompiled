# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/pet_stats_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PetNeed(Enum):
    FOOD = 'food'
    FUN = 'fun'
    ACTIVITY = 'activity'


class PetStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PetStatsModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return PetNeed(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getMailToOpen(self):
        return self._getNumber(1)

    def setMailToOpen(self, value):
        self._setNumber(1, value)

    def getTimeLeft(self):
        return self._getNumber(2)

    def setTimeLeft(self, value):
        self._setNumber(2, value)

    def getBonus(self):
        return self._getNumber(3)

    def setBonus(self, value):
        self._setNumber(3, value)

    def getMaxBonus(self):
        return self._getNumber(4)

    def setMaxBonus(self, value):
        self._setNumber(4, value)

    def getNextStage(self):
        return self._getNumber(5)

    def setNextStage(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PetStatsModel, self)._initialize()
        self._addStringProperty('type')
        self._addNumberProperty('mailToOpen', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('bonus', 0)
        self._addNumberProperty('maxBonus', 0)
        self._addNumberProperty('nextStage', 0)
