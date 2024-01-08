# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_video_reward_view_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class ArmoryYardVideoRewardViewModel(VehicleInfoModel):
    __slots__ = ('onClose', 'onError', 'onShowVehicle', 'onVideoStarted')

    def __init__(self, properties=10, commands=4):
        super(ArmoryYardVideoRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(8)

    def setIsWindowAccessible(self, value):
        self._setBool(8, value)

    def getVideoName(self):
        return self._getString(9)

    def setVideoName(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(ArmoryYardVideoRewardViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self._addStringProperty('videoName', '')
        self.onClose = self._addCommand('onClose')
        self.onError = self._addCommand('onError')
        self.onShowVehicle = self._addCommand('onShowVehicle')
        self.onVideoStarted = self._addCommand('onVideoStarted')
