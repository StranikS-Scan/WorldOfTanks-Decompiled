# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/video_view/video_view_subs_phrase_model.py
from frameworks.wulf import ViewModel

class VideoViewSubsPhraseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VideoViewSubsPhraseModel, self).__init__(properties=properties, commands=commands)

    def getStartTime(self):
        return self._getReal(0)

    def setStartTime(self, value):
        self._setReal(0, value)

    def getEndTime(self):
        return self._getReal(1)

    def setEndTime(self, value):
        self._setReal(1, value)

    def getText(self):
        return self._getString(2)

    def setText(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(VideoViewSubsPhraseModel, self)._initialize()
        self._addRealProperty('startTime', 0.0)
        self._addRealProperty('endTime', 0.0)
        self._addStringProperty('text', '')
