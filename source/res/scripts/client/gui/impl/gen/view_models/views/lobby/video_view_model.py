# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/video_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class VideoViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onVideoStarted', 'onVideoStopped')

    def __init__(self, properties=1, commands=3):
        super(VideoViewModel, self).__init__(properties=properties, commands=commands)

    def getVideoSource(self):
        return self._getResource(0)

    def setVideoSource(self, value):
        self._setResource(0, value)

    def _initialize(self):
        super(VideoViewModel, self)._initialize()
        self._addResourceProperty('videoSource', R.invalid())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
