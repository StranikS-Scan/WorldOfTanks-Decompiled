# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_system/friend_model.py
from frameworks.wulf import ViewModel

class FriendModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FriendModel, self).__init__(properties=properties, commands=commands)

    def getIsGiftReceived(self):
        return self._getBool(0)

    def setIsGiftReceived(self, value):
        self._setBool(0, value)

    def getSpaID(self):
        return self._getNumber(1)

    def setSpaID(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getClanAbbrev(self):
        return self._getString(3)

    def setClanAbbrev(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(FriendModel, self)._initialize()
        self._addBoolProperty('isGiftReceived', False)
        self._addNumberProperty('spaID', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('clanAbbrev', '')
