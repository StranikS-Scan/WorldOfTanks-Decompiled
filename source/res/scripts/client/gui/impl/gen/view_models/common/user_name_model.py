# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/user_name_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.badge_model import BadgeModel

class UserNameModel(ViewModel):
    __slots__ = ()
    IGR_TYPE_NONE = 0
    IGR_TYPE_BASE = 1
    IGR_TYPE_PREMIUM = 2

    def __init__(self, properties=9, commands=0):
        super(UserNameModel, self).__init__(properties=properties, commands=commands)

    @property
    def badge(self):
        return self._getViewModel(0)

    @property
    def suffixBadge(self):
        return self._getViewModel(1)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getHiddenUserName(self):
        return self._getString(3)

    def setHiddenUserName(self, value):
        self._setString(3, value)

    def getClanAbbrev(self):
        return self._getString(4)

    def setClanAbbrev(self, value):
        self._setString(4, value)

    def getIsFakeNameVisible(self):
        return self._getBool(5)

    def setIsFakeNameVisible(self, value):
        self._setBool(5, value)

    def getIgrType(self):
        return self._getNumber(6)

    def setIgrType(self, value):
        self._setNumber(6, value)

    def getIsTeamKiller(self):
        return self._getBool(7)

    def setIsTeamKiller(self, value):
        self._setBool(7, value)

    def getIsKilled(self):
        return self._getBool(8)

    def setIsKilled(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(UserNameModel, self)._initialize()
        self._addViewModelProperty('badge', BadgeModel())
        self._addViewModelProperty('suffixBadge', BadgeModel())
        self._addStringProperty('userName', '')
        self._addStringProperty('hiddenUserName', '')
        self._addStringProperty('clanAbbrev', '')
        self._addBoolProperty('isFakeNameVisible', True)
        self._addNumberProperty('igrType', 0)
        self._addBoolProperty('isTeamKiller', False)
        self._addBoolProperty('isKilled', False)
