# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_friend_vehicle.py
from frameworks.wulf import ViewModel

class WinbackCallFriendVehicle(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WinbackCallFriendVehicle, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getIsElite(self):
        return self._getBool(3)

    def setIsElite(self, value):
        self._setBool(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getNation(self):
        return self._getString(6)

    def setNation(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(WinbackCallFriendVehicle, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('isElite', False)
        self._addStringProperty('type', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('nation', '')
