# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/shared/clip/controllable_reload_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ClipState(Enum):
    NONE = 'none'
    NORMAL = 'normal'
    CRITICAL = 'critical'


class ControllableReloadModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(ControllableReloadModel, self).__init__(properties=properties, commands=commands)

    def getClipCapacity(self):
        return self._getNumber(0)

    def setClipCapacity(self, value):
        self._setNumber(0, value)

    def getQuantityInClip(self):
        return self._getNumber(1)

    def setQuantityInClip(self, value):
        self._setNumber(1, value)

    def getClipState(self):
        return ClipState(self._getString(2))

    def setClipState(self, value):
        self._setString(2, value.value)

    def getIsInControllableReload(self):
        return self._getBool(3)

    def setIsInControllableReload(self, value):
        self._setBool(3, value)

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

    def _initialize(self):
        super(ControllableReloadModel, self)._initialize()
        self._addNumberProperty('clipCapacity', -1)
        self._addNumberProperty('quantityInClip', -1)
        self._addStringProperty('clipState', ClipState.NONE.value)
        self._addBoolProperty('isInControllableReload', False)
        self._addRealProperty('autoloadTimeLeft', -1.0)
        self._addRealProperty('autoloadBaseDuration', -1.0)
        self._addBoolProperty('isAutoloadCritical', False)
        self._addBoolProperty('isAutoloadTimerOn', False)
