# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/player_model.py
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.common.player_online_status_model import PlayerOnlineStatusModel

class PlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def playerOnlineStatus(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayerOnlineStatusType():
        return PlayerOnlineStatusModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getClanAbbrev(self):
        return self._getString(2)

    def setClanAbbrev(self, value):
        self._setString(2, value)

    def getSpaID(self):
        return self._getNumber(3)

    def setSpaID(self, value):
        self._setNumber(3, value)

    def getLocked(self):
        return self._getBool(4)

    def setLocked(self, value):
        self._setBool(4, value)

    def getIsNameLoading(self):
        return self._getBool(5)

    def setIsNameLoading(self, value):
        self._setBool(5, value)

    def getIsWaitResponse(self):
        return self._getBool(6)

    def setIsWaitResponse(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addViewModelProperty('playerOnlineStatus', PlayerOnlineStatusModel())
        self._addStringProperty('name', '')
        self._addStringProperty('clanAbbrev', '')
        self._addNumberProperty('spaID', 0)
        self._addBoolProperty('locked', False)
        self._addBoolProperty('isNameLoading', True)
        self._addBoolProperty('isWaitResponse', False)
