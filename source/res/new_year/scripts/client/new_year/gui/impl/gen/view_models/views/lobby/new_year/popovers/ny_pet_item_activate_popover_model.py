# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_pet_item_activate_popover_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import NyIndicatorType

class NyPetItemActivatePopoverModel(NyIndicatorType):
    __slots__ = ('onItemActivate', 'onItemAmountChange')

    def __init__(self, properties=9, commands=2):
        super(NyPetItemActivatePopoverModel, self).__init__(properties=properties, commands=commands)

    def getItemsInInventory(self):
        return self._getNumber(1)

    def setItemsInInventory(self, value):
        self._setNumber(1, value)

    def getLoyaltyPoints(self):
        return self._getNumber(2)

    def setLoyaltyPoints(self, value):
        self._setNumber(2, value)

    def getVitalityPoints(self):
        return self._getNumber(3)

    def setVitalityPoints(self, value):
        self._setNumber(3, value)

    def getPotentialLoyaltyPoints(self):
        return self._getNumber(4)

    def setPotentialLoyaltyPoints(self, value):
        self._setNumber(4, value)

    def getPotentialVitalityPoints(self):
        return self._getNumber(5)

    def setPotentialVitalityPoints(self, value):
        self._setNumber(5, value)

    def getIsOnboarding(self):
        return self._getBool(6)

    def setIsOnboarding(self, value):
        self._setBool(6, value)

    def getWasLeaderboardFinished(self):
        return self._getBool(7)

    def setWasLeaderboardFinished(self, value):
        self._setBool(7, value)

    def getMaxValue(self):
        return self._getNumber(8)

    def setMaxValue(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(NyPetItemActivatePopoverModel, self)._initialize()
        self._addNumberProperty('itemsInInventory', 0)
        self._addNumberProperty('loyaltyPoints', 0)
        self._addNumberProperty('vitalityPoints', 0)
        self._addNumberProperty('potentialLoyaltyPoints', 0)
        self._addNumberProperty('potentialVitalityPoints', 0)
        self._addBoolProperty('isOnboarding', False)
        self._addBoolProperty('wasLeaderboardFinished', False)
        self._addNumberProperty('maxValue', -1)
        self.onItemActivate = self._addCommand('onItemActivate')
        self.onItemAmountChange = self._addCommand('onItemAmountChange')
