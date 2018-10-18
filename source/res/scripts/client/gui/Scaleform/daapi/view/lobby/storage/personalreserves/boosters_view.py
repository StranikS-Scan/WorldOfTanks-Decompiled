# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/personalreserves/boosters_view.py
from operator import attrgetter
from adisp import process
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyBoostersUrl
from gui.Scaleform.daapi.view.meta.StorageCategoryPersonalReservesViewMeta import StorageCategoryPersonalReservesViewMeta
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS as BC
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies.goodie_items import BOOSTERS_ORDERS, BOOSTER_QUALITY_NAMES, MAX_ACTIVE_BOOSTERS_COUNT
from gui.shared.event_dispatcher import showWebShop
from gui.shared.formatters import text_styles, getItemPricesVO
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.utils import decorators
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from shared_utils import CONST_CONTAINER
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IBoostersController
from gui.shared.utils.functions import makeTooltip

class _FilterBit(CONST_CONTAINER):
    QUALITY_SMALL = 1
    QUALITY_MEDIUM = 2
    QUALITY_BIG = 4
    XP = 8
    CREW_XP = 16
    FREE_XP = 32
    CREDITS = 64


_TYPE_BIT_TO_RESOURCE_TYPE_MAP = {_FilterBit.XP: GOODIE_RESOURCE_TYPE.XP,
 _FilterBit.CREW_XP: GOODIE_RESOURCE_TYPE.CREW_XP,
 _FilterBit.FREE_XP: GOODIE_RESOURCE_TYPE.FREE_XP,
 _FilterBit.CREDITS: GOODIE_RESOURCE_TYPE.CREDITS}
_QUALITY_BIT_TO_QUALITY_NAME_MAP = {_FilterBit.QUALITY_BIG: BOOSTER_QUALITY_NAMES.BIG,
 _FilterBit.QUALITY_MEDIUM: BOOSTER_QUALITY_NAMES.MEDIUM,
 _FilterBit.QUALITY_SMALL: BOOSTER_QUALITY_NAMES.SMALL}
_QUALITY_NAME_TO_LEVEL_MAP = {BOOSTER_QUALITY_NAMES.SMALL: 1,
 BOOSTER_QUALITY_NAMES.MEDIUM: 2,
 BOOSTER_QUALITY_NAMES.BIG: 3}
_QUALITY_FILTER_ITEMS = [{'filterValue': _FilterBit.QUALITY_SMALL,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_LEVEL_SMALL),
  'icon': RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_1}, {'filterValue': _FilterBit.QUALITY_MEDIUM,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_LEVEL_MEDIUM),
  'icon': RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_2}, {'filterValue': _FilterBit.QUALITY_BIG,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_LEVEL_BIG),
  'icon': RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_3}]
_TYPE_FILTER_ITEMS = [{'filterValue': _FilterBit.XP,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_VEHICLEEXP),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_XP_SMALL_BW},
 {'filterValue': _FilterBit.CREW_XP,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_CREWEXP),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_CREW_XP_SMALL_BW},
 {'filterValue': _FilterBit.FREE_XP,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_FREEEXP),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_FREE_XP_SMALL_BW},
 {'filterValue': _FilterBit.CREDITS,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_TYPE_CREDITS),
  'icon': RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_CREDITS_SMALL_BW}]

def getCriteriaFromFilterMask(filterMask):
    criteria = REQ_CRITERIA.EMPTY
    qualitySet = {_QUALITY_BIT_TO_QUALITY_NAME_MAP[bit] for bit in _QUALITY_BIT_TO_QUALITY_NAME_MAP.iterkeys() if filterMask & bit}
    if qualitySet:
        criteria |= REQ_CRITERIA.BOOSTER.QUALITY(qualitySet)
    typesSet = {_TYPE_BIT_TO_RESOURCE_TYPE_MAP[bit] for bit in _TYPE_BIT_TO_RESOURCE_TYPE_MAP.iterkeys() if filterMask & bit}
    if typesSet:
        criteria |= REQ_CRITERIA.BOOSTER.BOOSTER_TYPES(typesSet)
    return criteria


def getQualityLevel(quality):
    return _QUALITY_NAME_TO_LEVEL_MAP.get(quality)


class StorageCategoryPersonalReservesView(StorageCategoryPersonalReservesViewMeta):
    boosters = dependency.descriptor(IBoostersController)
    eventsCache = dependency.descriptor(IEventsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(StorageCategoryPersonalReservesView, self).__init__()
        self._boosters = []
        self.__filterMask = 0

    def navigateToStore(self):
        showWebShop(getBuyBoostersUrl())

    def resetFilter(self):
        self.__filterMask = 0
        self.as_resetFilterS(self.__filterMask)
        self.__onUpdateBoosters()

    def onFiltersChange(self, filterMask):
        self.__filterMask = filterMask
        self.__onUpdateBoosters()

    @process
    def activateReserve(self, boosterID):
        newBooster = self.goodiesCache.getBooster(boosterID)
        curBooster = self.__getActiveBoosterByType(newBooster.boosterType)
        shouldActivate = False
        if curBooster is None:
            shouldActivate |= (yield self.__canActivate(newBooster.description))
        else:
            shouldActivate |= (yield self.__canReplace(curBooster.description, newBooster.description))
        if shouldActivate:
            self.__activateBoosterRequest(newBooster)
        return

    def __canActivate(self, newBoosterDescription):
        return DialogsInterface.showDialog(I18nConfirmDialogMeta(BC.BOOSTER_ACTIVATION_CONFORMATION_TEXT_KEY, messageCtx={'newBoosterName': text_styles.middleTitle(newBoosterDescription)}, focusedID=DIALOG_BUTTON_ID.CLOSE))

    def __canReplace(self, curBoosterDescription, newBoosterDescription):
        return DialogsInterface.showDialog(I18nConfirmDialogMeta(BC.BOOSTER_REPLACE_CONFORMATION_TEXT_KEY, messageCtx={'newBoosterName': text_styles.middleTitle(newBoosterDescription),
         'curBoosterName': text_styles.middleTitle(curBoosterDescription)}, focusedID=DIALOG_BUTTON_ID.CLOSE))

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StorageCategoryPersonalReservesView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BOOSTERS_PANEL:
            viewPy.setSlotProps({'slotsCount': MAX_ACTIVE_BOOSTERS_COUNT,
             'slotWidth': 50,
             'paddings': 64,
             'groupPadding': 18,
             'ySlotPosition': 5,
             'offsetSlot': -2,
             'useOnlyLeftBtn': True})

    def _populate(self):
        super(StorageCategoryPersonalReservesView, self)._populate()
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateBoosters,
         'shop': self.__onUpdateBoosters})
        self.boosters.onBoosterChangeNotify += self.__onUpdateBoosters
        self.eventsCache.onSyncCompleted += self.__onQuestsUpdate
        self.__onUpdateBoosters()
        self.__initFilter()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.boosters.onBoosterChangeNotify -= self.__onUpdateBoosters
        self.eventsCache.onSyncCompleted -= self.__onQuestsUpdate
        super(StorageCategoryPersonalReservesView, self)._dispose()

    def _update(self, *args):
        self.__onUpdateBoosters()

    def __onUpdateBoosters(self, *args):
        activeBoostersCount = len(self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        totalBoostersCount = sum((x.count for x in self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_ACCOUNT).values()))
        filteredBoostersCount = 0
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
        criteria |= getCriteriaFromFilterMask(self.__filterMask)
        boosters = self.goodiesCache.getBoosters(criteria=criteria).values()
        dataProviderValues = []
        showDummyScreen = False
        filterWarningVO = None
        if boosters:
            for booster in sorted(boosters, cmp=self.__sort):
                mainText = text_styles.main(booster.getBonusDescription(valueFormatter=text_styles.neutral))
                romanLvl = getQualityLevel(booster.quality)
                vo = createStorageDefVO(booster.boosterID, mainText, mainText, booster.count, getItemPricesVO(booster.getSellPrice())[0], booster.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL), booster.getShopIcon(), 'altimage', enabled=booster.isReadyToActivate, level=int2roman(romanLvl) if romanLvl is not None else '')
                dataProviderValues.append(vo)
                filteredBoostersCount += booster.count

        elif totalBoostersCount == 0:
            showDummyScreen = True
        else:
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        self._dataProvider.buildList(*dataProviderValues)
        self.__updateFilterCounter(filteredBoostersCount, totalBoostersCount)
        self.__updateActiveBoostersCounter(activeBoostersCount, totalBoostersCount)
        self.as_showFilterWarningS(filterWarningVO)
        self.as_showDummyScreenS(showDummyScreen)
        return

    def __onQuestsUpdate(self, *args):
        self.__onUpdateBoosters()

    def __sort(self, a, b):
        return cmp(a.quality, b.quality) or cmp(BOOSTERS_ORDERS[a.boosterType], BOOSTERS_ORDERS[b.boosterType]) or cmp(b.effectValue, a.effectValue) or cmp(b.effectTime, a.effectTime)

    @classmethod
    def __getActiveBoosterByType(cls, bType):
        criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([bType])
        activeBoosters = cls.goodiesCache.getBoosters(criteria=criteria).values()
        return max(activeBoosters, key=attrgetter('effectValue')) if activeBoosters else None

    @decorators.process('loadStats')
    def __activateBoosterRequest(self, booster):
        result = yield BoosterActivator(booster).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __updateActiveBoostersCounter(self, active, total):
        self.as_initS({'activeText': text_styles.main(_ms(STORAGE.PERSONALRESERVES_ACTIVECOUNTLABEL, activeCount=text_styles.error(active) if active == 0 else text_styles.stats(active), totalCount=MAX_ACTIVE_BOOSTERS_COUNT)),
         'totalText': text_styles.main(_ms(STORAGE.PERSONALRESERVES_TOTALCOUNTLABEL, totalCount=text_styles.error(total) if total == 0 else text_styles.stats(total))),
         'hasActiveReserve': active != 0})

    def __initFilter(self):
        qualityFilters = {'items': _QUALITY_FILTER_ITEMS,
         'minSelectedItems': 0}
        typeFilters = {'items': _TYPE_FILTER_ITEMS,
         'minSelectedItems': 0}
        data = {'qualityFiltersLabel': STORAGE.PERSONALRESERVES_QUALITYFILTER_LABEL,
         'typeFiltersLabel': STORAGE.PERSONALRESERVES_TYPEFILTER_LABEL,
         'qualityFilters': qualityFilters,
         'typeFilters': typeFilters}
        self.as_initFilterS(data)

    def __updateFilterCounter(self, count, total):
        drawAttention = count == 0
        self.as_updateCounterS(self.__filterMask != 0, self._formatCountString(count, total), drawAttention)
