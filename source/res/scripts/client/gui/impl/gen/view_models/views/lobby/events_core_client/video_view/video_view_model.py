# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/events_core_client/video_view/video_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class VideoViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=4, commands=1):
        super(VideoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsControlsVisible(self):
        return self._getBool(0)

    def setIsControlsVisible(self, value):
        self._setBool(0, value)

    def getIsSubtitlesVisible(self):
        return self._getBool(1)

    def setIsSubtitlesVisible(self, value):
        self._setBool(1, value)

    def getVideoPath(self):
        return self._getResource(2)

    def setVideoPath(self, value):
        self._setResource(2, value)

    def getInitialAudioVolume(self):
        return self._getReal(3)

    def setInitialAudioVolume(self, value):
        self._setReal(3, value)

    def _initialize(self):
        super(VideoViewModel, self)._initialize()
        self._addBoolProperty('isControlsVisible', True)
        self._addBoolProperty('isSubtitlesVisible', True)
        self._addResourceProperty('videoPath', R.invalid())
        self._addRealProperty('initialAudioVolume', 0.5)
        self.onClose = self._addCommand('onClose')
