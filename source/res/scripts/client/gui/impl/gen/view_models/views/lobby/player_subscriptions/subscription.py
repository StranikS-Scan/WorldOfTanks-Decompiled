# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/player_subscriptions/subscription.py
from frameworks.wulf import ViewModel

class Subscription(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(Subscription, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getImageUriSmall(self):
        return self._getString(3)

    def setImageUriSmall(self, value):
        self._setString(3, value)

    def getHas3rdPartyRewardsToClaim(self):
        return self._getBool(4)

    def setHas3rdPartyRewardsToClaim(self, value):
        self._setBool(4, value)

    def getHasDepotRewardsToClaim(self):
        return self._getBool(5)

    def setHasDepotRewardsToClaim(self, value):
        self._setBool(5, value)

    def getImageUriMedium(self):
        return self._getString(6)

    def setImageUriMedium(self, value):
        self._setString(6, value)

    def getImageUriLarge(self):
        return self._getString(7)

    def setImageUriLarge(self, value):
        self._setString(7, value)

    def getRefreshTime(self):
        return self._getNumber(8)

    def setRefreshTime(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(Subscription, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('imageUriSmall', '')
        self._addBoolProperty('has3rdPartyRewardsToClaim', True)
        self._addBoolProperty('hasDepotRewardsToClaim', True)
        self._addStringProperty('imageUriMedium', '')
        self._addStringProperty('imageUriLarge', '')
        self._addNumberProperty('refreshTime', 0)
