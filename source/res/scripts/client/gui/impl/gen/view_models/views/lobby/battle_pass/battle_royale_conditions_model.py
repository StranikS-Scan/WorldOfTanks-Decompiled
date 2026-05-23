# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_royale_conditions_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_rows_model import GameModeRowsModel

class BattleRoyaleConditionsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleRoyaleConditionsModel, self).__init__(properties=properties, commands=commands)

    def getSolo(self):
        return self._getArray(0)

    def setSolo(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSoloType():
        return GameModeRowsModel

    def getSquad(self):
        return self._getArray(1)

    def setSquad(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSquadType():
        return GameModeRowsModel

    def _initialize(self):
        super(BattleRoyaleConditionsModel, self)._initialize()
        self._addArrayProperty('solo', Array())
        self._addArrayProperty('squad', Array())
