# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_friend_status.py
from enum import Enum
from frameworks.wulf import ViewModel

class WinBackCallFriendState(Enum):
    UNDEFINED = 'UNDEFINED'
    HAS_NOT_EMAIL = 'HAS_NOT_EMAIL'
    NOT_SENT = 'NOT_SENT'
    IN_PROGRESS = 'IN_PROGRESS'
    ANOTHER_CALLER_IN_PROGRESS = 'ANOTHER_CALLER_IN_PROGRESS'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    ACCEPT_BY_ANOTHER = 'ACCEPT_BY_ANOTHER'
    ANOTHER_CALLER_ACCEPTED = 'ANOTHER_CALLER_ACCEPTED'
    ROLLED_BACK = 'ROLLED_BACK'


class WinbackCallFriendStatus(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WinbackCallFriendStatus, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return WinBackCallFriendState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getStatus(self):
        return self._getString(1)

    def setStatus(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(WinbackCallFriendStatus, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('status', '')
