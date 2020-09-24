# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/blueprints/__init__.py
from account_helpers.AccountSettings import AccountSettings
from account_helpers.AccountSettings import BLUEPRINTS_STORAGE_FILTER
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import BasicCriteriesGroup
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CriteriesGroup
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup, CarouselFilter
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleName
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.impl import backport
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.requesters.ItemsRequester import RequestCriteria, PredicateCondition
from helpers import dependency, func_utils
from helpers.i18n import makeString
from skeletons.gui.shared import IItemsCache
from gui.shared import events

def blueprintExitEvent():
    return events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STORAGE), ctx={'defaultSection': STORAGE_CONSTANTS.BLUEPRINTS})


class _BlueprintsCriteriesGroup(CriteriesGroup):
    __itemsCache = dependency.descriptor(IItemsCache)

    def update(self, filters):
        super(_BlueprintsCriteriesGroup, self).update(filters)
        self._criteria |= RequestCriteria(PredicateCondition(self.__hasProgress))

    @staticmethod
    def isApplicableFor(vehicle):
        return True

    def __hasProgress(self, vehicle):
        data = self.__itemsCache.items.blueprints.getBlueprintData(vehicle.intCD, vehicle.level)
        if data is None:
            return False
        else:
            return 0 < data.filledCount < data.totalCount or data.canConvert


class ExtendedCriteriesGroup(BasicCriteriesGroup):
    __itemsCache = dependency.descriptor(IItemsCache)

    def update(self, filters):
        super(ExtendedCriteriesGroup, self).update(filters)
        if filters['unlock_available']:
            self._criteria |= RequestCriteria(PredicateCondition(self.__availableToUnlock))
        if filters['can_convert']:
            self._criteria |= RequestCriteria(PredicateCondition(self.__canConvert))

    def __availableToUnlock(self, vehicle):
        unlockAvailable, _ = g_techTreeDP.isNext2Unlock(vehicle.intCD, unlocked=self.__itemsCache.items.stats.unlocks, xps=self.__itemsCache.items.stats.vehiclesXPs, freeXP=self.__itemsCache.items.stats.actualFreeXP, level=vehicle.level)
        return unlockAvailable

    def __canConvert(self, vehicle):
        data = self.__itemsCache.items.blueprints.getBlueprintData(vehicle.intCD, vehicle.level)
        return False if data is None else data.canConvert


class BlueprintsStorageCarouselFilter(CarouselFilter):

    def __init__(self, criteries=None):
        super(BlueprintsStorageCarouselFilter, self).__init__()
        self._serverSections += (BLUEPRINTS_STORAGE_FILTER,)
        self._criteriesGroups = (EventCriteriesGroup(), ExtendedCriteriesGroup(), _BlueprintsCriteriesGroup()) + (criteries or tuple())

    def load(self):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        self._filters = defaultFilters
        self.update(defaultFilters, save=False)

    def save(self):
        pass


class BlueprintsStorageCarouselDataProvider(StorageCarouselDataProvider):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, carouselFilter, itemsCache, currentVehicle, filterCallback):
        super(BlueprintsStorageCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        g_techTreeDP.load()
        self._baseCriteria = self.filter.criteria
        self.__filterCallback = filterCallback

    def applyFilter(self, forceApply=False):
        self._buildVehicleItems()
        super(BlueprintsStorageCarouselDataProvider, self).applyFilter(forceApply=forceApply)
        if self.__filterCallback is not None:
            self.__filterCallback()
        return

    def _filterByIndices(self):
        self._vehicleItems = [ self._vehicleItems[ndx] for ndx in self._filteredIndices ]
        self.refresh()

    def _getSortedIndices(self):
        return self._getCachedSortedIndices(True)

    def _buildVehicle(self, item):
        bpRequester = self._itemsCache.items.blueprints
        name = getVehicleName(vehicle=item)
        intelligenceIcon = RES_ICONS.getBlueprintFragment('small', 'intelligence')
        nationalIcon = RES_ICONS.getBlueprintFragment('small', item.nationName)
        current, total = bpRequester.getBlueprintCount(item.intCD, item.level)
        nationalCost, intelligenceCost = bpRequester.getRequiredIntelligenceAndNational(item.level)
        availableCount = bpRequester.getConvertibleFragmentCount(item.intCD, item.level)
        if availableCount > 0:
            description = self.__getConvertAvailableDescription(availableCount)
        else:
            existingNational = bpRequester.getNationalFragments(item.intCD)
            existingIntelligence = bpRequester.getIntelligenceData()
            intelligenceRequired = max((0, intelligenceCost - existingIntelligence))
            nationalRequired = max((0, nationalCost - existingNational))
            description = self.__getConvertRequiredDescription(intelligenceRequired, intelligenceIcon, nationalRequired, nationalIcon)
        availableToUnlock, _ = g_techTreeDP.isNext2Unlock(item.intCD, unlocked=self._itemsCache.items.stats.unlocks, xps=self._itemsCache.items.stats.vehiclesXPs, freeXP=self._itemsCache.items.stats.actualFreeXP, level=item.level)
        fragmentsCostText = self.__formatFragmentsCost(intelligenceCost=intelligenceCost, intelligenceIcon=intelligenceIcon, nationalCost=nationalCost, nationalIcon=nationalIcon)
        discount = bpRequester.getBlueprintDiscount(item.intCD, item.level)
        fragmentsProgress = self.__formatFragmentProgress(current, total, discount)
        image = func_utils.makeFlashPath(item.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL))
        return {'id': item.intCD,
         'title': name,
         'description': description,
         'image': image,
         'imageAlt': RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_SMALL, 'empty_tank'),
         'fragmentsCostText': fragmentsCostText,
         'fragmentsProgress': fragmentsProgress,
         'hasDiscount': discount > 0,
         'availableToUnlock': availableToUnlock,
         'convertAvailable': availableCount > 0,
         'contextMenuId': CONTEXT_MENU_HANDLER_TYPE.STORAGE_BLUEPRINTS_ITEM}

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        blueprints = cls.__itemsCache.items.blueprints
        current, total = blueprints.getBlueprintCount(vehicle.intCD, vehicle.level)
        return (not vehicle.isInInventory,
         GUI_NATIONS_ORDER_INDEX_REVERSED.get(vehicle.nationName),
         current > 0,
         total,
         current)

    @classmethod
    def __formatFragmentProgress(cls, current, total, discount):
        return text_styles.alignText(''.join((text_styles.credits(backport.getIntegralFormat(current)), text_styles.main(''.join((' / ', backport.getIntegralFormat(total)))), text_styles.credits(''.join(('   ', backport.getIntegralFormat(discount), '%'))) if discount > 0 else '')), 'right')

    @classmethod
    def __formatFragment(cls, count, icon):
        return text_styles.concatStylesWithSpace(text_styles.stats(int(count)), icons.makeImageTag(source=icon, width=20, height=16))

    @classmethod
    def __formatFragmentsCost(cls, intelligenceCost, intelligenceIcon, nationalCost, nationalIcon):
        return text_styles.concatStylesWithSpace(cls.__formatFragment(intelligenceCost, intelligenceIcon), text_styles.main('+ '), cls.__formatFragment(nationalCost, nationalIcon))

    @classmethod
    def __getConvertAvailableDescription(cls, availableFragments):
        return makeString(STORAGE.BLUEPRINTS_CARD_CONVERTAVAILABLE, count=text_styles.stats(backport.getIntegralFormat(availableFragments)))

    @classmethod
    def __getConvertRequiredDescription(cls, intelligenceRequired, intelligenceIcon, nationalRequired, nationalIcon):
        description = text_styles.error(STORAGE.BLUEPRINTS_CARD_CONVERTREQUIRED)
        if intelligenceRequired > 0:
            description = ''.join((description, ' ', cls.__formatFragment(intelligenceRequired, intelligenceIcon)))
        if nationalRequired > 0:
            description = ''.join((description, ' ', cls.__formatFragment(nationalRequired, nationalIcon)))
        return description
