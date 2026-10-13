# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/shared/clip/auto_loader_clip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BoostState(Enum):
    UNAVAILABLE = 'unavailable'
    INAPPLICABLE = 'inapplicable'
    WAITINGFORSTART = 'waitingForStart'
    CHARGING = 'charging'
    CHARGED = 'charged'


class AutoLoaderClipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(AutoLoaderClipModel, self).__init__(properties=properties, commands=commands)

    def getClipCapacity(self):
        return self._getNumber(0)

    def setClipCapacity(self, value):
        self._setNumber(0, value)

    def getQuantityInClip(self):
        return self._getNumber(1)

    def setQuantityInClip(self, value):
        self._setNumber(1, value)

    def getShellLoadingTimeLeft(self):
        return self._getReal(2)

    def setShellLoadingTimeLeft(self, value):
        self._setReal(2, value)

    def getShellLoadingBaseDuration(self):
        return self._getReal(3)

    def setShellLoadingBaseDuration(self, value):
        self._setReal(3, value)

    def getAutoloadTimeLeft(self):
        return self._getReal(4)

    def setAutoloadTimeLeft(self, value):
        self._setReal(4, value)

    def getAutoloadBaseDuration(self):
        return self._getReal(5)

    def setAutoloadBaseDuration(self, value):
        self._setReal(5, value)

    def getIsAutoloadCritical(self):
        return self._getBool(6)

    def setIsAutoloadCritical(self, value):
        self._setBool(6, value)

    def getIsAutoloadTimerOn(self):
        return self._getBool(7)

    def setIsAutoloadTimerOn(self, value):
        self._setBool(7, value)

    def getIsTimerRed(self):
        return self._getBool(8)

    def setIsTimerRed(self, value):
        self._setBool(8, value)

    def getBoostState(self):
        return BoostState(self._getString(9))

    def setBoostState(self, value):
        self._setString(9, value.value)

    def getBoostTimeLeft(self):
        return self._getReal(10)

    def setBoostTimeLeft(self, value):
        self._setReal(10, value)

    def getBoostTotalTime(self):
        return self._getReal(11)

    def setBoostTotalTime(self, value):
        self._setReal(11, value)

    def getIsBoostApplicable(self):
        return self._getBool(12)

    def setIsBoostApplicable(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(AutoLoaderClipModel, self)._initialize()
        self._addNumberProperty('clipCapacity', -1)
        self._addNumberProperty('quantityInClip', -1)
        self._addRealProperty('shellLoadingTimeLeft', -1.0)
        self._addRealProperty('shellLoadingBaseDuration', -1.0)
        self._addRealProperty('autoloadTimeLeft', -1.0)
        self._addRealProperty('autoloadBaseDuration', -1.0)
        self._addBoolProperty('isAutoloadCritical', False)
        self._addBoolProperty('isAutoloadTimerOn', False)
        self._addBoolProperty('isTimerRed', False)
        self._addStringProperty('boostState', BoostState.UNAVAILABLE.value)
        self._addRealProperty('boostTimeLeft', 0.0)
        self._addRealProperty('boostTotalTime', 0.0)
        self._addBoolProperty('isBoostApplicable', False)
