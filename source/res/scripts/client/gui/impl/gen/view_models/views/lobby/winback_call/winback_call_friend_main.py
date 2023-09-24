# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_friend_main.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_base import WinbackCallFriendBase
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_records import WinbackCallFriendRecords
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_vehicle import WinbackCallFriendVehicle

class WinbackCallFriendMain(WinbackCallFriendBase):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(WinbackCallFriendMain, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(4)

    @staticmethod
    def getVehicleType():
        return WinbackCallFriendVehicle

    def getRecords(self):
        return self._getArray(5)

    def setRecords(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRecordsType():
        return WinbackCallFriendRecords

    def _initialize(self):
        super(WinbackCallFriendMain, self)._initialize()
        self._addViewModelProperty('vehicle', WinbackCallFriendVehicle())
        self._addArrayProperty('records', Array())
