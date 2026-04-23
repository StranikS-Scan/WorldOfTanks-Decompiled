# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/common/base_team_member_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from last_stand.gui.impl.gen.view_models.views.common.team_member_stats_model import TeamMemberStatsModel
from last_stand.gui.impl.gen.view_models.views.common.vehicle_model import VehicleModel

class TeamMemberBanType(Enum):
    NOTBANNED = 'notBanned'
    WARNED = 'warned'
    BANNED = 'banned'


class BaseTeamMemberModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
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

    def getId(self):
        return self._getNumber(3)

    def setId(self, value):
        self._setNumber(3, value)

    def getPlayerId(self):
        return self._getNumber(4)

    def setPlayerId(self, value):
        self._setNumber(4, value)

    def getIsOwnSquad(self):
        return self._getBool(5)

    def setIsOwnSquad(self, value):
        self._setBool(5, value)

    def getIsAlive(self):
        return self._getBool(6)

    def setIsAlive(self, value):
        self._setBool(6, value)

    def getIsReady(self):
        return self._getBool(7)

    def setIsReady(self, value):
        self._setBool(7, value)

    def getIsCurrentPlayer(self):
        return self._getBool(8)

    def setIsCurrentPlayer(self, value):
        self._setBool(8, value)

    def getSquadNum(self):
        return self._getNumber(9)

    def setSquadNum(self, value):
        self._setNumber(9, value)

    def getBanType(self):
        return TeamMemberBanType(self._getString(10))

    def setBanType(self, value):
        self._setString(10, value.value)

    def _initialize(self):
        super(BaseTeamMemberModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('stats', TeamMemberStatsModel())
        self._addNumberProperty('id', 0)
        self._addNumberProperty('playerId', 0)
        self._addBoolProperty('isOwnSquad', False)
        self._addBoolProperty('isAlive', True)
        self._addBoolProperty('isReady', True)
        self._addBoolProperty('isCurrentPlayer', False)
        self._addNumberProperty('squadNum', 0)
        self._addStringProperty('banType')
