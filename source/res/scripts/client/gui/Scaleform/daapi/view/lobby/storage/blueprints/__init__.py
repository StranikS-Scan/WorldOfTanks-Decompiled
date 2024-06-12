# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/blueprints/__init__.py
import nations
from account_helpers.AccountSettings import STORAGE_BLUEPRINTS_CAROUSEL_FILTER
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import BasicCriteriesGroup
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CriteriesGroup
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.Scaleform.daapi.view.lobby.storage.inhangar import StorageCarouselDataProvider, StorageCarouselFilter
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleName
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import getShopVehicleIconPath
from gui.shared.utils.requesters.ItemsRequester import RequestCriteria, PredicateCondition, REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache

def blueprintExitEvent():
    return events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STORAGE), ctx={'defaultSection': STORAGE_CONSTANTS.BLUEPRINTS})


class _BlueprintsCriteriesGroup(CriteriesGroup):
    __itemsCache = dependency.descriptor(IItemsCache)

    def update(self, filters):
        super(_BlueprintsCriteriesGroup, self).update(filters)
        self._criteria |= self.getGroupCriteria()

    @staticmethod
    def isApplicableFor(vehicle):
        return True

    @classmethod
    def getGroupCriteria(cls):
        return REQ_CRITERIA.CUSTOM(cls.__hasProgress)

    @classmethod
    def __hasProgress(cls, vehicle):
        data = cls.__itemsCache.items.blueprints.getBlueprintData(vehicle.intCD, vehicle.level)
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
        if self._earlyAccessController.isEnabled():
            self._criteria |= ~REQ_CRITERIA.CUSTOM(self.__earlyAccessVehiclesCriteria)

    @classmethod
    def __availableToUnlock(cls, vehicle):
        unlockAvailable, _ = g_techTreeDP.isNext2Unlock(vehicle.intCD, unlocked=cls.__itemsCache.items.stats.unlocks, xps=cls.__itemsCache.items.stats.vehiclesXPs, freeXP=cls.__itemsCache.items.stats.actualFreeXP, level=vehicle.level)
        return unlockAvailable

    @classmethod
    def __earlyAccessVehiclesCriteria(cls, vehicle):
        return vehicle.intCD in set(cls._earlyAccessController.getAffectedVehicles().keys()) or vehicle.intCD in cls._earlyAccessController.getBlockedVehicles()

    @classmethod
    def __canConvert(cls, vehicle):
        data = cls.__itemsCache.items.blueprints.getBlueprintData(vehicle.intCD, vehicle.level)
        return False if data is None else data.canConvert


class BlueprintsStorageCarouselFilter(StorageCarouselFilter):

    def __init__(self, criteries=None):
        super(BlueprintsStorageCarouselFilter, self).__init__()
        self._clientSections = (STORAGE_BLUEPRINTS_CAROUSEL_FILTER,)
        self._criteriesGroups = (EventCriteriesGroup(), ExtendedCriteriesGroup(), _BlueprintsCriteriesGroup()) + (criteries or tuple())


class BlueprintsStorageCarouselDataProvider(StorageCarouselDataProvider):
    __itemsCache = dependency.descriptor(IItemsCache)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, carouselFilter, itemsCache, filterCallback):
        super(BlueprintsStorageCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        g_techTreeDP.load()
        self._baseCriteria = _BlueprintsCriteriesGroup.getGroupCriteria() | ~REQ_CRITERIA.VEHICLE.HIDDEN_IN_HANGAR
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

    def _buildVehicle(self, item):
        bpRequester = self._itemsCache.items.blueprints
        name = getVehicleName(vehicle=item)
        intelligenceIcon = RES_ICONS.getBlueprintFragment('special', 'intelligence')
        current, total = bpRequester.getBlueprintCount(item.intCD, item.level)
        _, intelligenceCost = bpRequester.getRequiredIntelligenceAndNational(item.level)
        nationalsCost = bpRequester.getNationalRequiredOptions(item.intCD, item.level)
        availableCount = bpRequester.getConvertibleFragmentCount(item.intCD, item.level)
        if availableCount > 0:
            description = makeString(STORAGE.BLUEPRINTS_CARD_CONVERTAVAILABLE, count=text_styles.stats(backport.getIntegralFormat(availableCount)))
        else:
            description = text_styles.error(STORAGE.BLUEPRINTS_CARD_CONVERTREQUIRED)
        availableToUnlock, _ = g_techTreeDP.isNext2Unlock(item.intCD, unlocked=self._itemsCache.items.stats.unlocks, xps=self._itemsCache.items.stats.vehiclesXPs, freeXP=self._itemsCache.items.stats.actualFreeXP, level=item.level)
        intelligenceCostText, fragmentsCost = self.__formatFragmentsCost(intelligenceCost=intelligenceCost, intelligenceIcon=intelligenceIcon, nationalsCost=nationalsCost)
        discount = bpRequester.getBlueprintDiscount(item.intCD, item.level)
        fragmentsProgress = self.__formatFragmentProgress(current, total, discount)
        image = item.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL)
        return {'id': item.intCD,
         'title': name,
         'description': description,
         'image': image,
         'imageAlt': getShopVehicleIconPath(STORE_CONSTANTS.ICON_SIZE_SMALL, 'empty_tank'),
         'fragmentsCost': fragmentsCost,
         'intelligenceCostText': intelligenceCostText,
         'fragmentsProgress': fragmentsProgress,
         'hasDiscount': discount > 0,
         'availableToUnlock': availableToUnlock,
         'convertAvailable': availableCount > 0,
         'contextMenuId': CONTEXT_MENU_HANDLER_TYPE.STORAGE_BLUEPRINTS_ITEM}

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (GUI_NATIONS_ORDER_INDEX.get(vehicle.nationName), -vehicle.level, vehicle.userName)

    def __formatFragmentProgress(self, current, total, discount):
        return text_styles.alignText(''.join((text_styles.credits(backport.getIntegralFormat(current)), text_styles.main(''.join((' / ', backport.getIntegralFormat(total)))), text_styles.credits(''.join(('   ', backport.getIntegralFormat(discount), '%'))) if discount > 0 else '')), 'right')

    def __formatFragment(self, count, icon, iconWidth=23):
        return text_styles.concatStylesWithSpace(text_styles.stats(int(count)), icons.makeImageTag(source=icon, width=iconWidth, height=16))

    def __formatFragmentsCost(self, intelligenceCost, intelligenceIcon, nationalsCost):
        intelligenceCostText = text_styles.concatStylesWithSpace(self.__formatFragment(intelligenceCost, intelligenceIcon, 19), text_styles.mainBig(backport.text(R.strings.storage.blueprints.card.plus())), text_styles.main(backport.text(R.strings.storage.blueprints.card.additional())))
        nationalCostTexts = []
        lastPriceIdx = len(nationalsCost) - 1
        for index, (nId, cost) in enumerate(nationalsCost.iteritems()):
            nationName = nations.MAP[nId]
            nationalsCost = self.__gui.systemLocale.getNumberFormat(cost)
            nationalIcon = backport.image(R.images.gui.maps.icons.blueprints.fragment.special.dyn(nationName)())
            nationalCostTexts.append({'costStr': self.__formatFragment(nationalsCost, nationalIcon),
             'delimeterOffset': -5,
             'hasDelimeter': index < lastPriceIdx})

        return (intelligenceCostText, nationalCostTexts)
