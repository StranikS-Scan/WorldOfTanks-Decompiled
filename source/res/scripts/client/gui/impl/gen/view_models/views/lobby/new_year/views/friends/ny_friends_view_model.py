# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/friends/ny_friends_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_resource_box_model import NyWidgetResourceBoxModel
from gui.impl.gen.view_models.views.lobby.new_year.views.friends.friend_model import FriendModel

class LoadingState(IntEnum):
    PENDING = 1
    LOADED = 2
    FAILURE = 3


class NyFriendsViewModel(ViewModel):
    __slots__ = ('onGoToFriend', 'onChooseBestFriend', 'onDeleteBestFriend', 'onBannerChangeDisplay')

    def __init__(self, properties=7, commands=4):
        super(NyFriendsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def resourceBoxModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getResourceBoxModelType():
        return NyWidgetResourceBoxModel

    def getFriends(self):
        return self._getArray(1)

    def setFriends(self, value):
        self._setArray(1, value)

    @staticmethod
    def getFriendsType():
        return FriendModel

    def getBestFriends(self):
        return self._getArray(2)

    def setBestFriends(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBestFriendsType():
        return int

    def getTotalFriendsCount(self):
        return self._getNumber(3)

    def setTotalFriendsCount(self, value):
        self._setNumber(3, value)

    def getShowBanner(self):
        return self._getBool(4)

    def setShowBanner(self, value):
        self._setBool(4, value)

    def getFriendListLoadingState(self):
        return LoadingState(self._getNumber(5))

    def setFriendListLoadingState(self, value):
        self._setNumber(5, value.value)

    def getRealm(self):
        return self._getString(6)

    def setRealm(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(NyFriendsViewModel, self)._initialize()
        self._addViewModelProperty('resourceBoxModel', NyWidgetResourceBoxModel())
        self._addArrayProperty('friends', Array())
        self._addArrayProperty('bestFriends', Array())
        self._addNumberProperty('totalFriendsCount', 0)
        self._addBoolProperty('showBanner', False)
        self._addNumberProperty('friendListLoadingState')
        self._addStringProperty('realm', '')
        self.onGoToFriend = self._addCommand('onGoToFriend')
        self.onChooseBestFriend = self._addCommand('onChooseBestFriend')
        self.onDeleteBestFriend = self._addCommand('onDeleteBestFriend')
        self.onBannerChangeDisplay = self._addCommand('onBannerChangeDisplay')
