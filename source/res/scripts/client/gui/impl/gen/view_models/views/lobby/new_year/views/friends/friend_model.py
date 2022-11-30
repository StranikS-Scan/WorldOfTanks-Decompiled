# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/friends/friend_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_hangar_name_model import NyHangarNameModel

class UserStatus(Enum):
    OFFLINE = 'Offline'
    ONLINE = 'Online'


class FriendshipStatus(IntEnum):
    DEFAULT = 0
    BEST = 1
    YOUBEST = 2
    BOTHBEST = 4


class FriendModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(FriendModel, self).__init__(properties=properties, commands=commands)

    @property
    def hangarName(self):
        return self._getViewModel(0)

    @staticmethod
    def getHangarNameType():
        return NyHangarNameModel

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

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getLevelProgress(self):
        return self._getReal(6)

    def setLevelProgress(self, value):
        self._setReal(6, value)

    def getMaxLevelProgress(self):
        return self._getReal(7)

    def setMaxLevelProgress(self, value):
        self._setReal(7, value)

    def getAmountOfVisits(self):
        return self._getNumber(8)

    def setAmountOfVisits(self, value):
        self._setNumber(8, value)

    def getAmountOfCollectedResources(self):
        return self._getNumber(9)

    def setAmountOfCollectedResources(self, value):
        self._setNumber(9, value)

    def getFriendshipStatus(self):
        return FriendshipStatus(self._getNumber(10))

    def setFriendshipStatus(self, value):
        self._setNumber(10, value.value)

    def getIsRemoved(self):
        return self._getBool(11)

    def setIsRemoved(self, value):
        self._setBool(11, value)

    def getCanCollectResourcesTime(self):
        return self._getNumber(12)

    def setCanCollectResourcesTime(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(FriendModel, self)._initialize()
        self._addViewModelProperty('hangarName', NyHangarNameModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('nickname', '')
        self._addStringProperty('serverName', '')
        self._addStringProperty('userStatus')
        self._addNumberProperty('level', 1)
        self._addRealProperty('levelProgress', 0.0)
        self._addRealProperty('maxLevelProgress', 0.0)
        self._addNumberProperty('amountOfVisits', 0)
        self._addNumberProperty('amountOfCollectedResources', 0)
        self._addNumberProperty('friendshipStatus')
        self._addBoolProperty('isRemoved', False)
        self._addNumberProperty('canCollectResourcesTime', 0)
