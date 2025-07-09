# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/reward_video_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RewardVideoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RewardVideoModel, self).__init__(properties=properties, commands=commands)

    def getVideoResName(self):
        return self._getResource(0)

    def setVideoResName(self, value):
        self._setResource(0, value)

    def getDuration(self):
        return self._getNumber(1)

    def setDuration(self, value):
        self._setNumber(1, value)

    def getShowFooterTiming(self):
        return self._getNumber(2)

    def setShowFooterTiming(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(RewardVideoModel, self)._initialize()
        self._addResourceProperty('videoResName', R.invalid())
        self._addNumberProperty('duration', 0)
        self._addNumberProperty('showFooterTiming', 0)
