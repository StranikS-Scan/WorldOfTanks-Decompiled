# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/buy_package_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BuyPackageViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(BuyPackageViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def starterPackRewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getStarterPackRewardsType():
        return RewardItemModel

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getPrevPrice(self):
        return self._getNumber(2)

    def setPrevPrice(self, value):
        self._setNumber(2, value)

    def getChapterID(self):
        return self._getNumber(3)

    def setChapterID(self, value):
        self._setNumber(3, value)

    def getIsActive(self):
        return self._getBool(4)

    def setIsActive(self, value):
        self._setBool(4, value)

    def getIsPurchaseWithLevels(self):
        return self._getBool(5)

    def setIsPurchaseWithLevels(self, value):
        self._setBool(5, value)

    def getRemainingLevelsCount(self):
        return self._getNumber(6)

    def setRemainingLevelsCount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(BuyPackageViewModel, self)._initialize()
        self._addViewModelProperty('starterPackRewards', UserListModel())
        self._addNumberProperty('price', 0)
        self._addNumberProperty('prevPrice', 0)
        self._addNumberProperty('chapterID', 0)
        self._addBoolProperty('isActive', False)
        self._addBoolProperty('isPurchaseWithLevels', False)
        self._addNumberProperty('remainingLevelsCount', 0)
