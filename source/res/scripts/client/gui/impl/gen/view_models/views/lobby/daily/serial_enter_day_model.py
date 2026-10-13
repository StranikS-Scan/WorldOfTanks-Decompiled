# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/serial_enter_day_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class DayState(Enum):
    DISABLED = 'disabled'
    CURRENT = 'current'
    NEEDRELOGIN = 'needRelogin'
    TODAY = 'today'
    COMPLETED = 'completed'


class SerialEnterDayModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SerialEnterDayModel, self).__init__(properties=properties, commands=commands)

    def getDay(self):
        return self._getNumber(0)

    def setDay(self, value):
        self._setNumber(0, value)

    def getState(self):
        return DayState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getIsFinal(self):
        return self._getBool(2)

    def setIsFinal(self, value):
        self._setBool(2, value)

    def getBonuses(self):
        return self._getArray(3)

    def setBonuses(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBonusesType():
        return IconBonusModel

    def _initialize(self):
        super(SerialEnterDayModel, self)._initialize()
        self._addNumberProperty('day', 0)
        self._addStringProperty('state')
        self._addBoolProperty('isFinal', False)
        self._addArrayProperty('bonuses', Array())
