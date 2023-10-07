# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/configurations/opt_device.py
import operator
from account_helpers.AccountSettings import AccountSettings, SHOW_OPT_DEVICE_HINT_TROPHY, SHOW_OPT_DEVICE_HINT, SHOW_OPT_MODERNIZED_DEVICE_HINT
from gui.impl.auxiliary.selected_filters import BaseSelectedFilters
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider, DeluxeOptDeviceProvider, TrophyOptDeviceProvider, ModernisedOptDeviceProvider
from gui.shared.money import Currency
from helpers import dependency
from items.components.supply_slots_components import SlotCategories
from skeletons.gui.shared import IItemsCache

class OptDeviceTabs(object):
    SIMPLE = 'simple'
    DELUXE = 'deluxe'
    TROPHY = 'trophy'
    MODERNIZED = 'modernized'
    ALL = (SIMPLE,
     TROPHY,
     DELUXE,
     MODERNIZED)


def getOptDeviceTabByItem(item):
    if item is None:
        return OptDeviceTabs.SIMPLE
    elif item.isDeluxe:
        return OptDeviceTabs.DELUXE
    elif item.isTrophy:
        return OptDeviceTabs.TROPHY
    else:
        return OptDeviceTabs.MODERNIZED if item.isModernized else OptDeviceTabs.SIMPLE


class OptDeviceTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return OptDeviceTabs.SIMPLE

    @tabUpdateFunc(OptDeviceTabs.SIMPLE)
    def _updateSimple(self, viewModel, isFirst=False):
        pass

    @tabUpdateFunc(OptDeviceTabs.MODERNIZED)
    def _updateModernized(self, viewModel, isFirst=False):
        self.__updateSpecial(viewModel, OptDeviceTabs.MODERNIZED, isFirst)

    @tabUpdateFunc(OptDeviceTabs.TROPHY)
    def _updateTrophy(self, viewModel, isFirst=False):
        self.__updateSpecial(viewModel, OptDeviceTabs.TROPHY, isFirst)

    @tabUpdateFunc(OptDeviceTabs.DELUXE)
    def _updateDeluxe(self, viewModel, isFirst=False):
        self.__updateSpecial(viewModel, OptDeviceTabs.DELUXE, isFirst)

    def tabOrderKey(self, tabName):
        return OptDeviceTabs.ALL.index(tabName)

    def getTabCurrency(self, tabName):
        return Currency.EQUIP_COIN if tabName == OptDeviceTabs.MODERNIZED else ''

    def _getAllProviders(self):
        return {OptDeviceTabs.SIMPLE: SimpleOptDeviceProvider,
         OptDeviceTabs.DELUXE: DeluxeOptDeviceProvider,
         OptDeviceTabs.TROPHY: TrophyOptDeviceProvider,
         OptDeviceTabs.MODERNIZED: ModernisedOptDeviceProvider}

    def __updateSpecial(self, viewModel, tabName, isFirst):
        if not self.isVisited(tabName):
            viewModel.setNewItemsCount(1)
        elif not isFirst and viewModel.getNewItemsCount() != 0:
            viewModel.setNewItemsCount(0)


class OptDeviceSelectedFilters(BaseSelectedFilters):
    __slots__ = ()
    FIREPOWER = SlotCategories.FIREPOWER
    SURVIVABILITY = SlotCategories.SURVIVABILITY
    MOBILITY = SlotCategories.MOBILITY
    STEALTH = SlotCategories.STEALTH

    def changeFilter(self, filterName, model):
        super(OptDeviceSelectedFilters, self).changeFilter(filterName, model)
        model.setSelectedCount(len(self._selectedFilters))

    def __init__(self):
        super(OptDeviceSelectedFilters, self).__init__()
        self._addFilter(self.FIREPOWER, self.__firepowerFilter, operator.or_)
        self._addFilter(self.SURVIVABILITY, self.__survivabilityFilter, operator.or_)
        self._addFilter(self.MOBILITY, self.__mobilityFilter, operator.or_)
        self._addFilter(self.STEALTH, self.__stealthFilter, operator.or_)

    @staticmethod
    def __firepowerFilter(item):
        return SlotCategories.FIREPOWER in item.descriptor.categories

    @staticmethod
    def __survivabilityFilter(item):
        return SlotCategories.SURVIVABILITY in item.descriptor.categories

    @staticmethod
    def __mobilityFilter(item):
        return SlotCategories.MOBILITY in item.descriptor.categories

    @staticmethod
    def __stealthFilter(item):
        return SlotCategories.STEALTH in item.descriptor.categories


class OptDeviceIntroductionController(object):
    itemsCache = dependency.descriptor(IItemsCache)
    TROPHY_INTRO = 'trophy'
    DELUXE_INTRO = 'deluxe'
    MODERNIZED_INTRO = 'modernized'
    SETTINGS = {TROPHY_INTRO: SHOW_OPT_DEVICE_HINT_TROPHY,
     DELUXE_INTRO: SHOW_OPT_DEVICE_HINT,
     MODERNIZED_INTRO: SHOW_OPT_MODERNIZED_DEVICE_HINT}
    INTRO_BY_TAB = {OptDeviceTabs.TROPHY: TROPHY_INTRO,
     OptDeviceTabs.DELUXE: DELUXE_INTRO,
     OptDeviceTabs.MODERNIZED: MODERNIZED_INTRO}

    @classmethod
    def getIntroduction(cls, tabName, hasItems):
        if tabName not in cls.INTRO_BY_TAB:
            return None
        else:
            intro = cls.INTRO_BY_TAB[tabName]
            isShown = not AccountSettings.getSettings(cls.SETTINGS[intro])
            return intro if not isShown or not hasItems else None

    @classmethod
    def setIntroductionValue(cls, introName):
        settingName = cls.SETTINGS.get(introName)
        if settingName is not None:
            AccountSettings.setSettings(settingName, False)
        return
