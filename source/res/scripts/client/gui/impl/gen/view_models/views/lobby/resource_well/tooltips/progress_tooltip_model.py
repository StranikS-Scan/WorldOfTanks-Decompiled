# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/tooltips/progress_tooltip_model.py
from frameworks.wulf import ViewModel

class ProgressTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ProgressTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getReal(0)

    def setCurrentProgress(self, value):
        self._setReal(0, value)

    def getProgressDiff(self):
        return self._getReal(1)

    def setProgressDiff(self, value):
        self._setReal(1, value)

    def getNeedShowDiff(self):
        return self._getBool(2)

    def setNeedShowDiff(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ProgressTooltipModel, self)._initialize()
        self._addRealProperty('currentProgress', 0.0)
        self._addRealProperty('progressDiff', 0.0)
        self._addBoolProperty('needShowDiff', False)
