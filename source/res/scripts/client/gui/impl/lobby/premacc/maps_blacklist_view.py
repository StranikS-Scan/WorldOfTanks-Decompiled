# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/maps_blacklist_view.py
import logging
from typing import TYPE_CHECKING
import ArenaType
from constants import PremiumConfigs, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import View, ViewFlags, ViewSettings
from gui import SystemMessages
from gui.Scaleform import MENU
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl, getWotPlusShopUrl
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_info_tooltip_model import MapsBlacklistInfoTooltipModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_map_filter_model import MapsBlacklistMapFilterModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapStateEnum, MapsBlacklistSlotModel, SlotTypeEnum
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_view_model import MapsBlacklistViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.account_dashboard.tooltips.excluded_maps_reward_slots_tooltip_view import ExcludedMapsRewardSlotsTooltipView
from gui.impl.lobby.premacc.views_helpers import deferPreferredMapsUiRefresh, getPreferredMapsUiRefreshDelay, isPreferredMapsClientDiff, iterResolvedSlots, populateMapsBlacklistSlotModel, shouldSchedulePreferredMapsUiRefresh
from PlayerEvents import g_playerEvents
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items.processors.common import MapsBlackListChanger, MapsBlackListRemover, MapsBlackListSetter
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, i18n, time_utils
from items.vehicles import CAMOUFLAGE_KINDS
from preferred_maps import SlotTypeId
from shared_utils import findFirst
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from th_async import th_async, th_await
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Any, Dict, Generator, List, Optional, Type
    from frameworks.wulf import ViewEvent
_SLOT_TYPE_ID_TO_ENUM = {SlotTypeId.DEFAULT: SlotTypeEnum.DEFAULT,
 SlotTypeId.PREMIUM: SlotTypeEnum.PREMIUM,
 SlotTypeId.SUBSCRB: SlotTypeEnum.SUBSCRB,
 SlotTypeId.REWARDS: SlotTypeEnum.REWARDS}

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def _buildSlotsModels(lobbyContext=None, itemsCache=None):
    config = lobbyContext.getServerSettings().getPreferredMapsConfig()
    slotCooldown = config['slotCooldown']
    serverUTCTime = time_utils.getServerUTCTime()
    blackListSlotsModel = []
    for slot in iterResolvedSlots(config, itemsCache):
        slotModel = MapsBlacklistSlotModel()
        if populateMapsBlacklistSlotModel(slotModel, slot, slotCooldown, serverUTCTime, _SLOT_TYPE_ID_TO_ENUM[slot.type]):
            blackListSlotsModel.append(slotModel)

    return blackListSlotsModel


class MapsBlacklistView(ViewImpl):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __gameSession = dependency.descriptor(IGameSessionController)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('__minTimeToWait', '__availableMaps', '__notifier')

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=MapsBlacklistViewModel, exitEvent=None):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = (exitEvent,)
        super(MapsBlacklistView, self).__init__(settings)
        self.__availableMaps = []
        self.__minTimeToWait = 0
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(SimpleNotifier(self.__getCooldownNotificationDelta, self.__update))
        Waiting.show('loadPage')

    @property
    def viewModel(self):
        return super(MapsBlacklistView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.premacc.maps_blacklist.maps_blacklist_tooltips.MapsBlacklistInfoTooltipContent():
            return MapsBlacklistInfoTooltipContent()
        if event.contentID == R.views.lobby.account_dashboard.tooltips.ExcludedMapsRewardSlotsTooltipView():
            rewardsSlot = findFirst(lambda s: s.getType() == SlotTypeEnum.REWARDS, (slot for slot in self.viewModel.disabledMaps.getItems()))
            if rewardsSlot:
                slotState = rewardsSlot.getState()
                if slotState == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED_BY_KILL_SWITCH:
                    slotState = MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED
                return ExcludedMapsRewardSlotsTooltipView(slotState, rewardsSlot.getCooldownTime(), rewardsSlot.getExpirationTime())
        return super(MapsBlacklistView, self).createToolTipContent(event=event, contentID=contentID)

    def _getEvents(self):
        return ((self.viewModel.onCloseEvent, self.__onDestroy),
         (self.viewModel.onBackAction, self.__onDestroy),
         (self.viewModel.onFilterClick, self.__onFilterSelected),
         (self.viewModel.onMapAddToBlacklistEvent, self.__onMapAddToBlacklist),
         (self.viewModel.onMapRemoveFromBlacklistEvent, self.__onMapRemoveFromBlacklist),
         (self.viewModel.onFilterReset, self.__onFilterReset),
         (self.viewModel.onBuyPremiumClick, self.__onBuyPremiumClick),
         (self.viewModel.onGetSubscriptionClick, self.__onGetSubscriptionClick),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__gameSession.onPremiumNotify, self.__update),
         (self.__wotPlusCtrl.onDataChanged, self.__onWotPlusChanged),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def _getCallbacks(self):
        return (('preferredMaps', self.__update),)

    def _onLoading(self, *args, **kwargs):
        super(MapsBlacklistView, self)._onLoading(*args, **kwargs)
        self.__updateAvailableMaps()
        self.__initFilterData()
        self.__update()

    def _initialize(self, exitEvent):
        super(MapsBlacklistView, self)._initialize(exitEvent)
        Waiting.hide('loadPage')

    def _finalize(self):
        self.__availableMaps = []
        self.__notifier.clearNotification()
        super(MapsBlacklistView, self)._finalize()

    def __onWindowClose(self):
        self.destroyWindow()

    @args2params(int)
    def __onFilterSelected(self, seasonID):
        with self.viewModel.transaction() as viewModel:
            for mapFilter in viewModel.mapsFilters.getItems():
                if mapFilter.getFilterID() == seasonID:
                    mapFilter.setSelected(not mapFilter.getSelected())
                    break

            self.__applyFilter(viewModel)

    def __onFilterReset(self, _=None):
        with self.viewModel.transaction() as viewModel:
            mapsFilters = viewModel.mapsFilters.getItems()
            for mapFilter in mapsFilters:
                mapFilter.setSelected(False)

            mapsFilters.invalidate()
            self.__applyFilter(viewModel)

    def __onBuyPremiumClick(self):
        showShop(getBuyPremiumUrl())

    def __onGetSubscriptionClick(self):
        showShop(getWotPlusShopUrl())

    def __applyFilter(self, viewModel):
        mapsFilters = viewModel.mapsFilters.getItems()
        selectedFilterIDs = [ mapFilter.getFilterID() for mapFilter in mapsFilters if mapFilter.getSelected() ]
        countSelectedMaps = 0
        allFiltered = all([ mapFilter.getSelected() for mapFilter in mapsFilters ]) or not selectedFilterIDs
        with viewModel.maps.transaction() as viewModelMaps:
            maps = viewModelMaps.getItems()
            for itemModel in maps:
                filtered = allFiltered or itemModel.getSeasonId() in selectedFilterIDs
                if filtered:
                    countSelectedMaps += 1
                itemModel.setFiltered(filtered)

            maps.invalidate()
        viewModel.setMapsSelected(countSelectedMaps)
        viewModel.setMapsTotal(len(self.__availableMaps))
        viewModel.setIsFilterApplied(bool(selectedFilterIDs))

    @args2params(str)
    def __onMapAddToBlacklist(self, mapId):
        self.__showMapConfirmDialog(mapId)

    @args2params(str)
    def __onMapRemoveFromBlacklist(self, mapId):
        self.__sendMapRemovingRequest(mapId)

    def __onDestroy(self, _=None):
        self.destroyWindow()

    def __initFilterData(self):
        with self.viewModel.transaction() as viewModel:
            mapsFilters = viewModel.mapsFilters.getItems()
            for seasonName, seasonID in CAMOUFLAGE_KINDS.iteritems():
                filterModel = MapsBlacklistMapFilterModel()
                filterModel.setFilterName(seasonName)
                filterModel.setFilterID(seasonID)
                mapsFilters.addViewModel(filterModel)

    def __updateAvailableMaps(self):
        self.__availableMaps = []
        availableMaps = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()['mapIDs']
        for geometryID in availableMaps:
            if geometryID not in ArenaType.g_geometryCache:
                _logger.error('Server has arena, but client does not have! GeometryID: %d', geometryID)
                continue
            geometryType = ArenaType.g_geometryCache[geometryID]
            self.__availableMaps.append(geometryType)

        self.__availableMaps.sort(key=lambda item: item.name)

    def __updateMainData(self, viewModel):
        hasFreeOrExpiredSlots = self.__hasFreeOrExpiredSlots()
        with viewModel.maps.transaction() as viewModelMaps:
            maps = viewModelMaps.getItems()
            maps.clear()
            for geometryType in self.__availableMaps:
                slotModel = MapsBlacklistSlotModel()
                mapName = geometryType.geometryName
                slotModel.setMapId(mapName)
                slotModel.setSeasonId(geometryType.vehicleCamouflageKind)
                slotModel.setCooldownTime(self.__minTimeToWait)
                disabledModel = self.__getDisabledMap(mapName)
                if disabledModel:
                    state = disabledModel.getState()
                    slotModel.setState(state)
                    if state == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN:
                        slotModel.setCooldownTime(disabledModel.getCooldownTime())
                elif hasFreeOrExpiredSlots:
                    slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE)
                else:
                    slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED)
                maps.addViewModel(slotModel)

            maps.invalidate()
        self.__applyFilter(viewModel)

    def __updateDisabledMaps(self, viewModel):
        with viewModel.disabledMaps.transaction() as viewModelDisabledMaps:
            disabledMaps = viewModelDisabledMaps.getItems()
            disabledMaps.clear()
            minTimeToWait = 0
            allInCooldownState = True
            for slotModel in _buildSlotsModels():
                disabledMaps.addViewModel(slotModel)
                slotState = slotModel.getState()
                if slotState == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN:
                    if minTimeToWait == 0 or minTimeToWait > slotModel.getCooldownTime():
                        minTimeToWait = slotModel.getCooldownTime()
                if slotState not in (MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED, MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED_BY_KILL_SWITCH):
                    allInCooldownState = False

            disabledMaps.invalidate()
            self.__minTimeToWait = minTimeToWait if allInCooldownState else 0
            viewModel.setCooldownTime(self.__minTimeToWait)
            config = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
            if shouldSchedulePreferredMapsUiRefresh(config, self.__itemsCache):
                self.__notifier.startNotification()
            else:
                self.__notifier.stopNotification()

    def __update(self, *args, **kwargs):
        with self.viewModel.transaction() as viewModel:
            self.__updateDisabledMaps(viewModel)
            self.__updateMainData(viewModel)
            self.__updateEnvironment(viewModel)

    def __onWotPlusChanged(self, data):
        if 'isEnabled' in data:
            self.__update()

    def __getCooldownNotificationDelta(self):
        config = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
        return getPreferredMapsUiRefreshDelay(config, self.__itemsCache)

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff and not diff[PremiumConfigs.IS_PREFERRED_MAPS_ENABLED]:
            self.__onWindowClose()
            return
        if PremiumConfigs.PREFERRED_MAPS in diff or RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.__updateAvailableMaps()
            self.__update()

    def __onClientUpdated(self, diff, _):
        if not isPreferredMapsClientDiff(diff):
            return
        deferPreferredMapsUiRefresh(self.__onPreferredMapsClientDiffApplied)

    def __onPreferredMapsClientDiffApplied(self):
        self.__updateAvailableMaps()
        self.__update()

    def __hasFreeOrExpiredSlots(self):
        for model in self.viewModel.disabledMaps.getItems():
            if model.getState() in (MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE, MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_CHANGE):
                return True

        return False

    def __getDisabledMap(self, mapName):
        for model in self.viewModel.disabledMaps.getItems():
            if model.getMapId() == mapName:
                return model

        return None

    @th_async
    def __showMapConfirmDialog(self, mapId):
        changeableMaps = []
        for item in self.viewModel.disabledMaps.getItems():
            if item.getState() == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_CHANGE:
                changeableMaps.append(item.getMapId())
            if item.getState() == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE:
                changeableMaps = []
                break

        cooldown = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()['slotCooldown']
        result, choice = yield th_await(dialogs.mapsBlacklistConfirm(mapId, cooldown, changeableMaps, self))
        if result:
            self.__sendMapChangingRequest(mapId, choice)

    @decorators.adisp_process('updating')
    def __sendMapChangingRequest(self, mapToSet, mapToChange):
        serverSettings = self.__lobbyContext.getServerSettings()
        cooldown = time_utils.getTillTimeString(serverSettings.getPreferredMapsConfig()['slotCooldown'], MENU.MAPBLACKLIST_TIMELEFTSHORT, isRoundUp=True, removeLeadingZeros=True)
        dstMapID = self.__mapNameToID(mapToSet)
        if dstMapID is not None:
            dstMapName = i18n.makeString(ArenaType.g_cache[dstMapID].name)
        else:
            _logger.error('[MapChangingRequest] ID is unavailable for map: %s', mapToSet)
            return
        if mapToChange:
            srcMapID = self.__mapNameToID(mapToChange)
            requester = MapsBlackListChanger(srcMapID, dstMapID)
        else:
            requester = MapsBlackListSetter(dstMapID)
        result = yield requester.request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg % {'mapName': dstMapName,
             'time': cooldown}, type=result.sysMsgType)
        return

    @decorators.adisp_process('updating')
    def __sendMapRemovingRequest(self, removeMapName):
        yield MapsBlackListRemover(self.__mapNameToID(removeMapName)).request()

    @staticmethod
    def __mapNameToID(mapName):
        return ArenaType.g_geometryNamesToIDs[mapName]

    def __updateEnvironment(self, viewModel):
        viewModel.setIsWotPlusEnabled(self.__wotPlusCtrl.isWotPlusEnabled())


class MapsBlacklistInfoTooltipContent(View):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.premacc.maps_blacklist.maps_blacklist_tooltips.MapsBlacklistInfoTooltipContent(), ViewFlags.VIEW, MapsBlacklistInfoTooltipModel())
        super(MapsBlacklistInfoTooltipContent, self).__init__(settings)
        mapsConfig = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
        self.viewModel.setMaxCooldownTime(mapsConfig['slotCooldown'])

    @property
    def viewModel(self):
        return super(MapsBlacklistInfoTooltipContent, self).getViewModel()
