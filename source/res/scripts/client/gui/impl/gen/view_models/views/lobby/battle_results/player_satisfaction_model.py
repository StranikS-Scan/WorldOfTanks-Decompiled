# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/player_satisfaction_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PlayerSatisfactionStates(Enum):
    NONE = 'none'
    WORSE = 'worse'
    USUAL = 'usual'
    BETTER = 'better'


class PlayerSatisfactionModel(ViewModel):
    __slots__ = ('onSatisfactionRatingSelected',)

    def __init__(self, properties=2, commands=1):
        super(PlayerSatisfactionModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return PlayerSatisfactionStates(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsPlayerSatisfactionInterfaceEnabled(self):
        return self._getBool(1)

    def setIsPlayerSatisfactionInterfaceEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PlayerSatisfactionModel, self)._initialize()
        self._addStringProperty('state', PlayerSatisfactionStates.NONE.value)
        self._addBoolProperty('isPlayerSatisfactionInterfaceEnabled', False)
        self.onSatisfactionRatingSelected = self._addCommand('onSatisfactionRatingSelected')
