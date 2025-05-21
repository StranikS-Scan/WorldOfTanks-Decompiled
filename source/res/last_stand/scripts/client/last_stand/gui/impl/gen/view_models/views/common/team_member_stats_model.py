# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/common/team_member_stats_model.py
from frameworks.wulf import ViewModel

class TeamMemberStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(TeamMemberStatsModel, self).__init__(properties=properties, commands=commands)

    def getKills(self):
        return self._getNumber(0)

    def setKills(self, value):
        self._setNumber(0, value)

    def getPlaceByKills(self):
        return self._getNumber(1)

    def setPlaceByKills(self, value):
        self._setNumber(1, value)

    def getDamage(self):
        return self._getNumber(2)

    def setDamage(self, value):
        self._setNumber(2, value)

    def getPlaceByDamage(self):
        return self._getNumber(3)

    def setPlaceByDamage(self, value):
        self._setNumber(3, value)

    def getAssist(self):
        return self._getNumber(4)

    def setAssist(self, value):
        self._setNumber(4, value)

    def getBlocked(self):
        return self._getNumber(5)

    def setBlocked(self, value):
        self._setNumber(5, value)

    def getSouls(self):
        return self._getNumber(6)

    def setSouls(self, value):
        self._setNumber(6, value)

    def getPlaceByMatter(self):
        return self._getNumber(7)

    def setPlaceByMatter(self, value):
        self._setNumber(7, value)

    def getPlace(self):
        return self._getNumber(8)

    def setPlace(self, value):
        self._setNumber(8, value)

    def getKeys(self):
        return self._getNumber(9)

    def setKeys(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(TeamMemberStatsModel, self)._initialize()
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('placeByKills', 0)
        self._addNumberProperty('damage', 0)
        self._addNumberProperty('placeByDamage', 0)
        self._addNumberProperty('assist', 0)
        self._addNumberProperty('blocked', 0)
        self._addNumberProperty('souls', 0)
        self._addNumberProperty('placeByMatter', 0)
        self._addNumberProperty('place', 1)
        self._addNumberProperty('keys', 0)
