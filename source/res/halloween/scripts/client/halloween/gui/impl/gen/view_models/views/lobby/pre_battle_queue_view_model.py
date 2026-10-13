# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/pre_battle_queue_view_model.py
from gui.impl.gen.view_models.views.selectable_view_model import SelectableViewModel

class PreBattleQueueViewModel(SelectableViewModel):
    __slots__ = ('onExitBattle', 'onEscape')

    def __init__(self, properties=7, commands=4):
        super(PreBattleQueueViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedDifficultyLevel(self):
        return self._getNumber(0)

    def setSelectedDifficultyLevel(self, value):
        self._setNumber(0, value)

    def getIsExitButtonAvailable(self):
        return self._getBool(1)

    def setIsExitButtonAvailable(self, value):
        self._setBool(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def getTip(self):
        return self._getString(4)

    def setTip(self, value):
        self._setString(4, value)

    def getIsFirstTip(self):
        return self._getBool(5)

    def setIsFirstTip(self, value):
        self._setBool(5, value)

    def getTimerStartTime(self):
        return self._getNumber(6)

    def setTimerStartTime(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(PreBattleQueueViewModel, self)._initialize()
        self._addNumberProperty('selectedDifficultyLevel', 0)
        self._addBoolProperty('isExitButtonAvailable', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('tip', '')
        self._addBoolProperty('isFirstTip', False)
        self._addNumberProperty('timerStartTime', 0)
        self.onExitBattle = self._addCommand('onExitBattle')
        self.onEscape = self._addCommand('onEscape')
