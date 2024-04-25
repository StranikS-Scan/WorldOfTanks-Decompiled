# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/battle_mode_widget_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_mode_model import BattleModeModel

class DisableReason(Enum):
    NOTPLATOONLEADER = 'notPlatoonLeader'
    PLATOONSEARCHINPROGRESS = 'platoonSearchInProgress'


class BattleModeWidgetModel(ViewModel):
    __slots__ = ('onBattleModeChanged',)

    def __init__(self, properties=6, commands=1):
        super(BattleModeWidgetModel, self).__init__(properties=properties, commands=commands)

    def getSelectedMode(self):
        return self._getString(0)

    def setSelectedMode(self, value):
        self._setString(0, value)

    def getIsSelectedModeAvailable(self):
        return self._getBool(1)

    def setIsSelectedModeAvailable(self, value):
        self._setBool(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getDisableReason(self):
        return DisableReason(self._getString(3))

    def setDisableReason(self, value):
        self._setString(3, value.value)

    def getBattleModes(self):
        return self._getArray(4)

    def setBattleModes(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBattleModesType():
        return BattleModeModel

    def getCanShowAnimation(self):
        return self._getBool(5)

    def setCanShowAnimation(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BattleModeWidgetModel, self)._initialize()
        self._addStringProperty('selectedMode', '')
        self._addBoolProperty('isSelectedModeAvailable', False)
        self._addBoolProperty('isDisabled', False)
        self._addStringProperty('disableReason')
        self._addArrayProperty('battleModes', Array())
        self._addBoolProperty('canShowAnimation', False)
        self.onBattleModeChanged = self._addCommand('onBattleModeChanged')
