# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/video_view/video_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.video_view.video_view_subs_phrase_model import VideoViewSubsPhraseModel

class VideoViewModel(ViewModel):
    __slots__ = ('onClose', 'onError', 'onVideoStarted', 'onVideoPause', 'onVideoPlay', 'currentVolume')

    def __init__(self, properties=5, commands=6):
        super(VideoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(0)

    def setIsWindowAccessible(self, value):
        self._setBool(0, value)

    def getIsControlsVisible(self):
        return self._getBool(1)

    def setIsControlsVisible(self, value):
        self._setBool(1, value)

    def getVideoName(self):
        return self._getString(2)

    def setVideoName(self, value):
        self._setString(2, value)

    def getDefaultVolume(self):
        return self._getReal(3)

    def setDefaultVolume(self, value):
        self._setReal(3, value)

    def getPhrases(self):
        return self._getArray(4)

    def setPhrases(self, value):
        self._setArray(4, value)

    @staticmethod
    def getPhrasesType():
        return VideoViewSubsPhraseModel

    def _initialize(self):
        super(VideoViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self._addBoolProperty('isControlsVisible', True)
        self._addStringProperty('videoName', '')
        self._addRealProperty('defaultVolume', 0.0)
        self._addArrayProperty('phrases', Array())
        self.onClose = self._addCommand('onClose')
        self.onError = self._addCommand('onError')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoPause = self._addCommand('onVideoPause')
        self.onVideoPlay = self._addCommand('onVideoPlay')
        self.currentVolume = self._addCommand('currentVolume')
