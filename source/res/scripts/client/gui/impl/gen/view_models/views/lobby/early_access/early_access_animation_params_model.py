# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_animation_params_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class AnimationType(IntEnum):
    NONE = 0
    FROMTO = 1


class EarlyAccessAnimationParamsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EarlyAccessAnimationParamsModel, self).__init__(properties=properties, commands=commands)

    def getAnimationType(self):
        return AnimationType(self._getNumber(0))

    def setAnimationType(self, value):
        self._setNumber(0, value.value)

    def getStart(self):
        return self._getNumber(1)

    def setStart(self, value):
        self._setNumber(1, value)

    def getEnd(self):
        return self._getNumber(2)

    def setEnd(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(EarlyAccessAnimationParamsModel, self)._initialize()
        self._addNumberProperty('animationType')
        self._addNumberProperty('start', 0)
        self._addNumberProperty('end', 0)
