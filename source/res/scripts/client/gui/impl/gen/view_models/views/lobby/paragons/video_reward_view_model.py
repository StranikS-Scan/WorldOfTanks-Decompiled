# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/video_reward_view_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class VideoRewardViewModel(VehicleInfoModel):
    __slots__ = ('onClose', 'onError')

    def __init__(self, properties=11, commands=2):
        super(VideoRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(10)

    def setIsWindowAccessible(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(VideoRewardViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self.onClose = self._addCommand('onClose')
        self.onError = self._addCommand('onError')
