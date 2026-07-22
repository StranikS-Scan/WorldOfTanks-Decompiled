# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/user_item.py
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.common.player_online_status_model import PlayerOnlineStatusModel

class UserItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(UserItem, self).__init__(properties=properties, commands=commands)

    @property
    def playerOnlineStatus(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayerOnlineStatusType():
        return PlayerOnlineStatusModel

    def getUserID(self):
        return self._getNumber(1)

    def setUserID(self, value):
        self._setNumber(1, value)

    def getUserNickName(self):
        return self._getString(2)

    def setUserNickName(self, value):
        self._setString(2, value)

    def getClanTag(self):
        return self._getString(3)

    def setClanTag(self, value):
        self._setString(3, value)

    def getIsWaitResponse(self):
        return self._getBool(4)

    def setIsWaitResponse(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(UserItem, self)._initialize()
        self._addViewModelProperty('playerOnlineStatus', PlayerOnlineStatusModel())
        self._addNumberProperty('userID', 0)
        self._addStringProperty('userNickName', '')
        self._addStringProperty('clanTag', '')
        self._addBoolProperty('isWaitResponse', False)
