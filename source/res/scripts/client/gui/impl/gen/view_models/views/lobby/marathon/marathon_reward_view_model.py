# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/marathon_reward_view_model.py
from frameworks.wulf import ViewModel

class MarathonRewardViewModel(ViewModel):
    __slots__ = ('onGoToVehicleBtnClick', 'onViewRewardsBtnClick', 'onCloseBtnClick', 'onVideoStarted', 'onVideoStopped')

    def __init__(self, properties=6, commands=5):
        super(MarathonRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsGoToVehicleBtnEnabled(self):
        return self._getBool(0)

    def setIsGoToVehicleBtnEnabled(self, value):
        self._setBool(0, value)

    def getVideoSource(self):
        return self._getString(1)

    def setVideoSource(self, value):
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

    def _initialize(self):
        super(MarathonRewardViewModel, self)._initialize()
        self._addBoolProperty('isGoToVehicleBtnEnabled', True)
        self._addStringProperty('videoSource', '')
        self._addBoolProperty('vehicleIsElite', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLvl', '')
        self._addStringProperty('vehicleName', '')
        self.onGoToVehicleBtnClick = self._addCommand('onGoToVehicleBtnClick')
        self.onViewRewardsBtnClick = self._addCommand('onViewRewardsBtnClick')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
