# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/base_team_member_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from halloween.gui.impl.gen.view_models.views.lobby.common.detailed_stats_model import DetailedStatsModel
from halloween.gui.impl.gen.view_models.views.lobby.common.team_member_stats_model import TeamMemberStatsModel
from halloween.gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class BaseTeamMemberModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(BaseTeamMemberModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserType():
        return UserNameModel

    @property
    def vehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    @property
    def stats(self):
        return self._getViewModel(2)

    @staticmethod
    def getStatsType():
        return TeamMemberStatsModel

    @property
    def detailedStats(self):
        return self._getViewModel(3)

    @staticmethod
    def getDetailedStatsType():
        return DetailedStatsModel

    def getId(self):
        return self._getNumber(4)

    def setId(self, value):
        self._setNumber(4, value)

    def getPlayerId(self):
        return self._getNumber(5)

    def setPlayerId(self, value):
        self._setNumber(5, value)

    def getIsOwnSquad(self):
        return self._getBool(6)

    def setIsOwnSquad(self, value):
        self._setBool(6, value)

    def getIsPrematureLeave(self):
        return self._getBool(7)

    def setIsPrematureLeave(self, value):
        self._setBool(7, value)

    def getIsCurrentPlayer(self):
        return self._getBool(8)

    def setIsCurrentPlayer(self, value):
        self._setBool(8, value)

    def getSquadNum(self):
        return self._getNumber(9)

    def setSquadNum(self, value):
        self._setNumber(9, value)

    def getIsWarned(self):
        return self._getBool(10)

    def setIsWarned(self, value):
        self._setBool(10, value)

    def getIsFriendRequestSent(self):
        return self._getBool(11)

    def setIsFriendRequestSent(self, value):
        self._setBool(11, value)

    def getIsInFriendList(self):
        return self._getBool(12)

    def setIsInFriendList(self, value):
        self._setBool(12, value)

    def getIsPlatoonRequestCanBeMade(self):
        return self._getBool(13)

    def setIsPlatoonRequestCanBeMade(self, value):
        self._setBool(13, value)

    def getIsPlatoonRequestSent(self):
        return self._getBool(14)

    def setIsPlatoonRequestSent(self, value):
        self._setBool(14, value)

    def getIsBlacklisted(self):
        return self._getBool(15)

    def setIsBlacklisted(self, value):
        self._setBool(15, value)

    def getNumberOfRespawns(self):
        return self._getNumber(16)

    def setNumberOfRespawns(self, value):
        self._setNumber(16, value)

    def getIsAlly(self):
        return self._getBool(17)

    def setIsAlly(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(BaseTeamMemberModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('stats', TeamMemberStatsModel())
        self._addViewModelProperty('detailedStats', DetailedStatsModel())
        self._addNumberProperty('id', 0)
        self._addNumberProperty('playerId', 0)
        self._addBoolProperty('isOwnSquad', False)
        self._addBoolProperty('isPrematureLeave', True)
        self._addBoolProperty('isCurrentPlayer', False)
        self._addNumberProperty('squadNum', 0)
        self._addBoolProperty('isWarned', False)
        self._addBoolProperty('isFriendRequestSent', False)
        self._addBoolProperty('isInFriendList', False)
        self._addBoolProperty('isPlatoonRequestCanBeMade', True)
        self._addBoolProperty('isPlatoonRequestSent', False)
        self._addBoolProperty('isBlacklisted', False)
        self._addNumberProperty('numberOfRespawns', 0)
        self._addBoolProperty('isAlly', False)
