# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/game_mode_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_rows_model import GameModeRowsModel

class GameModeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(GameModeModel, self).__init__(properties=properties, commands=commands)

    def getTableRows(self):
        return self._getArray(0)

    def setTableRows(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTableRowsType():
        return GameModeRowsModel

    def _initialize(self):
        super(GameModeModel, self)._initialize()
        self._addArrayProperty('tableRows', Array())
