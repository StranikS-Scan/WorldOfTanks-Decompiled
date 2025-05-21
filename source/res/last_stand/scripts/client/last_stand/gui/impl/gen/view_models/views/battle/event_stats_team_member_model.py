# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/battle/event_stats_team_member_model.py
from last_stand.gui.impl.gen.view_models.views.common.base_team_member_model import BaseTeamMemberModel

class EventStatsTeamMemberModel(BaseTeamMemberModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(EventStatsTeamMemberModel, self).__init__(properties=properties, commands=commands)

    def getIsFriendRequestSent(self):
        return self._getBool(11)

    def setIsFriendRequestSent(self, value):
        self._setBool(11, value)

    def getIsInFriendList(self):
        return self._getBool(12)

    def setIsInFriendList(self, value):
        self._setBool(12, value)

    def getIsPlatoonRequestCanMade(self):
        return self._getBool(13)

    def setIsPlatoonRequestCanMade(self, value):
        self._setBool(13, value)

    def getIsPlatoonRequestInSquad(self):
        return self._getBool(14)

    def setIsPlatoonRequestInSquad(self, value):
        self._setBool(14, value)

    def getIsPlatoonRequestSent(self):
        return self._getBool(15)

    def setIsPlatoonRequestSent(self, value):
        self._setBool(15, value)

    def getIsBlacklisted(self):
        return self._getBool(16)

    def setIsBlacklisted(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(EventStatsTeamMemberModel, self)._initialize()
        self._addBoolProperty('isFriendRequestSent', False)
        self._addBoolProperty('isInFriendList', False)
        self._addBoolProperty('isPlatoonRequestCanMade', True)
        self._addBoolProperty('isPlatoonRequestInSquad', True)
        self._addBoolProperty('isPlatoonRequestSent', False)
        self._addBoolProperty('isBlacklisted', False)
