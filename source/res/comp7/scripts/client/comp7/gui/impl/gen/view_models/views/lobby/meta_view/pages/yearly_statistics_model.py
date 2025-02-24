# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/yearly_statistics_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.yearly_statistics_season_model import YearlyStatisticsSeasonModel

class YearlyStatisticsModel(ViewModel):
    __slots__ = ('onGoToSeasonStatistics',)

    def __init__(self, properties=1, commands=1):
        super(YearlyStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getSeasonCards(self):
        return self._getArray(0)

    def setSeasonCards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSeasonCardsType():
        return YearlyStatisticsSeasonModel

    def _initialize(self):
        super(YearlyStatisticsModel, self)._initialize()
        self._addArrayProperty('seasonCards', Array())
        self.onGoToSeasonStatistics = self._addCommand('onGoToSeasonStatistics')
