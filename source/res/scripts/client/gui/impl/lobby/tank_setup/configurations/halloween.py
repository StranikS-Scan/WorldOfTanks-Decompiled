# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/configurations/halloween.py
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController, BaseDealPanel
from gui.impl.lobby.tank_setup.array_providers.halloween import HalloweenConsumableProvider

class ConsumableTabs(object):
    DEFAULT = 'default'
    ALL = (DEFAULT,)


class HalloweenTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return ConsumableTabs.DEFAULT

    @tabUpdateFunc(ConsumableTabs.DEFAULT)
    def _updateDefault(self, viewModel, isFirst=False):
        pass

    def tabOrderKey(self, tabName):
        return ConsumableTabs.ALL.index(tabName)

    def _getAllProviders(self):
        return {ConsumableTabs.DEFAULT: HalloweenConsumableProvider}


class HalloweenDealPanel(BaseDealPanel):

    @classmethod
    def addItem(cls, vehicle, item, prices):
        if item is None:
            return
        else:
            prices[cls._ON_VEHICLE_IN_SETUP] = False
            if item.isInInventory:
                prices[cls._IN_STORAGE] += 1
                return
            prices[cls._MONEY] += item.getBuyPrice().price
            return
