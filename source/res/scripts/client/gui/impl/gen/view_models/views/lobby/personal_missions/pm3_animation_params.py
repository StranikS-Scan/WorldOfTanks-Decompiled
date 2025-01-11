# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_animation_params.py
from frameworks.wulf import ViewModel

class Pm3AnimationParams(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(Pm3AnimationParams, self).__init__(properties=properties, commands=commands)

    def getStart(self):
        return self._getNumber(0)

    def setStart(self, value):
        self._setNumber(0, value)

    def getEnd(self):
        return self._getNumber(1)

    def setEnd(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(Pm3AnimationParams, self)._initialize()
        self._addNumberProperty('start', 0)
        self._addNumberProperty('end', 0)
