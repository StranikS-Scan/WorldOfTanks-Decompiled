# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar_event/offspring_concert_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class OffspringConcertViewModel(ViewModel):
    __slots__ = ('onTrackClicked', 'onTrackSwitched', 'onCameraBtnClicked', 'onCameraSwitched', 'onCloseAction')

    def getTracks(self):
        return self._getArray(0)

    def setTracks(self, value):
        self._setArray(0, value)

    def getCurrentTrackIdx(self):
        return self._getNumber(1)

    def setCurrentTrackIdx(self, value):
        self._setNumber(1, value)

    def getPreviousTrackIdx(self):
        return self._getNumber(2)

    def setPreviousTrackIdx(self, value):
        self._setNumber(2, value)

    def getDesiredToSwitchTrackIdx(self):
        return self._getNumber(3)

    def setDesiredToSwitchTrackIdx(self, value):
        self._setNumber(3, value)

    def getCurrentCameraIdx(self):
        return self._getNumber(4)

    def setCurrentCameraIdx(self, value):
        self._setNumber(4, value)

    def getTriggerTrackFinishedAnimation(self):
        return self._getBool(5)

    def setTriggerTrackFinishedAnimation(self, value):
        self._setBool(5, value)

    def getIsDragging(self):
        return self._getBool(6)

    def setIsDragging(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(OffspringConcertViewModel, self)._initialize()
        self._addArrayProperty('tracks', Array())
        self._addNumberProperty('currentTrackIdx', 0)
        self._addNumberProperty('previousTrackIdx', -1)
        self._addNumberProperty('desiredToSwitchTrackIdx', 0)
        self._addNumberProperty('currentCameraIdx', 1)
        self._addBoolProperty('triggerTrackFinishedAnimation', False)
        self._addBoolProperty('isDragging', False)
        self.onTrackClicked = self._addCommand('onTrackClicked')
        self.onTrackSwitched = self._addCommand('onTrackSwitched')
        self.onCameraBtnClicked = self._addCommand('onCameraBtnClicked')
        self.onCameraSwitched = self._addCommand('onCameraSwitched')
        self.onCloseAction = self._addCommand('onCloseAction')
