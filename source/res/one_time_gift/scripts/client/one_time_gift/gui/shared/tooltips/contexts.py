# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/shared/tooltips/contexts.py
from gui.shared.tooltips.contexts import ExtendedAwardContext

class OneTimeGiftVehicleContext(ExtendedAwardContext):

    def __init__(self, fieldsToExclude=None):
        super(OneTimeGiftVehicleContext, self).__init__(fieldsToExclude)
        self._showCrew = True
        self._showVehicleSlot = True
        self._allModulesAvailable = True
        self._showBuyPrice = True
        self._showUnlockPrice = True
        self._isAwardWindow = False

    def getStatsConfiguration(self, item):
        value = super(OneTimeGiftVehicleContext, self).getStatsConfiguration(item)
        value.sellPrice = True
        value.inventoryCount = True
        value.vehiclesCount = True
        value.futureRentals = True
        value.xp = True
        value.dailyXP = True
        return value

    def getParamsConfiguration(self, item):
        value = super(OneTimeGiftVehicleContext, self).getParamsConfiguration(item)
        value.simplifiedOnly = False
        return value

    def getStatusConfiguration(self, item):
        value = super(OneTimeGiftVehicleContext, self).getStatusConfiguration(item)
        value.showCustomStates = False
        return value
