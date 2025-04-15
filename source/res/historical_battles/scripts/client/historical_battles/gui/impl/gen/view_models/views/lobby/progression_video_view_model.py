# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/progression_video_view_model.py
from frameworks.wulf import ViewModel

class ProgressionVideoViewModel(ViewModel):
    __slots__ = ('onClose', 'onError', 'onVideoStarted', 'onVideoEnded')

    def __init__(self, properties=2, commands=4):
        super(ProgressionVideoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(0)

    def setIsWindowAccessible(self, value):
        self._setBool(0, value)

    def getVideoName(self):
        return self._getString(1)

    def setVideoName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ProgressionVideoViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self._addStringProperty('videoName', '')
        self.onClose = self._addCommand('onClose')
        self.onError = self._addCommand('onError')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoEnded = self._addCommand('onVideoEnded')
