# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_portal_awards_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_guaranteed_award import WtEventGuaranteedAward
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class currencyTooltipTypes(Enum):
    GOLD = 'gold'
    CREDITS = 'credits'


class WtEventPortalAwardsModel(WtEventPortalAwardsBaseModel):
    __slots__ = ('onAnimationEnded', 'onReRoll', 'onAnimationSettingChange')

    def __init__(self, properties=22, commands=7):
        super(WtEventPortalAwardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedAward(self):
        return self._getViewModel(9)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    def getIsBossLootBox(self):
        return self._getBool(10)

    def setIsBossLootBox(self, value):
        self._setBool(10, value)

    def getCurrencyTooltipType(self):
        return currencyTooltipTypes(self._getString(11))

    def setCurrencyTooltipType(self, value):
        self._setString(11, value.value)

    def getOpenedBoxesCount(self):
        return self._getNumber(12)

    def setOpenedBoxesCount(self, value):
        self._setNumber(12, value)

    def getRerollPrice(self):
        return self._getNumber(13)

    def setRerollPrice(self, value):
        self._setNumber(13, value)

    def getRerollCount(self):
        return self._getNumber(14)

    def setRerollCount(self, value):
        self._setNumber(14, value)

    def getIsRerollAffordable(self):
        return self._getBool(15)

    def setIsRerollAffordable(self, value):
        self._setBool(15, value)

    def getIsLaunchAnimated(self):
        return self._getBool(16)

    def setIsLaunchAnimated(self, value):
        self._setBool(16, value)

    def getCurrentCrystals(self):
        return self._getNumber(17)

    def setCurrentCrystals(self, value):
        self._setNumber(17, value)

    def getCurrentGold(self):
        return self._getNumber(18)

    def setCurrentGold(self, value):
        self._setNumber(18, value)

    def getCurrentCredits(self):
        return self._getNumber(19)

    def setCurrentCredits(self, value):
        self._setNumber(19, value)

    def getCurrentFreeExperience(self):
        return self._getNumber(20)

    def setCurrentFreeExperience(self, value):
        self._setNumber(20, value)

    def getIsWalletAvailable(self):
        return self._getBool(21)

    def setIsWalletAvailable(self, value):
        self._setBool(21, value)

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
