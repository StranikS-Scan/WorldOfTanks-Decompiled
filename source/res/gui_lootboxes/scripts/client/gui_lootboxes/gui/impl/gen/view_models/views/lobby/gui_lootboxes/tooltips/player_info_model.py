# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/player_info_model.py
from frameworks.wulf import ViewModel

class PlayerInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PlayerInfoModel, self).__init__(properties=properties, commands=commands)

    def getPlayerName(self):
        return self._getString(0)

    def setPlayerName(self, value):
        self._setString(0, value)

    def getPlayerClanTag(self):
        return self._getString(1)

    def setPlayerClanTag(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PlayerInfoModel, self)._initialize()
        self._addStringProperty('playerName', '')
        self._addStringProperty('playerClanTag', '')
