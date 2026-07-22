# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/players_list_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.player_info_model import PlayerInfoModel

class PlayersListTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PlayersListTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsAllNamesLoaded(self):
        return self._getBool(0)

    def setIsAllNamesLoaded(self, value):
        self._setBool(0, value)

    def getPlayersCount(self):
        return self._getNumber(1)

    def setPlayersCount(self, value):
        self._setNumber(1, value)

    def getPlayers(self):
        return self._getArray(2)

    def setPlayers(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPlayersType():
        return PlayerInfoModel

    def _initialize(self):
        super(PlayersListTooltipModel, self)._initialize()
        self._addBoolProperty('isAllNamesLoaded', True)
        self._addNumberProperty('playersCount', 0)
        self._addArrayProperty('players', Array())
