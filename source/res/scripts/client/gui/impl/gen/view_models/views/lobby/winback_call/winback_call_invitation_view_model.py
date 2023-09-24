# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_invitation_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_base import WinbackCallFriendBase

class WinbackCallInvitationViewModel(ViewModel):
    __slots__ = ('onClose', 'onSend')
    ARG_DATABASE_ID = 'databaseID'

    def __init__(self, properties=1, commands=2):
        super(WinbackCallInvitationViewModel, self).__init__(properties=properties, commands=commands)

    def getFriends(self):
        return self._getArray(0)

    def setFriends(self, value):
        self._setArray(0, value)

    @staticmethod
    def getFriendsType():
        return WinbackCallFriendBase

    def _initialize(self):
        super(WinbackCallInvitationViewModel, self)._initialize()
        self._addArrayProperty('friends', Array())
        self.onClose = self._addCommand('onClose')
        self.onSend = self._addCommand('onSend')
