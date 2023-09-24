# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_main import WinbackCallFriendMain

class WinbackCallMainViewModel(ViewModel):
    __slots__ = ('onCopyLink', 'onOpenSubmissionForm')
    FRIEND_VEHICLE_TOOLTIP_ID = 'friendVehicleTooltip'

    def __init__(self, properties=8, commands=2):
        super(WinbackCallMainViewModel, self).__init__(properties=properties, commands=commands)

    def getEventStart(self):
        return self._getNumber(0)

    def setEventStart(self, value):
        self._setNumber(0, value)

    def getEventFinish(self):
        return self._getNumber(1)

    def setEventFinish(self, value):
        self._setNumber(1, value)

    def getIsLinkCopied(self):
        return self._getBool(2)

    def setIsLinkCopied(self, value):
        self._setBool(2, value)

    def getCanSendInvite(self):
        return self._getBool(3)

    def setCanSendInvite(self, value):
        self._setBool(3, value)

    def getFriendsBack(self):
        return self._getNumber(4)

    def setFriendsBack(self, value):
        self._setNumber(4, value)

    def getIsRewardsReceived(self):
        return self._getBool(5)

    def setIsRewardsReceived(self, value):
        self._setBool(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getFriends(self):
        return self._getArray(7)

    def setFriends(self, value):
        self._setArray(7, value)

    @staticmethod
    def getFriendsType():
        return WinbackCallFriendMain

    def _initialize(self):
        super(WinbackCallMainViewModel, self)._initialize()
        self._addNumberProperty('eventStart', 0)
        self._addNumberProperty('eventFinish', 0)
        self._addBoolProperty('isLinkCopied', False)
        self._addBoolProperty('canSendInvite', True)
        self._addNumberProperty('friendsBack', 0)
        self._addBoolProperty('isRewardsReceived', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('friends', Array())
        self.onCopyLink = self._addCommand('onCopyLink')
        self.onOpenSubmissionForm = self._addCommand('onOpenSubmissionForm')
