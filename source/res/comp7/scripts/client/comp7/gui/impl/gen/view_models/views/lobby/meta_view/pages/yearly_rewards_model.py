# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/yearly_rewards_model.py
from enum import Enum
from comp7.gui.impl.gen.view_models.views.lobby.enums import Rank
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.yearly_rewards_card_model import YearlyRewardsCardModel
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_base_model import ProgressionItemBaseModel

class BannerState(Enum):
    DEFAULT = 'default'
    NOTACCRUEDREWARDS = 'notAccruedRewards'
    REWARDSSELECTIONAVAILABLE = 'rewardsSelectionAvailable'
    REWARDSRECEIVED = 'rewardsReceived'


class YearlyRewardsModel(ViewModel):
    __slots__ = ('onGoToStylePreview', 'onGoToVehiclePreview', 'onGoToRewardsSelection', 'onIntroViewed')

    def __init__(self, properties=8, commands=4):
        super(YearlyRewardsModel, self).__init__(properties=properties, commands=commands)

    def getCards(self):
        return self._getArray(0)

    def setCards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCardsType():
        return YearlyRewardsCardModel

    def getBannerState(self):
        return BannerState(self._getString(1))

    def setBannerState(self, value):
        self._setString(1, value.value)

    def getCurrentRank(self):
        return Rank(self._getNumber(2))

    def setCurrentRank(self, value):
        self._setNumber(2, value.value)

    def getIsQualificationActive(self):
        return self._getBool(3)

    def setIsQualificationActive(self, value):
        self._setBool(3, value)

    def getHasDataError(self):
        return self._getBool(4)

    def setHasDataError(self, value):
        self._setBool(4, value)

    def getWithIntro(self):
        return self._getBool(5)

    def setWithIntro(self, value):
        self._setBool(5, value)

    def getRanks(self):
        return self._getArray(6)

    def setRanks(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRanksType():
        return ProgressionItemBaseModel

    def getTopPercentage(self):
        return self._getNumber(7)

    def setTopPercentage(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(YearlyRewardsModel, self)._initialize()
        self._addArrayProperty('cards', Array())
        self._addStringProperty('bannerState')
        self._addNumberProperty('currentRank')
        self._addBoolProperty('isQualificationActive', False)
        self._addBoolProperty('hasDataError', False)
        self._addBoolProperty('withIntro', True)
        self._addArrayProperty('ranks', Array())
        self._addNumberProperty('topPercentage', 0)
        self.onGoToStylePreview = self._addCommand('onGoToStylePreview')
        self.onGoToVehiclePreview = self._addCommand('onGoToVehiclePreview')
        self.onGoToRewardsSelection = self._addCommand('onGoToRewardsSelection')
        self.onIntroViewed = self._addCommand('onIntroViewed')
