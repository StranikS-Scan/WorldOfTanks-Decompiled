# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/video_view_model.py
from frameworks.wulf import ViewModel

class VideoViewModel(ViewModel):
    __slots__ = ('onClose', 'onError', 'onVideoStarted')

    def __init__(self, properties=2, commands=3):
        super(VideoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(0)

    def setIsWindowAccessible(self, value):
        self._setBool(0, value)

    def getVideoName(self):
        return self._getString(1)

    def setVideoName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(VideoViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self._addStringProperty('videoName', '')
        self.onClose = self._addCommand('onClose')
        self.onError = self._addCommand('onError')
        self.onVideoStarted = self._addCommand('onVideoStarted')
