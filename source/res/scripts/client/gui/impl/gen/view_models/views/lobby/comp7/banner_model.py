# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/banner_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonModel

class BannerModel(ViewModel):
    __slots__ = ('onOpen',)

    def __init__(self, properties=3, commands=1):
        super(BannerModel, self).__init__(properties=properties, commands=commands)

    @property
    def season(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonType():
        return SeasonModel

    def getIsSingle(self):
        return self._getBool(1)

    def setIsSingle(self, value):
        self._setBool(1, value)

    def getTimeLeftUntilPrimeTime(self):
        return self._getNumber(2)

    def setTimeLeftUntilPrimeTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BannerModel, self)._initialize()
        self._addViewModelProperty('season', SeasonModel())
        self._addBoolProperty('isSingle', True)
        self._addNumberProperty('timeLeftUntilPrimeTime', 0)
        self.onOpen = self._addCommand('onOpen')
