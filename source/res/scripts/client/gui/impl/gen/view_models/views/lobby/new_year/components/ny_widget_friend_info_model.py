# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_widget_friend_info_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class UserStatus(Enum):
    OFFLINE = 'Offline'
    ONLINE = 'Online'


class NyWidgetFriendInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(NyWidgetFriendInfoModel, self).__init__(properties=properties, commands=commands)

    def getIsShow(self):
        return self._getBool(0)

    def setIsShow(self, value):
        self._setBool(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getNickname(self):
        return self._getString(2)

    def setNickname(self, value):
        self._setString(2, value)

    def getServerName(self):
        return self._getString(3)

    def setServerName(self, value):
        self._setString(3, value)

    def getUserStatus(self):
        return UserStatus(self._getString(4))

    def setUserStatus(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(NyWidgetFriendInfoModel, self)._initialize()
        self._addBoolProperty('isShow', False)
        self._addNumberProperty('id', 0)
        self._addStringProperty('nickname', '')
        self._addStringProperty('serverName', '')
        self._addStringProperty('userStatus', UserStatus.OFFLINE.value)
