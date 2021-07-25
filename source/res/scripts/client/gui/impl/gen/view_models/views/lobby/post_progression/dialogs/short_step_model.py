# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/dialogs/short_step_model.py
from frameworks.wulf import ViewModel

class ShortStepModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ShortStepModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ShortStepModel, self)._initialize()
        self._addNumberProperty('level', 0)
