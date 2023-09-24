# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/maps_blacklist_view.py
import typing
import ArenaType
import logging
from constants import PREMIUM_TYPE, PremiumConfigs, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import View, ViewSettings, ViewFlags
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.Scaleform.Waiting import Waiting
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_info_tooltip_model import MapsBlacklistInfoTooltipModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_map_filter_model import MapsBlacklistMapFilterModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapsBlacklistSlotModel, MapStateEnum
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_view_model import MapsBlacklistViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.processors.common import MapsBlackListSetter, MapsBlackListChanger, MapsBlackListRemover
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable
from helpers import dependency
from helpers import i18n
from helpers import time_utils
from items.vehicles import CAMOUFLAGE_KINDS
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from wg_async import wg_await, wg_async
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import List, Type, Any, Dict, Optional
    from frameworks.wulf import ViewEvent

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache, wotPlusController=IWotPlusController)
def buildSlotsModels(lobbyContext=None, itemsCache=None, wotPlusController=None):
    serverSettings = lobbyContext.getServerSettings()
    mapsConfig = serverSettings.getPreferredMapsConfig()
    slotCooldown = mapsConfig['slotCooldown']
    defaultSlots = mapsConfig['defaultSlots']
    premiumSlots = mapsConfig['premiumSlots']
    wotPlusSlots = mapsConfig['wotPlusSlots'] if serverSettings.isWotPlusExcludedMapEnabled() else 0
    totalSlots = defaultSlots + premiumSlots + wotPlusSlots
    maps = [ (mapId, selectedTime) for mapId, selectedTime in itemsCache.items.stats.getMapsBlackList() if mapId > 0 ]
    serverUTCTime = time_utils.getServerUTCTime()
    availableSlots = defaultSlots
    if itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS):
        availableSlots += premiumSlots
    if wotPlusController.isEnabled():
        availableSlots += wotPlusSlots
    disabledMaps = []
    for i in range(totalSlots):
        slotModel = MapsBlacklistSlotModel()
        slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED)
        if i < availableSlots:
            slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE)
        disabledMaps.append(slotModel)

    for i, (geometryID, selectedTime) in enumerate(maps[:totalSlots]):
        slotModel = disabledMaps[i]
        if geometryID not in ArenaType.g_geometryCache:
            _logger.error('Server sent already selected map, but client does not have it! GeometryID: %d', geometryID)
            continue
        slotModel.setMapId(ArenaType.g_geometryCache[geometryID].geometryName)
        slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_CHANGE)
        slotModel.setCooldownTime(0)
        dTime = serverUTCTime - selectedTime
        if slotCooldown > dTime:
            slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN)
            slotModel.setCooldownTime(selectedTime + slotCooldown)

    return disabledMaps


class MapsBlacklistView(ViewImpl, SoundViewMixin):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('__availableMaps', '__notifier')

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=MapsBlacklistViewModel, exitEvent=None):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = (exitEvent,)
        super(MapsBlacklistView, self).__init__(settings)
        self.__availableMaps = []
        self.minTimeToWait = 0
        self.__notifier = Notifiable()
        Waiting.show('loadPage')

    @property
    def viewModel(self):
        return super(MapsBlacklistView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return MapsBlacklistInfoTooltipContent() if event.contentID == R.views.lobby.premacc.maps_blacklist.maps_blacklist_tooltips.MapsBlacklistInfoTooltipContent() else super(MapsBlacklistView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        self.__updateAvailableMaps()
        self.__initFilterData()
        self.__update()

    def _initialize(self, exitEvent):
        super(MapsBlacklistView, self)._initialize(exitEvent)
        self._addSoundEvent()
        self.viewModel.onCloseEvent += self.__onDestroy
        self.viewModel.onBackAction += self.__onDestroy
        self.viewModel.onFilterClick += self.__onFilterSelected
        self.viewModel.onMapAddToBlacklistEvent += self.__onMapAddToBlacklist
        self.viewModel.onMapRemoveFromBlacklistEvent += self.__onMapRemoveFromBlacklist
        self.viewModel.onFilterReset += self.__onFilterReset
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__update
        self.__wotPlusCtrl.onDataChanged += self.__onWotPlusChanged
        g_clientUpdateManager.addCallbacks({'preferredMaps': self.__update})
        self.__notifier.addNotificator(AcyclicNotifier(lambda : time_utils.ONE_MINUTE, self.__update))
        Waiting.hide('loadPage')

    def _finalize(self):
        self.viewModel.onCloseEvent -= self.__onDestroy
        self.viewModel.onBackAction -= self.__onDestroy
        self.viewModel.onFilterClick -= self.__onFilterSelected
        self.viewModel.onMapAddToBlacklistEvent -= self.__onMapAddToBlacklist
        self.viewModel.onMapRemoveFromBlacklistEvent -= self.__onMapRemoveFromBlacklist
        self.viewModel.onFilterReset -= self.__onFilterReset
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__update
        self.__wotPlusCtrl.onDataChanged -= self.__onWotPlusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__availableMaps = []
        self.__notifier.clearNotification()
        self._removeSoundEvent()

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

    def __applyFilter(self, viewModel):
        mapsFilters = viewModel.mapsFilters.getItems()
        selectedFilterIDs = [ mapFilter.getFilterID() for mapFilter in mapsFilters if mapFilter.getSelected() ]
        countSelectedMaps = 0
        allFiltered = all([ mapFilter.getSelected() for mapFilter in mapsFilters ]) or not selectedFilterIDs
        with viewModel.maps.transaction() as viewModelMaps:
            maps = viewModelMaps.getItems()
            for itemModel in maps:
                if allFiltered:
                    filtered = True
                else:
                    filtered = itemModel.getSeasonId() in selectedFilterIDs
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
                slotModel.setCooldownTime(self.minTimeToWait)
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
            hasCooldown = False
            allInCooldownState = True
            for slotModel in buildSlotsModels():
                disabledMaps.addViewModel(slotModel)
                slotState = slotModel.getState()
                if slotState == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN:
                    if minTimeToWait == 0 or minTimeToWait > slotModel.getCooldownTime():
                        minTimeToWait = slotModel.getCooldownTime()
                    hasCooldown = True
                if slotState != MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED:
                    allInCooldownState = False

            disabledMaps.invalidate()
            self.minTimeToWait = minTimeToWait if allInCooldownState else 0
            viewModel.setCooldownTime(self.minTimeToWait)
            if hasCooldown:
                self.__notifier.startNotification()
            else:
                self.__notifier.stopNotification()

    def __update(self, *args, **kwargs):
        with self.viewModel.transaction() as viewModel:
            self.__updateDisabledMaps(viewModel)
            self.__updateMainData(viewModel)

    def __onWotPlusChanged(self, data):
        if 'isEnabled' in data:
            self.__update()

    def __timerUpdate(self):
        self.__update()

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff and not diff[PremiumConfigs.IS_PREFERRED_MAPS_ENABLED]:
            self.__onWindowClose()
            return
        if PremiumConfigs.PREFERRED_MAPS in diff or RENEWABLE_SUBSCRIPTION_CONFIG in diff:
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

    @wg_async
    def __showMapConfirmDialog(self, mapId):
        changeableMaps = []
        for item in self.viewModel.disabledMaps.getItems():
            if item.getState() == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_CHANGE:
                changeableMaps.append(item.getMapId())
            if item.getState() == MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE:
                changeableMaps = []
                break

        cooldown = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()['slotCooldown']
        result, choice = yield wg_await(dialogs.mapsBlacklistConfirm(mapId, cooldown, changeableMaps, self))
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
