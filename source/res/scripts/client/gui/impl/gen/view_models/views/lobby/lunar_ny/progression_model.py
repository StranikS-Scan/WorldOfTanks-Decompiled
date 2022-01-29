# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.progression_level_model import ProgressionLevelModel

class ProgressionModel(ViewModel):
    __slots__ = ('onAnimationProgressionEnd',)

    def __init__(self, properties=3, commands=1):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    def getEnvelopesSent(self):
        return self._getNumber(0)

    def setEnvelopesSent(self, value):
        self._setNumber(0, value)

    def getLastViewedEnvelopesSent(self):
        return self._getNumber(1)

    def setLastViewedEnvelopesSent(self, value):
        self._setNumber(1, value)

    def getProgressionLevels(self):
        return self._getArray(2)

    def setProgressionLevels(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addNumberProperty('envelopesSent', 0)
        self._addNumberProperty('lastViewedEnvelopesSent', 0)
        self._addArrayProperty('progressionLevels', Array())
        self.onAnimationProgressionEnd = self._addCommand('onAnimationProgressionEnd')
