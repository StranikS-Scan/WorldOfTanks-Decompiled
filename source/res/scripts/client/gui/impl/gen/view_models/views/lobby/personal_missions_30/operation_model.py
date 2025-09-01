# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/operation_model.py
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import OperationState
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.additional_mission_model import AdditionalMissionModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.detail_model import DetailModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_reward_model import MainViewRewardModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.mission_model import MissionModel

class OperationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(OperationModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return MainViewRewardModel

    def getDetails(self):
        return self._getArray(1)

    def setDetails(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDetailsType():
        return DetailModel

    def getMissions(self):
        return self._getArray(2)

    def setMissions(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMissionsType():
        return MissionModel

    def getAdditionalMissions(self):
        return self._getArray(3)

    def setAdditionalMissions(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAdditionalMissionsType():
        return AdditionalMissionModel

    def getOperationId(self):
        return self._getNumber(4)

    def setOperationId(self, value):
        self._setNumber(4, value)

    def getOperationState(self):
        return OperationState(self._getString(5))

    def setOperationState(self, value):
        self._setString(5, value.value)

    def getValue(self):
        return self._getNumber(6)

    def setValue(self, value):
        self._setNumber(6, value)

    def getMaxValue(self):
        return self._getNumber(7)

    def setMaxValue(self, value):
        self._setNumber(7, value)

    def getDeltaFrom(self):
        return self._getNumber(8)

    def setDeltaFrom(self, value):
        self._setNumber(8, value)

    def getVehicleInHangar(self):
        return self._getBool(9)

    def setVehicleInHangar(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(OperationModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('details', Array())
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('additionalMissions', Array())
        self._addNumberProperty('operationId', 0)
        self._addStringProperty('operationState')
        self._addNumberProperty('value', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('deltaFrom', 0)
        self._addBoolProperty('vehicleInHangar', False)
