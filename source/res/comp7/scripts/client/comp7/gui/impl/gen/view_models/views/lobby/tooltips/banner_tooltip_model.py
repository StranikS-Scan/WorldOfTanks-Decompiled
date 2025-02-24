# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/banner_tooltip_model.py
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonModel

class BannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BannerTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def season(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonType():
        return SeasonModel

    def getTimeLeftUntilPrimeTime(self):
        return self._getNumber(1)

    def setTimeLeftUntilPrimeTime(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BannerTooltipModel, self)._initialize()
        self._addViewModelProperty('season', SeasonModel())
        self._addNumberProperty('timeLeftUntilPrimeTime', 0)
