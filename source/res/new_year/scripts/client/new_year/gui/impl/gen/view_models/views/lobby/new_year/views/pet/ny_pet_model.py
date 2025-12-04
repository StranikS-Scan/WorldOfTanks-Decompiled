# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/ny_pet_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.pet_shop.ny_pet_shop import NyPetShop

class State(Enum):
    UNKNOWN = ''
    SAD = 'sad'
    NORMAL = 'normal'
    FUN = 'fun'


class IndicatorType(Enum):
    FOOD = 'food'
    FUN = 'fun'
    ACTIVITY = 'activity'


class SingleTipType(IntEnum):
    EMPTY = -1
    NEWSTORY = 1
    FUNOPENED = 2
    ACTIVITYOPENED = 3
    LEADERBOARD = 4


class NyPetModel(ViewModel):
    __slots__ = ('onLootBoxEntryPointClick', 'onOnboardingFinish', 'onResetWasOverflowed', 'onProgressFillSound', 'onDeleteItemLeaderboardPoint', 'onCloseSingleTip', 'onPetStateAnimationsChange', 'onShopClick', 'onStoryClick', 'onGetGift', 'onItemClick')

    def __init__(self, properties=21, commands=11):
        super(NyPetModel, self).__init__(properties=properties, commands=commands)

    @property
    def lootBox(self):
        return self._getViewModel(0)

    @staticmethod
    def getLootBoxType():
        return LootBoxEntryPointModel

    @property
    def shop(self):
        return self._getViewModel(1)

    @staticmethod
    def getShopType():
        return NyPetShop

    @property
    def foodIndicator(self):
        return self._getViewModel(2)

    @staticmethod
    def getFoodIndicatorType():
        return NyPetIndicatorModel

    @property
    def funIndicator(self):
        return self._getViewModel(3)

    @staticmethod
    def getFunIndicatorType():
        return NyPetIndicatorModel

    @property
    def activityIndicator(self):
        return self._getViewModel(4)

    @staticmethod
    def getActivityIndicatorType():
        return NyPetIndicatorModel

    def getPetNeeds(self):
        return self._getArray(5)

    def setPetNeeds(self, value):
        self._setArray(5, value)

    @staticmethod
    def getPetNeedsType():
        return IndicatorType

    def getHasPetAnimations(self):
        return self._getBool(6)

    def setHasPetAnimations(self, value):
        self._setBool(6, value)

    def getWasLeaderboardFinished(self):
        return self._getBool(7)

    def setWasLeaderboardFinished(self, value):
        self._setBool(7, value)

    def getIsOnboarding(self):
        return self._getBool(8)

    def setIsOnboarding(self, value):
        self._setBool(8, value)

    def getIsOnboardingVideoClosed(self):
        return self._getBool(9)

    def setIsOnboardingVideoClosed(self, value):
        self._setBool(9, value)

    def getSingleTip(self):
        return SingleTipType(self._getNumber(10))

    def setSingleTip(self, value):
        self._setNumber(10, value.value)

    def getNeedToCloseSingleTip(self):
        return self._getBool(11)

    def setNeedToCloseSingleTip(self, value):
        self._setBool(11, value)

    def getNewStoryOpenedNumber(self):
        return self._getNumber(12)

    def setNewStoryOpenedNumber(self, value):
        self._setNumber(12, value)

    def getIsPopoverOpened(self):
        return self._getBool(13)

    def setIsPopoverOpened(self, value):
        self._setBool(13, value)

    def getIsGuiLootBoxesVisible(self):
        return self._getBool(14)

    def setIsGuiLootBoxesVisible(self, value):
        self._setBool(14, value)

    def getGiftTime(self):
        return self._getNumber(15)

    def setGiftTime(self, value):
        self._setNumber(15, value)

    def getGiftCount(self):
        return self._getNumber(16)

    def setGiftCount(self, value):
        self._setNumber(16, value)

    def getMaxBonus(self):
        return self._getNumber(17)

    def setMaxBonus(self, value):
        self._setNumber(17, value)

    def getCurBonus(self):
        return self._getNumber(18)

    def setCurBonus(self, value):
        self._setNumber(18, value)

    def getState(self):
        return State(self._getString(19))

    def setState(self, value):
        self._setString(19, value.value)

    def getIsStoryEntryPointBubble(self):
        return self._getBool(20)

    def setIsStoryEntryPointBubble(self, value):
        self._setBool(20, value)

    def _initialize(self):
        super(NyPetModel, self)._initialize()
        self._addViewModelProperty('lootBox', LootBoxEntryPointModel())
        self._addViewModelProperty('shop', NyPetShop())
        self._addViewModelProperty('foodIndicator', NyPetIndicatorModel())
        self._addViewModelProperty('funIndicator', NyPetIndicatorModel())
        self._addViewModelProperty('activityIndicator', NyPetIndicatorModel())
        self._addArrayProperty('petNeeds', Array())
        self._addBoolProperty('hasPetAnimations', True)
        self._addBoolProperty('wasLeaderboardFinished', False)
        self._addBoolProperty('isOnboarding', False)
        self._addBoolProperty('isOnboardingVideoClosed', False)
        self._addNumberProperty('singleTip', SingleTipType.EMPTY.value)
        self._addBoolProperty('needToCloseSingleTip', False)
        self._addNumberProperty('newStoryOpenedNumber', 0)
        self._addBoolProperty('isPopoverOpened', False)
        self._addBoolProperty('isGuiLootBoxesVisible', False)
        self._addNumberProperty('giftTime', 0)
        self._addNumberProperty('giftCount', 0)
        self._addNumberProperty('maxBonus', 0)
        self._addNumberProperty('curBonus', 0)
        self._addStringProperty('state')
        self._addBoolProperty('isStoryEntryPointBubble', False)
        self.onLootBoxEntryPointClick = self._addCommand('onLootBoxEntryPointClick')
        self.onOnboardingFinish = self._addCommand('onOnboardingFinish')
        self.onResetWasOverflowed = self._addCommand('onResetWasOverflowed')
        self.onProgressFillSound = self._addCommand('onProgressFillSound')
        self.onDeleteItemLeaderboardPoint = self._addCommand('onDeleteItemLeaderboardPoint')
        self.onCloseSingleTip = self._addCommand('onCloseSingleTip')
        self.onPetStateAnimationsChange = self._addCommand('onPetStateAnimationsChange')
        self.onShopClick = self._addCommand('onShopClick')
        self.onStoryClick = self._addCommand('onStoryClick')
        self.onGetGift = self._addCommand('onGetGift')
        self.onItemClick = self._addCommand('onItemClick')
