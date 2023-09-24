# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_friend_base.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_status import WinbackCallFriendStatus

class WinbackCallFriendBase(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WinbackCallFriendBase, self).__init__(properties=properties, commands=commands)

    @property
    def status(self):
        return self._getViewModel(0)

    @staticmethod
    def getStatusType():
        return WinbackCallFriendStatus

    def getDatabaseID(self):
        return self._getNumber(1)

    def setDatabaseID(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getClan(self):
        return self._getString(3)

    def setClan(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(WinbackCallFriendBase, self)._initialize()
        self._addViewModelProperty('status', WinbackCallFriendStatus())
        self._addNumberProperty('databaseID', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('clan', '')
