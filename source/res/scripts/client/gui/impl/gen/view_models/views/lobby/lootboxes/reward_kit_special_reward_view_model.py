# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/reward_kit_special_reward_view_model.py
from frameworks.wulf import ViewModel

class RewardKitSpecialRewardViewModel(ViewModel):
    __slots__ = ('onContinue', 'onGoToReward', 'onClose', 'onVideoStarted', 'onVideoStopped')

    def __init__(self, properties=10, commands=5):
        super(RewardKitSpecialRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getVideoSource(self):
        return self._getString(0)

    def setVideoSource(self, value):
        self._setString(0, value)

    def getCongratsType(self):
        return self._getString(1)

    def setCongratsType(self, value):
        self._setString(1, value)

    def getIsGuaranteedReward(self):
        return self._getBool(2)

    def setIsGuaranteedReward(self, value):
        self._setBool(2, value)

    def getVehicleIsElite(self):
        return self._getBool(3)

    def setVehicleIsElite(self, value):
        self._setBool(3, value)

    def getVehicleType(self):
        return self._getString(4)

    def setVehicleType(self, value):
        self._setString(4, value)

    def getVehicleLvl(self):
        return self._getString(5)

    def setVehicleLvl(self, value):
        self._setString(5, value)

    def getVehicleName(self):
        return self._getString(6)

    def setVehicleName(self, value):
        self._setString(6, value)

    def getStreamBufferLength(self):
        return self._getNumber(7)

    def setStreamBufferLength(self, value):
        self._setNumber(7, value)

    def getIsViewAccessible(self):
        return self._getBool(8)

    def setIsViewAccessible(self, value):
        self._setBool(8, value)

    def getRealm(self):
        return self._getString(9)

    def setRealm(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(RewardKitSpecialRewardViewModel, self)._initialize()
        self._addStringProperty('videoSource', '')
        self._addStringProperty('congratsType', '')
        self._addBoolProperty('isGuaranteedReward', False)
        self._addBoolProperty('vehicleIsElite', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLvl', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('streamBufferLength', 1)
        self._addBoolProperty('isViewAccessible', True)
        self._addStringProperty('realm', '')
        self.onContinue = self._addCommand('onContinue')
        self.onGoToReward = self._addCommand('onGoToReward')
        self.onClose = self._addCommand('onClose')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
