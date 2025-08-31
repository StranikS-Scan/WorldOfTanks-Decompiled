# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_video_rewards_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_reward_item_model import Pm3RewardItemModel

class OperationState(Enum):
    COMPLETEWITHHONOR = 'completeWithHonor'
    COMPLETE = 'complete'
    COMPANYCOMPLETE = 'companyComplete'


class PersonalMissionsVideoRewardsViewModel(VehicleInfoModel):
    __slots__ = ('onClose', 'onError', 'onShowVehicle', 'onVideoStarted')

    def __init__(self, properties=15, commands=4):
        super(PersonalMissionsVideoRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(10)

    def setIsWindowAccessible(self, value):
        self._setBool(10, value)

    def getVideoName(self):
        return self._getString(11)

    def setVideoName(self, value):
        self._setString(11, value)

    def getIsFinalPm3Rewards(self):
        return self._getBool(12)

    def setIsFinalPm3Rewards(self, value):
        self._setBool(12, value)

    def getState(self):
        return OperationState(self._getString(13))

    def setState(self, value):
        self._setString(13, value.value)

    def getRewards(self):
        return self._getArray(14)

    def setRewards(self, value):
        self._setArray(14, value)

    @staticmethod
    def getRewardsType():
        return Pm3RewardItemModel

    def _initialize(self):
        super(PersonalMissionsVideoRewardsViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self._addStringProperty('videoName', '')
        self._addBoolProperty('isFinalPm3Rewards', False)
        self._addStringProperty('state')
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onError = self._addCommand('onError')
        self.onShowVehicle = self._addCommand('onShowVehicle')
        self.onVideoStarted = self._addCommand('onVideoStarted')
