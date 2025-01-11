# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quests_page_tab_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TabState(Enum):
    DISABLED = 'disabled'
    ISAVAILABLE = 'isAvailable'
    COMPLETEWITHHONOR = 'completeWithHonor'
    COMPLETED = 'completed'


class Pm3QuestsPageTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(Pm3QuestsPageTabModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def getMaxValue(self):
        return self._getNumber(2)

    def setMaxValue(self, value):
        self._setNumber(2, value)

    def getMinVehicleLevel(self):
        return self._getNumber(3)

    def setMinVehicleLevel(self, value):
        self._setNumber(3, value)

    def getMaxVehicleLevel(self):
        return self._getNumber(4)

    def setMaxVehicleLevel(self, value):
        self._setNumber(4, value)

    def getSelected(self):
        return self._getBool(5)

    def setSelected(self, value):
        self._setBool(5, value)

    def getState(self):
        return TabState(self._getString(6))

    def setState(self, value):
        self._setString(6, value.value)

    def getBranchName(self):
        return self._getString(7)

    def setBranchName(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(Pm3QuestsPageTabModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('value', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('minVehicleLevel', 0)
        self._addNumberProperty('maxVehicleLevel', 0)
        self._addBoolProperty('selected', False)
        self._addStringProperty('state')
        self._addStringProperty('branchName', '')
