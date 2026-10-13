# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/battle/views/fort_rush_hud_base_capture_indicator_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class FortRushBaseCaptureTeam(Enum):
    NEUTRAL = 'neutral'
    ALLY = 'ally'
    ENEMY = 'enemy'


class FortRushBaseCaptureState(Enum):
    IDLE = 'Idle'
    CAPTURING = 'Capturing'
    CONTESTED = 'Contested'
    DECAPPING = 'Decapping'


class FortRushHudBaseCaptureIndicatorModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(FortRushHudBaseCaptureIndicatorModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getString(0)

    def setLabel(self, value):
        self._setString(0, value)

    def getOwnerTeam(self):
        return FortRushBaseCaptureTeam(self._getString(1))

    def setOwnerTeam(self, value):
        self._setString(1, value.value)

    def getCapturingTeam(self):
        return FortRushBaseCaptureTeam(self._getString(2))

    def setCapturingTeam(self, value):
        self._setString(2, value.value)

    def getState(self):
        return FortRushBaseCaptureState(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def getCaptureProgress(self):
        return self._getReal(4)

    def setCaptureProgress(self, value):
        self._setReal(4, value)

    def getUid(self):
        return self._getNumber(5)

    def setUid(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(FortRushHudBaseCaptureIndicatorModel, self)._initialize()
        self._addStringProperty('label', '')
        self._addStringProperty('ownerTeam', FortRushBaseCaptureTeam.NEUTRAL.value)
        self._addStringProperty('capturingTeam', FortRushBaseCaptureTeam.NEUTRAL.value)
        self._addStringProperty('state', FortRushBaseCaptureState.IDLE.value)
        self._addRealProperty('captureProgress', 0.0)
        self._addNumberProperty('uid', -1)
