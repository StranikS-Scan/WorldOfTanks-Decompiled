# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/personalreserves/boosters_view.py
import copy
from account_helpers import AccountSettings
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO, isStorageSessionTimeout
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyBoostersUrl
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies.goodie_items import BOOSTERS_ORDERS, MAX_ACTIVE_BOOSTERS_COUNT
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showWebShop
from gui.shared.formatters import text_styles, getItemPricesVO
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, func_utils
from helpers.time_utils import ONE_HOUR
from helpers.i18n import makeString as _ms
from shared_utils import CONST_CONTAINER
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IBoostersController, IEpicBattleMetaGameController
from gui.shared.utils.functions import makeTooltip
from gui.shared import event_dispatcher as shared_events
from gui.Scaleform.daapi.view.meta.StorageCategoryPersonalReservesViewMeta import StorageCategoryPersonalReservesViewMeta

class _FilterBit(CONST_CONTAINER):
    XP = 1
    CREW_XP = 2
    FREE_XP = 4
    CREDITS = 8
    ONE = 16
    TWO = 32
    FOUR = 64
    SIX = 128


_TYPE_BIT_TO_RESOURCE_TYPE_MAP = {_FilterBit.XP: GOODIE_RESOURCE_TYPE.XP,
 _FilterBit.CREW_XP: GOODIE_RESOURCE_TYPE.CREW_XP,
 _FilterBit.FREE_XP: GOODIE_RESOURCE_TYPE.FREE_XP,
 _FilterBit.CREDITS: GOODIE_RESOURCE_TYPE.CREDITS}
_DURATION_BIT_TO_DURATION_VALUE = {_FilterBit.ONE: 1,
 _FilterBit.TWO: 2,
 _FilterBit.FOUR: 4,
 _FilterBit.SIX: 6}

def getDurationInSeconds(hour):
    return hour * ONE_HOUR


_DURATION_FILTER_ITEMS = [{'filterValue': _FilterBit.ONE,
  'selected': False,
  'tooltip': makeTooltip(body=_ms(TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_DURATION, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.ONE))),
  'label': _ms(STORAGE.PERSONALRESERVES_DURATIONFILTER_BTN_LABEL, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.ONE))},
 {'filterValue': _FilterBit.TWO,
  'selected': False,
  'tooltip': makeTooltip(body=_ms(TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_DURATION, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.TWO))),
  'label': _ms(STORAGE.PERSONALRESERVES_DURATIONFILTER_BTN_LABEL, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.TWO))},
 {'filterValue': _FilterBit.FOUR,
  'selected': False,
  'tooltip': makeTooltip(body=_ms(TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_DURATION, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.FOUR))),
  'label': _ms(STORAGE.PERSONALRESERVES_DURATIONFILTER_BTN_LABEL, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.FOUR))},
 {'filterValue': _FilterBit.SIX,
  'selected': False,
  'tooltip': makeTooltip(body=_ms(TOOLTIPS.STORAGE_FILTER_PERSONALRESERVES_BTNS_DURATION, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.SIX))),
  'label': _ms(STORAGE.PERSONALRESERVES_DURATIONFILTER_BTN_LABEL, durTime=_DURATION_BIT_TO_DURATION_VALUE.get(_FilterBit.SIX))}]
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
    durationSet = {getDurationInSeconds(_DURATION_BIT_TO_DURATION_VALUE[bit]) for bit in _DURATION_BIT_TO_DURATION_VALUE.iterkeys() if filterMask & bit}
    if durationSet:
        criteria |= REQ_CRITERIA.BOOSTER.DURATION(durationSet)
    typesSet = {_TYPE_BIT_TO_RESOURCE_TYPE_MAP[bit] for bit in _TYPE_BIT_TO_RESOURCE_TYPE_MAP.iterkeys() if filterMask & bit}
    if typesSet:
        criteria |= REQ_CRITERIA.BOOSTER.BOOSTER_TYPES(typesSet)
    return criteria


class StorageCategoryPersonalReservesView(StorageCategoryPersonalReservesViewMeta):
    _boostersCtrl = dependency.descriptor(IBoostersController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        super(StorageCategoryPersonalReservesView, self).__init__()
        self._boosters = []
        self.__filterMask = 0
        self._loadFilters()

    def navigateToStore(self):
        showWebShop(getBuyBoostersUrl())

    def resetFilter(self):
        self.__filterMask = 0
        self.as_resetFilterS(self.__filterMask)
        self.__onUpdateBoosters()

    def onFiltersChange(self, filterMask):
        self.__filterMask = filterMask
        self.__onUpdateBoosters()

    def activateReserve(self, boosterID):
        shared_events.showBoosterActivateDialog(boosterID)

    def _getClientSectionKey(self):
        pass

    def _loadFilters(self):
        if isStorageSessionTimeout():
            return
        filterDict = AccountSettings.getSessionSettings(self._getClientSectionKey())
        self.__filterMask = filterDict['filterMask']

    def _saveFilters(self):
        filterDict = {'filterMask': self.__filterMask}
        AccountSettings.setSessionSettings(self._getClientSectionKey(), filterDict)

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
        self._boostersCtrl.onBoosterChangeNotify += self.__onUpdateBoosters
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdate
        self._epicCtrl.onUpdated += self.__onUpdateBoosters
        self.__onUpdateBoosters()
        self.__initFilter()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._boostersCtrl.onBoosterChangeNotify -= self.__onUpdateBoosters
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdate
        self._epicCtrl.onUpdated -= self.__onUpdateBoosters
        self._saveFilters()
        super(StorageCategoryPersonalReservesView, self)._dispose()

    def _update(self, *args):
        self.__onUpdateBoosters()

    def __onUpdateBoosters(self, *args):
        activeBoostersCount = len(self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        totalBoostersCount = sum((x.count for x in self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_ACCOUNT).values()))
        filteredBoostersCount = 0
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
        criteria |= getCriteriaFromFilterMask(self.__filterMask)
        boosters = self._goodiesCache.getBoosters(criteria=criteria).values()
        dataProviderValues = []
        showDummyScreen = False
        filterWarningVO = None
        if boosters:
            for booster in sorted(boosters, cmp=self.__sort):
                influence = backport.text(R.strings.menu.booster.influence.dyn(booster.boosterGuiType)())
                limitResource = R.strings.menu.booster.limit.dyn(booster.boosterGuiType)
                if limitResource:
                    additionalInfo = text_styles.alert(backport.text(limitResource()))
                else:
                    additionalInfo = ''
                vo = createStorageDefVO(booster.boosterID, text_styles.hightlight(_ms(MENU.BOOSTER_DESCRIPTION_EFFECTVALUETIME, effectValue=booster.getFormattedValue(), effectTime=booster.getEffectTimeStr(hoursOnly=True))), text_styles.main(influence), booster.count, getItemPricesVO(booster.getSellPrice())[0], func_utils.makeFlashPath(booster.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL)), func_utils.makeFlashPath(booster.getShopIcon()), 'altimage', enabled=booster.isReadyToActivate, active=booster.state, contextMenuId=CONTEXT_MENU_HANDLER_TYPE.STORAGE_PERSONAL_RESERVE_ITEM, additionalInfo=additionalInfo)
                dataProviderValues.append(vo)
                filteredBoostersCount += booster.count

        elif totalBoostersCount == 0:
            showDummyScreen = True
        else:
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        self._dataProvider.buildList(dataProviderValues)
        self.__updateFilterCounter(filteredBoostersCount, totalBoostersCount)
        self.__updateActiveBoostersCounter(activeBoostersCount, totalBoostersCount)
        self.as_showFilterWarningS(filterWarningVO)
        self.as_showDummyScreenS(showDummyScreen)
        return

    def __onQuestsUpdate(self, *args):
        self.__onUpdateBoosters()

    def __sort(self, a, b):
        return cmp(a.quality, b.quality) or cmp(BOOSTERS_ORDERS[a.boosterType], BOOSTERS_ORDERS[b.boosterType]) or cmp(b.effectValue, a.effectValue) or cmp(b.effectTime, a.effectTime)

    def __updateActiveBoostersCounter(self, active, total):
        self.as_initS({'activeText': text_styles.main(_ms(STORAGE.PERSONALRESERVES_ACTIVECOUNTLABEL, activeCount=text_styles.error(active) if active == 0 else text_styles.stats(active), totalCount=MAX_ACTIVE_BOOSTERS_COUNT)),
         'hasActiveReserve': active != 0})

    def __initFilter(self):
        durationItems = copy.deepcopy(_DURATION_FILTER_ITEMS)
        for item in durationItems:
            if self.__filterMask & item['filterValue'] == item['filterValue']:
                item.update({'selected': True})

        typeItems = copy.deepcopy(_TYPE_FILTER_ITEMS)
        for item in typeItems:
            if self.__filterMask & item['filterValue'] == item['filterValue']:
                item.update({'selected': True})

        durationFilters = {'items': durationItems,
         'minSelectedItems': 0}
        typeFilters = {'items': typeItems,
         'minSelectedItems': 0}
        self.as_initFilterS(typeFilters, durationFilters)

    def __updateFilterCounter(self, count, total):
        shouldShow = self.__filterMask != 0
        if shouldShow and total > 0:
            countString = self._formatCountString(count, total)
            drawAttention = count == 0
            self.as_updateCounterS(shouldShow, countString, drawAttention)
        else:
            countString = self._formatTotalCountString(total)
            self.as_updateCounterS(False, countString, False)
