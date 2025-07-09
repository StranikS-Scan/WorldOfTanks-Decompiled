# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/player_model.py
from frameworks.wulf import ViewModel

class PlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getClanAbbrev(self):
        return self._getString(1)

    def setClanAbbrev(self, value):
        self._setString(1, value)

    def getSpaID(self):
        return self._getNumber(2)

    def setSpaID(self, value):
        self._setNumber(2, value)

    def getLocked(self):
        return self._getBool(3)

    def setLocked(self, value):
        self._setBool(3, value)

    def getIsNameLoading(self):
        return self._getBool(4)

    def setIsNameLoading(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('clanAbbrev', '')
        self._addNumberProperty('spaID', 0)
        self._addBoolProperty('locked', False)
        self._addBoolProperty('isNameLoading', True)
