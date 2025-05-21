# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/key_tooltip_view_model.py
from frameworks.wulf import ViewModel

class KeyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(KeyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getKeyCount(self):
        return self._getNumber(0)

    def setKeyCount(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getEffective(self):
        return self._getNumber(2)

    def setEffective(self, value):
        self._setNumber(2, value)

    def getMissionDaily(self):
        return self._getNumber(3)

    def setMissionDaily(self, value):
        self._setNumber(3, value)

    def getVehicleDaily(self):
        return self._getNumber(4)

    def setVehicleDaily(self, value):
        self._setNumber(4, value)

    def getIsPostBattle(self):
        return self._getBool(5)

    def setIsPostBattle(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(KeyTooltipViewModel, self)._initialize()
        self._addNumberProperty('keyCount', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('effective', 0)
        self._addNumberProperty('missionDaily', 0)
        self._addNumberProperty('vehicleDaily', 0)
        self._addBoolProperty('isPostBattle', False)
