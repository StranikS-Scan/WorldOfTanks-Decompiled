# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/user_name_model.py
from frameworks.wulf import ViewModel

class UserNameModel(ViewModel):
    __slots__ = ()

    def getUserName(self):
        return self._getString(0)

    def setUserName(self, value):
        self._setString(0, value)

    def getClanAbbrev(self):
        return self._getString(1)

    def setClanAbbrev(self, value):
        self._setString(1, value)

    def getIsTeamKiller(self):
        return self._getBool(2)

    def setIsTeamKiller(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(UserNameModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('clanAbbrev', '')
        self._addBoolProperty('isTeamKiller', False)
