# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_royale_results_view_model.py
from frameworks.wulf import ViewModel
from frameworks.wulf import View

class BattleRoyaleResultsViewModel(ViewModel):
    __slots__ = ()

    def getSummaryResults(self):
        return self._getView(0)

    def setSummaryResults(self, value):
        self._setView(0, value)

    def getScoreResults(self):
        return self._getView(1)

    def setScoreResults(self, value):
        self._setView(1, value)

    def getIsAnimInProgress(self):
        return self._getBool(2)

    def setIsAnimInProgress(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattleRoyaleResultsViewModel, self)._initialize()
        self._addViewProperty('summaryResults')
        self._addViewProperty('scoreResults')
        self._addBoolProperty('isAnimInProgress', True)
