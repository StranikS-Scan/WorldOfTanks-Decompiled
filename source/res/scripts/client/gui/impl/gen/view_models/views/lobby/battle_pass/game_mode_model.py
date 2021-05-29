# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/game_mode_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_card_model import GameModeCardModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_rows_model import GameModeRowsModel

class ArenaBonusType(IntEnum):
    REGULAR = 1
    RANKED = 22
    BATTLE_ROYALE_SOLO = 29
    EPIC_BATTLE = 27


class GameModeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(GameModeModel, self).__init__(properties=properties, commands=commands)

    @property
    def tableRows(self):
        return self._getViewModel(0)

    @property
    def cards(self):
        return self._getViewModel(1)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def getText(self):
        return self._getString(3)

    def setText(self, value):
        self._setString(3, value)

    def getArenaBonusType(self):
        return ArenaBonusType(self._getNumber(4))

    def setArenaBonusType(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(GameModeModel, self)._initialize()
        self._addViewModelProperty('tableRows', UserListModel())
        self._addViewModelProperty('cards', UserListModel())
        self._addStringProperty('title', '')
        self._addStringProperty('text', '')
        self._addNumberProperty('arenaBonusType')
