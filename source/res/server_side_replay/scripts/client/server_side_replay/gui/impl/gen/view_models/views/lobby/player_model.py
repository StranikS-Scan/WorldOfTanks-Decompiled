# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/player_model.py
from frameworks.wulf import ViewModel

class PlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    def getSpaID(self):
        return self._getNumber(0)

    def setSpaID(self, value):
        self._setNumber(0, value)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getClanTag(self):
        return self._getString(2)

    def setClanTag(self, value):
        self._setString(2, value)

    def getClanTagColor(self):
        return self._getString(3)

    def setClanTagColor(self, value):
        self._setString(3, value)

    def getBadgeID(self):
        return self._getString(4)

    def setBadgeID(self, value):
        self._setString(4, value)

    def getSuffixBadgeID(self):
        return self._getString(5)

    def setSuffixBadgeID(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addNumberProperty('spaID', 0)
        self._addStringProperty('userName', '')
        self._addStringProperty('clanTag', '')
        self._addStringProperty('clanTagColor', '')
        self._addStringProperty('badgeID', '')
        self._addStringProperty('suffixBadgeID', '')
