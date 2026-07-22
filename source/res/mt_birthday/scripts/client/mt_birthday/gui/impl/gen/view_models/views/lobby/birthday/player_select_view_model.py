# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/player_select_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.player_model import PlayerModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.players_tab_model import PlayersTabModel

class PlayerSelectViewModel(ViewModel):
    __slots__ = ('onClose', 'onConfirm')

    def __init__(self, properties=8, commands=2):
        super(PlayerSelectViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def lastFights(self):
        return self._getViewModel(0)

    @staticmethod
    def getLastFightsType():
        return PlayersTabModel

    @property
    def friends(self):
        return self._getViewModel(1)

    @staticmethod
    def getFriendsType():
        return PlayersTabModel

    @property
    def clanmates(self):
        return self._getViewModel(2)

    @staticmethod
    def getClanmatesType():
        return PlayersTabModel

    @property
    def sentResponse(self):
        return self._getViewModel(3)

    @staticmethod
    def getSentResponseType():
        return PlayersTabModel

    def getStampCount(self):
        return self._getNumber(4)

    def setStampCount(self, value):
        self._setNumber(4, value)

    def getMaxSelectedPlayers(self):
        return self._getNumber(5)

    def setMaxSelectedPlayers(self, value):
        self._setNumber(5, value)

    def getIsError(self):
        return self._getBool(6)

    def setIsError(self, value):
        self._setBool(6, value)

    def getPreviouslySelectedPlayers(self):
        return self._getArray(7)

    def setPreviouslySelectedPlayers(self, value):
        self._setArray(7, value)

    @staticmethod
    def getPreviouslySelectedPlayersType():
        return PlayerModel

    def _initialize(self):
        super(PlayerSelectViewModel, self)._initialize()
        self._addViewModelProperty('lastFights', PlayersTabModel())
        self._addViewModelProperty('friends', PlayersTabModel())
        self._addViewModelProperty('clanmates', PlayersTabModel())
        self._addViewModelProperty('sentResponse', PlayersTabModel())
        self._addNumberProperty('stampCount', 0)
        self._addNumberProperty('maxSelectedPlayers', 5)
        self._addBoolProperty('isError', False)
        self._addArrayProperty('previouslySelectedPlayers', Array())
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
