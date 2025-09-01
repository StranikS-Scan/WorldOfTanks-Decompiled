# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/research_purchase_model.py
from frameworks.wulf import ViewModel

class ResearchPurchaseModel(ViewModel):
    __slots__ = ('onAction', 'onBlueprint')
    ACTION_RESEARCH = 'action_research'
    ACTION_PURCHASE = 'action_purchase'
    ACTION_PURCHASE_SHOP = 'action_purchase_shop'
    ACTION_RESTORE = 'action_restore'
    ACTION_IN_GARAGE = 'action_in_garage'
    ACTION_STATE_ENABLED = 'action_state_enabled'
    ACTION_STATE_DISABLED = 'action_state_disabled'
    ACTION_DESC_NOT_ENOUGH_CREDITS = 'notEnoughCredits'
    ACTION_DESC_NOT_ENOUGH_XP = 'notEnoughXp'
    ACTION_DESC_PARENT_MODULE_IS_LOCKED = 'parentModuleIsLocked'
    ACTION_DESC_WALLET_UNAVAILABLE = 'walletUnavailable'
    ACTION_DESC_RESTORE_REQUESTED = 'restoreRequested'

    def __init__(self, properties=18, commands=2):
        super(ResearchPurchaseModel, self).__init__(properties=properties, commands=commands)

    def getAction(self):
        return self._getString(0)

    def setAction(self, value):
        self._setString(0, value)

    def getActionState(self):
        return self._getString(1)

    def setActionState(self, value):
        self._setString(1, value)

    def getActionStateReason(self):
        return self._getString(2)

    def setActionStateReason(self, value):
        self._setString(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getOldPrice(self):
        return self._getNumber(4)

    def setOldPrice(self, value):
        self._setNumber(4, value)

    def getPriceDiscount(self):
        return self._getNumber(5)

    def setPriceDiscount(self, value):
        self._setNumber(5, value)

    def getCurrency(self):
        return self._getString(6)

    def setCurrency(self, value):
        self._setString(6, value)

    def getBlueprintFragments(self):
        return self._getNumber(7)

    def setBlueprintFragments(self, value):
        self._setNumber(7, value)

    def getBlueprintTotal(self):
        return self._getNumber(8)

    def setBlueprintTotal(self, value):
        self._setNumber(8, value)

    def getCombatXp(self):
        return self._getNumber(9)

    def setCombatXp(self, value):
        self._setNumber(9, value)

    def getFreeXp(self):
        return self._getNumber(10)

    def setFreeXp(self, value):
        self._setNumber(10, value)

    def getTimeLeft(self):
        return self._getNumber(11)

    def setTimeLeft(self, value):
        self._setNumber(11, value)

    def getCooldownTimeLeft(self):
        return self._getNumber(12)

    def setCooldownTimeLeft(self, value):
        self._setNumber(12, value)

    def getNotInShopVehicle(self):
        return self._getBool(13)

    def setNotInShopVehicle(self, value):
        self._setBool(13, value)

    def getPromoTitle(self):
        return self._getString(14)

    def setPromoTitle(self, value):
        self._setString(14, value)

    def getPromoFinishTime(self):
        return self._getNumber(15)

    def setPromoFinishTime(self, value):
        self._setNumber(15, value)

    def getPremium(self):
        return self._getBool(16)

    def setPremium(self, value):
        self._setBool(16, value)

    def getElite(self):
        return self._getBool(17)

    def setElite(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(ResearchPurchaseModel, self)._initialize()
        self._addStringProperty('action', '')
        self._addStringProperty('actionState', '')
        self._addStringProperty('actionStateReason', '')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('oldPrice', 0)
        self._addNumberProperty('priceDiscount', 0)
        self._addStringProperty('currency', '')
        self._addNumberProperty('blueprintFragments', 0)
        self._addNumberProperty('blueprintTotal', 0)
        self._addNumberProperty('combatXp', 0)
        self._addNumberProperty('freeXp', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('cooldownTimeLeft', 0)
        self._addBoolProperty('notInShopVehicle', False)
        self._addStringProperty('promoTitle', '')
        self._addNumberProperty('promoFinishTime', 0)
        self._addBoolProperty('premium', False)
        self._addBoolProperty('elite', False)
        self.onAction = self._addCommand('onAction')
        self.onBlueprint = self._addCommand('onBlueprint')
