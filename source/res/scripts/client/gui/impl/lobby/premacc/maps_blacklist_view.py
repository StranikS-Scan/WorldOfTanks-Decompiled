# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/maps_blacklist_view.py
import logging
import ArenaType
from async import await, async
from constants import PREMIUM_TYPE, EMPTY_GEOMETRY_ID, PremiumConfigs
from frameworks.wulf import View, ViewSettings, ViewFlags
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.Scaleform.Waiting import Waiting
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_info_tooltip_model import MapsBlacklistInfoTooltipModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_map_filter_model import MapsBlacklistMapFilterModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_states import MapsBlacklistSlotStates
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapsBlacklistSlotModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_view_model import MapsBlacklistViewModel
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.shared.utils import decorators
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.processors.common import MapsBlackListSetter, MapsBlackListChanger, MapsBlackListRemover
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable
from helpers import dependency
from helpers import i18n
from helpers import time_utils
from items.vehicles import CAMOUFLAGE_KINDS
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def buildSlotsModels(modelClazz, lobbyContext=None, itemsCache=None):
    mapsConfig = lobbyContext.getServerSettings().getPreferredMapsConfig()
    slotCooldown = mapsConfig['slotCooldown']
    defaultSlots = mapsConfig['defaultSlots']
    premiumSlots = mapsConfig['premiumSlots']
    totalSlots = defaultSlots + premiumSlots
    maps = itemsCache.items.stats.getMapsBlackList()
    mapsLen = len(maps)
    isPremiumAcc = itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
    serverUTCTime = time_utils.getServerUTCTime()

    def _getEmptyState(isPremiumSlot):
        return MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_DISABLED if isPremiumSlot and not isPremiumAcc else MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_ACTIVE

    result = []
    for i in range(totalSlots):
        slotModel = modelClazz()
        if mapsLen > i:
            geometryID, selectedTime = maps[i]
            if geometryID == EMPTY_GEOMETRY_ID:
                slotModel.setState(_getEmptyState(i >= defaultSlots))
                result.append(slotModel)
                continue
            if geometryID not in ArenaType.g_geometryCache:
                _logger.error('Server sent already selected map, but client does not have it! GeometryID: %d', geometryID)
                continue
            slotModel.setMapId(ArenaType.g_geometryCache[geometryID].geometryName)
            dTime = serverUTCTime - selectedTime
            if slotCooldown > dTime:
                slotModel.setState(MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN)
                timeToWait = slotCooldown - dTime
                slotModel.setCooldownTime(timeToWait)
            else:
                slotModel.setState(MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_CHANGE)
        else:
            slotModel.setState(_getEmptyState(i >= defaultSlots))
        result.append(slotModel)

    return result


class MapsBlacklistView(ViewImpl, SoundViewMixin):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ('__availableMaps', '__notifier')

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=MapsBlacklistViewModel, exitEvent=None):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = (exitEvent,)
        super(MapsBlacklistView, self).__init__(settings)
        self.__availableMaps = []
        self.__notifier = None
        Waiting.show('loadPage')
        return

    @property
    def viewModel(self):
        return super(MapsBlacklistView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return MapsBlacklistInfoTooltipContent() if event.contentID == R.views.lobby.premacc.maps_blacklist.maps_blacklist_tooltips.MapsBlacklistInfoTooltipContent() else super(MapsBlacklistView, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self, exitEvent):
        super(MapsBlacklistView, self)._initialize(exitEvent)
        self._addSoundEvent()
        self.viewModel.onCloseEvent += self.__onDestroy
        self.viewModel.onBackAction += self.__onDestroy
        self.viewModel.mapsFilters.onItemClicked += self.__onFilterSelected
        self.viewModel.onMapAddToBlacklistEvent += self.__onMapAddToBlacklist
        self.viewModel.onMapRemoveFromBlacklistEvent += self.__onMapRemoveFromBlacklist
        self.viewModel.onFilterReset += self.__onFilterReset
        self.viewModel.onInitialized += self.__onInitialized
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__updatePrem
        g_clientUpdateManager.addCallbacks({'preferredMaps': self.__onPreferredMapsChanged})
        self.__initFilterData()
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(AcyclicNotifier(lambda : time_utils.ONE_MINUTE, self.__timerUpdate))
        self.__updateAvailableMaps()
        self.__update()

    def _finalize(self):
        self.viewModel.onCloseEvent -= self.__onDestroy
        self.viewModel.onBackAction -= self.__onDestroy
        self.viewModel.mapsFilters.onItemClicked -= self.__onFilterSelected
        self.viewModel.onMapAddToBlacklistEvent -= self.__onMapAddToBlacklist
        self.viewModel.onMapRemoveFromBlacklistEvent -= self.__onMapRemoveFromBlacklist
        self.viewModel.onFilterReset -= self.__onFilterReset
        self.viewModel.onInitialized -= self.__onInitialized
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__updatePrem
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__availableMaps = []
        self.__notifier.clearNotification()
        self._removeSoundEvent()

    def __onWindowClose(self):
        self.destroyWindow()

    def __onFilterSelected(self, eventData):
        mapFilter = self.viewModel.mapsFilters.getItems()[eventData['index']]
        mapFilter.setSelected(not mapFilter.getSelected())
        self.__applyFilter()

    def __onFilterReset(self, _=None):
        for mapFilter in self.viewModel.mapsFilters.getItems():
            mapFilter.setSelected(False)

        self.__applyFilter()

    def __applyFilter(self):
        mapsFilters = self.viewModel.mapsFilters.getItems()
        selectedFilterIDs = [ mapFilter.getFilterID() for mapFilter in mapsFilters if mapFilter.getSelected() ]
        countSelectedMaps = 0
        allFiltered = all([ mapFilter.getSelected() for mapFilter in mapsFilters ]) or not selectedFilterIDs
        for itemModel in self.viewModel.maps.getItems():
            if allFiltered:
                filtered = True
            else:
                filtered = itemModel.getSeasonId() in selectedFilterIDs
            if filtered:
                countSelectedMaps += 1
            itemModel.setFiltered(filtered)

        self.viewModel.setMapsSelected(countSelectedMaps)
        self.viewModel.setMapsTotal(len(self.__availableMaps))
        self.viewModel.setIsFilterApplied(bool(selectedFilterIDs))

    def __onMapAddToBlacklist(self, eventData):
        self.__showMapConfirmDialog(eventData.get('mapId', ''))

    def __onMapRemoveFromBlacklist(self, eventData):
        self.__sendMapRemovingRequest(eventData.get('mapId', ''))

    def __onDestroy(self, _=None):
        self.destroyWindow()

    def __initFilterData(self):
        mapsFilters = self.viewModel.mapsFilters.getItems()
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

    def __updateMainData(self):
        hasFreeOrExpiredSlots = self.__hasFreeOrExpiredSlots()
        maps = self.viewModel.maps.getItems()
        maps.clear()
        for geometryType in self.__availableMaps:
            slotModel = MapsBlacklistSlotModel()
            mapName = geometryType.geometryName
            slotModel.setMapId(mapName)
            slotModel.setSeasonId(geometryType.vehicleCamouflageKind)
            slotModel.setCooldownTime(self.viewModel.getCooldownTime())
            disabledModel = self.__getDisabledMap(mapName)
            if disabledModel:
                state = disabledModel.getState()
                slotModel.setState(state)
                if state == MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN:
                    slotModel.setCooldownTime(disabledModel.getCooldownTime())
            elif hasFreeOrExpiredSlots:
                slotModel.setState(MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_ACTIVE)
            else:
                slotModel.setState(MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_DISABLED)
            maps.addViewModel(slotModel)

        maps.invalidate()
        self.__applyFilter()

    def __updateDisabledMaps(self):
        disabledMaps = self.viewModel.disabledMaps.getItems()
        disabledMaps.clear()
        minTimeToWait = 0
        hasCooldown = False
        allInCooldownState = True
        for slotModel in buildSlotsModels(MapsBlacklistSlotModel):
            disabledMaps.addViewModel(slotModel)
            slotState = slotModel.getState()
            if slotState == MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN:
                if minTimeToWait == 0 or minTimeToWait > slotModel.getCooldownTime():
                    minTimeToWait = slotModel.getCooldownTime()
                hasCooldown = True
            if slotState != MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_DISABLED:
                allInCooldownState = False

        disabledMaps.invalidate()
        self.viewModel.setCooldownTime(minTimeToWait if allInCooldownState else 0)
        if hasCooldown:
            self.__notifier.startNotification()
        else:
            self.__notifier.stopNotification()

    def __update(self):
        self.__updateDisabledMaps()
        self.__updateMainData()

    def __timerUpdate(self):
        self.__update()

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff and not diff[PremiumConfigs.IS_PREFERRED_MAPS_ENABLED]:
            self.__onWindowClose()
            return
        if PremiumConfigs.PREFERRED_MAPS in diff:
            self.__updateAvailableMaps()
            self.__update()

    def __onPreferredMapsChanged(self, _):
        self.__update()

    def __updatePrem(self, *_):
        self.__update()

    def __hasFreeOrExpiredSlots(self):
        for model in self.viewModel.disabledMaps.getItems():
            if model.getState() in (MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_ACTIVE, MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_CHANGE):
                return True

        return False

    def __getDisabledMap(self, mapName):
        for model in self.viewModel.disabledMaps.getItems():
            if model.getMapId() == mapName:
                return model

        return None

    @async
    def __showMapConfirmDialog(self, mapId):
        changeableMaps = []
        for item in self.viewModel.disabledMaps.getItems():
            if item.getState() == MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_CHANGE:
                changeableMaps.append(item.getMapId())
            if item.getState() == MapsBlacklistSlotStates.MAPS_BLACKLIST_SLOT_STATE_ACTIVE:
                changeableMaps = []
                break

        cooldown = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()['slotCooldown']
        result, choice = yield await(dialogs.mapsBlacklistConfirm(mapId, cooldown, changeableMaps, self))
        if result:
            self.__sendMapChangingRequest(mapId, choice)

    @decorators.process('updating')
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

    @decorators.process('updating')
    def __sendMapRemovingRequest(self, removeMapName):
        yield MapsBlackListRemover(self.__mapNameToID(removeMapName)).request()

    @staticmethod
    def __mapNameToID(mapName):
        return ArenaType.g_geometryNamesToIDs[mapName]

    def __onInitialized(self):
        Waiting.hide('loadPage')


class MapsBlacklistInfoTooltipContent(View):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.premacc.maps_blacklist.maps_blacklist_tooltips.MapsBlacklistInfoTooltipContent(), ViewFlags.COMPONENT, MapsBlacklistInfoTooltipModel())
        super(MapsBlacklistInfoTooltipContent, self).__init__(settings)
        mapsConfig = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
        self.viewModel.setMaxCooldownTime(mapsConfig['slotCooldown'])

    @property
    def viewModel(self):
        return super(MapsBlacklistInfoTooltipContent, self).getViewModel()
