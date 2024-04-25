# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/player_info_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import BaseTeamMemberModel

class PlayerInfoModel(BaseTeamMemberModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(PlayerInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def killerVehicle(self):
        return self._getViewModel(11)

    @staticmethod
    def getKillerVehicleType():
        return VehicleInfoModel

    def getIsKilled(self):
        return self._getBool(12)

    def setIsKilled(self, value):
        self._setBool(12, value)

    def getReason(self):
        return self._getString(13)

    def setReason(self, value):
        self._setString(13, value)

    def getTasksCompleted(self):
        return self._getNumber(14)

    def setTasksCompleted(self, value):
        self._setNumber(14, value)

    def getTasksAmount(self):
        return self._getNumber(15)

    def setTasksAmount(self, value):
        self._setNumber(15, value)

    def getFrontManId(self):
        return self._getNumber(16)

    def setFrontManId(self, value):
        self._setNumber(16, value)

    def getPolygon(self):
        return self._getString(17)

    def setPolygon(self, value):
        self._setString(17, value)

    def _initialize(self):
        super(PlayerInfoModel, self)._initialize()
        self._addViewModelProperty('killerVehicle', VehicleInfoModel())
        self._addBoolProperty('isKilled', False)
        self._addStringProperty('reason', '')
        self._addNumberProperty('tasksCompleted', 0)
        self._addNumberProperty('tasksAmount', 5)
        self._addNumberProperty('frontManId', 0)
        self._addStringProperty('polygon', '')
