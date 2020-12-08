# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_special_reward_view_model.py
from frameworks.wulf import ViewModel

class LootBoxSpecialRewardViewModel(ViewModel):
    __slots__ = ('onContinueBtnClick', 'onGoToRewardBtnClick', 'onCloseBtnClick', 'onVideoStarted', 'onVideoStopped', 'onVideoInterrupted')

    def __init__(self, properties=8, commands=6):
        super(LootBoxSpecialRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getVideoSource(self):
        return self._getString(0)

    def setVideoSource(self, value):
        self._setString(0, value)

    def getCongratsType(self):
        return self._getString(1)

    def setCongratsType(self, value):
        self._setString(1, value)

    def getVehicleIsElite(self):
        return self._getBool(2)

    def setVehicleIsElite(self, value):
        self._setBool(2, value)

    def getVehicleType(self):
        return self._getString(3)

    def setVehicleType(self, value):
        self._setString(3, value)

    def getVehicleLvl(self):
        return self._getString(4)

    def setVehicleLvl(self, value):
        self._setString(4, value)

    def getVehicleName(self):
        return self._getString(5)

    def setVehicleName(self, value):
        self._setString(5, value)

    def getStreamBufferLength(self):
        return self._getNumber(6)

    def setStreamBufferLength(self, value):
        self._setNumber(6, value)

    def getIsViewAccessible(self):
        return self._getBool(7)

    def setIsViewAccessible(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(LootBoxSpecialRewardViewModel, self)._initialize()
        self._addStringProperty('videoSource', '')
        self._addStringProperty('congratsType', '')
        self._addBoolProperty('vehicleIsElite', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLvl', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('streamBufferLength', 1)
        self._addBoolProperty('isViewAccessible', True)
        self.onContinueBtnClick = self._addCommand('onContinueBtnClick')
        self.onGoToRewardBtnClick = self._addCommand('onGoToRewardBtnClick')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
        self.onVideoInterrupted = self._addCommand('onVideoInterrupted')
