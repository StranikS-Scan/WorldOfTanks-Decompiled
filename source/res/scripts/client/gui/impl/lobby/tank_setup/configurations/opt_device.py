# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/configurations/opt_device.py
import operator
from account_helpers.AccountSettings import AccountSettings, SHOW_OPT_DEVICE_HINT_TROPHY, SHOW_OPT_DEVICE_HINT
from gui.impl.auxiliary.selected_filters import BaseSelectedFilters
from gui.impl.lobby.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider, DeluxeOptDeviceProvider
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.supply_slots_components import SlotCategories
from skeletons.gui.shared import IItemsCache

class OptDeviceTabs(object):
    SIMPLE = 'simple'
    SPECIAL = 'special'
    ALL = (SIMPLE, SPECIAL)


def getOptDeviceTabByItem(item):
    if item is None:
        return OptDeviceTabs.SIMPLE
    else:
        return OptDeviceTabs.SPECIAL if item.isDeluxe or item.isTrophy else OptDeviceTabs.SIMPLE


class OptDeviceTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return OptDeviceTabs.SIMPLE

    @tabUpdateFunc(OptDeviceTabs.SIMPLE)
    def _updateSimple(self, viewModel, isFirst=False):
        pass

    @tabUpdateFunc(OptDeviceTabs.SPECIAL)
    def _updateDeluxe(self, viewModel, isFirst=False):
        if isFirst:
            if OptDeviceIntroductionController.getIntroduction(OptDeviceTabs.SPECIAL):
                viewModel.setNewItemsCount(1)
        elif viewModel.getNewItemsCount() != 0 and not OptDeviceIntroductionController.getIntroduction(OptDeviceTabs.SPECIAL):
            viewModel.setNewItemsCount(0)

    def tabOrderKey(self, tabName):
        return OptDeviceTabs.ALL.index(tabName)

    def _getAllProviders(self):
        return {OptDeviceTabs.SIMPLE: SimpleOptDeviceProvider,
         OptDeviceTabs.SPECIAL: DeluxeOptDeviceProvider}


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
    SETTINGS = {TROPHY_INTRO: SHOW_OPT_DEVICE_HINT_TROPHY,
     DELUXE_INTRO: SHOW_OPT_DEVICE_HINT}

    @classmethod
    def getIntroduction(cls, tabName):
        result = None
        if tabName == OptDeviceTabs.SPECIAL:
            result = cls._getTrophyIntroduction()
            if result is None:
                result = cls._getDeluxeIntroduction()
        return result

    @classmethod
    def _getTrophyIntroduction(cls):
        prefSetting = AccountSettings.getSettings(SHOW_OPT_DEVICE_HINT_TROPHY)
        return cls.TROPHY_INTRO if prefSetting and cls.itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.OPTIONAL_DEVICE.TROPHY | REQ_CRITERIA.INVENTORY_OR_UNLOCKED) else None

    @classmethod
    def _getDeluxeIntroduction(cls):
        prefSetting = AccountSettings.getSettings(SHOW_OPT_DEVICE_HINT)
        return cls.DELUXE_INTRO if prefSetting else None

    @classmethod
    def _getIntroductionValue(cls, introName):
        settingName = cls.SETTINGS.get(introName)
        return AccountSettings.getSettings(settingName) if settingName is not None else False

    @classmethod
    def setIntroductionValue(cls, introName):
        settingName = cls.SETTINGS.get(introName)
        if settingName is not None:
            AccountSettings.setSettings(settingName, False)
        return
