# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/yearly_rewards_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_rewards_card_model import YearlyRewardsCardModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class BannerState(Enum):
    DEFAULT = 'default'
    NOTACCRUEDREWARDS = 'notAccruedRewards'
    REWARDSSELECTIONAVAILABLE = 'rewardsSelectionAvailable'
    REWARDSRECEIVED = 'rewardsReceived'


class YearlyRewardsModel(ViewModel):
    __slots__ = ('onGoToStylePreview', 'onGoToVehiclePreview', 'onGoToRewardsSelection')
    DEFAULT_CARD_INDEX = -1

    def __init__(self, properties=9, commands=3):
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

    def getHasInitialCardsAnimation(self):
        return self._getBool(5)

    def setHasInitialCardsAnimation(self, value):
        self._setBool(5, value)

    def getInitialCardIndex(self):
        return self._getNumber(6)

    def setInitialCardIndex(self, value):
        self._setNumber(6, value)

    def getRanks(self):
        return self._getArray(7)

    def setRanks(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRanksType():
        return ProgressionItemBaseModel

    def getTopPercentage(self):
        return self._getNumber(8)

    def setTopPercentage(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(YearlyRewardsModel, self)._initialize()
        self._addArrayProperty('cards', Array())
        self._addStringProperty('bannerState')
        self._addNumberProperty('currentRank')
        self._addBoolProperty('isQualificationActive', False)
        self._addBoolProperty('hasDataError', False)
        self._addBoolProperty('hasInitialCardsAnimation', False)
        self._addNumberProperty('initialCardIndex', -1)
        self._addArrayProperty('ranks', Array())
        self._addNumberProperty('topPercentage', 0)
        self.onGoToStylePreview = self._addCommand('onGoToStylePreview')
        self.onGoToVehiclePreview = self._addCommand('onGoToVehiclePreview')
        self.onGoToRewardsSelection = self._addCommand('onGoToRewardsSelection')
