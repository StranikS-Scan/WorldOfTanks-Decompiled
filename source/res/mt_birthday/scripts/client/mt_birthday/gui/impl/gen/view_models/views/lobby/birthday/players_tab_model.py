# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/players_tab_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.player_model import PlayerModel

class PlayersTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PlayersTabModel, self).__init__(properties=properties, commands=commands)

    def getPlayersToSelect(self):
        return self._getArray(0)

    def setPlayersToSelect(self, value):
        self._setArray(0, value)

    @staticmethod
    def getPlayersToSelectType():
        return PlayerModel

    def getIsLoaded(self):
        return self._getBool(1)

    def setIsLoaded(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PlayersTabModel, self)._initialize()
        self._addArrayProperty('playersToSelect', Array())
        self._addBoolProperty('isLoaded', False)
