# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/user_item.py
from frameworks.wulf import ViewModel

class UserItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(UserItem, self).__init__(properties=properties, commands=commands)

    def getUserID(self):
        return self._getNumber(0)

    def setUserID(self, value):
        self._setNumber(0, value)

    def getUserNickName(self):
        return self._getString(1)

    def setUserNickName(self, value):
        self._setString(1, value)

    def getClanTag(self):
        return self._getString(2)

    def setClanTag(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(UserItem, self)._initialize()
        self._addNumberProperty('userID', 0)
        self._addStringProperty('userNickName', '')
        self._addStringProperty('clanTag', '')
