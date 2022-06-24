# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/game_mode_rows_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_cell_model import GameModeCellModel

class GameModeRowsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(GameModeRowsModel, self).__init__(properties=properties, commands=commands)

    @property
    def cell(self):
        return self._getViewModel(0)

    @staticmethod
    def getCellType():
        return GameModeCellModel

    def _initialize(self):
        super(GameModeRowsModel, self)._initialize()
        self._addViewModelProperty('cell', UserListModel())
