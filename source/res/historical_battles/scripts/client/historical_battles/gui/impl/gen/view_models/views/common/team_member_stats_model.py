# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/team_member_stats_model.py
from frameworks.wulf import ViewModel

class TeamMemberStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TeamMemberStatsModel, self).__init__(properties=properties, commands=commands)

    def getKills(self):
        return self._getNumber(0)

    def setKills(self, value):
        self._setNumber(0, value)

    def getDamage(self):
        return self._getNumber(1)

    def setDamage(self, value):
        self._setNumber(1, value)

    def getAssist(self):
        return self._getNumber(2)

    def setAssist(self, value):
        self._setNumber(2, value)

    def getBlocked(self):
        return self._getNumber(3)

    def setBlocked(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(TeamMemberStatsModel, self)._initialize()
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('damage', 0)
        self._addNumberProperty('assist', 0)
        self._addNumberProperty('blocked', 0)
