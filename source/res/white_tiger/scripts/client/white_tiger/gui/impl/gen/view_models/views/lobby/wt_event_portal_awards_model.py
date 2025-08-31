# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portal_awards_model.py
from enum import Enum
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_guaranteed_award import WtEventGuaranteedAward
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class currencyTooltipTypes(Enum):
    GOLD = 'gold'
    CREDITS = 'credits'


class WtEventPortalAwardsModel(WtEventPortalAwardsBaseModel):
    __slots__ = ('onAnimationEnded', 'onReRoll', 'onAnimationSettingChange')

    def __init__(self, properties=21, commands=8):
        super(WtEventPortalAwardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedAward(self):
        return self._getViewModel(8)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    def getIsBossLootBox(self):
        return self._getBool(9)

    def setIsBossLootBox(self, value):
        self._setBool(9, value)

    def getCurrencyTooltipType(self):
        return currencyTooltipTypes(self._getString(10))

    def setCurrencyTooltipType(self, value):
        self._setString(10, value.value)

    def getOpenedBoxesCount(self):
        return self._getNumber(11)

    def setOpenedBoxesCount(self, value):
        self._setNumber(11, value)

    def getRerollPrice(self):
        return self._getNumber(12)

    def setRerollPrice(self, value):
        self._setNumber(12, value)

    def getRerollCount(self):
        return self._getNumber(13)

    def setRerollCount(self, value):
        self._setNumber(13, value)

    def getIsRerollAffordable(self):
        return self._getBool(14)

    def setIsRerollAffordable(self, value):
        self._setBool(14, value)

    def getIsLaunchAnimated(self):
        return self._getBool(15)

    def setIsLaunchAnimated(self, value):
        self._setBool(15, value)

    def getCurrentCrystals(self):
        return self._getNumber(16)

    def setCurrentCrystals(self, value):
        self._setNumber(16, value)

    def getCurrentGold(self):
        return self._getNumber(17)

    def setCurrentGold(self, value):
        self._setNumber(17, value)

    def getCurrentCredits(self):
        return self._getNumber(18)

    def setCurrentCredits(self, value):
        self._setNumber(18, value)

    def getCurrentFreeExperience(self):
        return self._getNumber(19)

    def setCurrentFreeExperience(self, value):
        self._setNumber(19, value)

    def getIsWalletAvailable(self):
        return self._getBool(20)

    def setIsWalletAvailable(self, value):
        self._setBool(20, value)

    def _initialize(self):
        super(WtEventPortalAwardsModel, self)._initialize()
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addBoolProperty('isBossLootBox', False)
        self._addStringProperty('currencyTooltipType', currencyTooltipTypes.GOLD.value)
        self._addNumberProperty('openedBoxesCount', 0)
        self._addNumberProperty('rerollPrice', 500)
        self._addNumberProperty('rerollCount', 3)
        self._addBoolProperty('isRerollAffordable', False)
        self._addBoolProperty('isLaunchAnimated', False)
        self._addNumberProperty('currentCrystals', 0)
        self._addNumberProperty('currentGold', 0)
        self._addNumberProperty('currentCredits', 0)
        self._addNumberProperty('currentFreeExperience', 0)
        self._addBoolProperty('isWalletAvailable', False)
        self.onAnimationEnded = self._addCommand('onAnimationEnded')
        self.onReRoll = self._addCommand('onReRoll')
        self.onAnimationSettingChange = self._addCommand('onAnimationSettingChange')
