# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/platoon_controller.py
import logging
from typing import TYPE_CHECKING
import BigWorld
import Event
import SoundGroups
import VOIP
from CurrentVehicle import g_currentVehicle
import CGF
from shared_utils import findFirst
from UnitBase import UNIT_ROLE, UnitAssemblerSearchFlags, extendTiersFilter
from constants import EPlatoonButtonState, MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL, Configs
from PlatoonTank import PlatoonTank, PlatoonTankInfo
from account_helpers.AccountSettings import AccountSettings, UNIT_FILTER, GUI_START_BEHAVIOR
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GAME, GuiSettingsBehavior, OnceOnlyHints
from adisp import adisp_process, adisp_async
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.platoon_config import QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME, PREBATTLE_TYPE_TO_VEH_CRITERIA, PrbEntityInfo, EPlatoonLayout, ePlatoonLayouts, Position, SquadInfo, buildCurrentLayouts
from gui.prb_control import prb_getters
from gui.prb_control import settings
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.squad.entity import SquadEntity
from gui.prb_control.entities.base.unit.ctx import AutoSearchUnitCtx
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.formatters import messages
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import functions
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.statistics import HARDWARE_SCORE_PARAMS
from messenger import MessengerEntry
from messenger.ext import channel_num_gen
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, PREBATTLE_TYPE, QUEUE_TYPE_TO_PREBATTLE_TYPE
from gui.prb_control.entities.base.unit.permissions import UnitPermissions
from gui.prb_control.entities.base.unit.entity import UnitEntity
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters.ranges import toRomanRangeString
from gui.impl.lobby.platoon.platoon_helpers import convertTierFilterToList
from gui.prb_control.settings import REQUEST_TYPE
from cgf_components.hangar_camera_manager import HangarCameraManager
if TYPE_CHECKING:
    from typing import Any, Optional as TOptional, Tuple as TTuple
    from UnitBase import ProfileVehicle
_logger = logging.getLogger(__name__)
_MIN_PERF_PRESET_NAME = 'MIN'
_MAX_SLOT_COUNT_FOR_PLAYER_RESORTING = 3

class _FilterExpander(CallbackDelayer):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(_FilterExpander, self).__init__()
        self.__initialTierFlags = 0
        self.__expandedTierFlags = 0
        self.__iterations = 0
        self.__nextDelayGenerator = None
        return

    def start(self, userSearchFlags):
        self.clearCallbacks()
        self.__initialTierFlags = self.__expandedTierFlags = userSearchFlags & UnitAssemblerSearchFlags.ALL_VEH_TIERS
        self.__iterations = 0
        delayListByTiers = self.__getExtendDelaysByTiers()
        self.__nextDelayGenerator = self.__getNextDelayByTier(delayListByTiers)
        delayByTier = next(self.__nextDelayGenerator, None)
        if delayByTier is not None:
            self.delayCallback(delayByTier, self.__refreshCurrentlySearchedTiers)
        else:
            self.stop()
        return

    def updateSearchFlags(self, newFlags):
        newTierFlags = newFlags & UnitAssemblerSearchFlags.ALL_VEH_TIERS
        if self.__nextDelayGenerator is None or self.__initialTierFlags == newTierFlags:
            return
        else:
            self.__initialTierFlags = self.__expandedTierFlags = newTierFlags
            for _ in xrange(self.__iterations):
                self.__expandedTierFlags = extendTiersFilter(self.__expandedTierFlags)

            self.__platoonCtrl.onFilterUpdate()
            return

    def stop(self):
        self.__initialTierFlags = 0
        self.__expandedTierFlags = 0
        self.__iterations = 0
        self.__platoonCtrl.onFilterUpdate()
        self.__nextDelayGenerator = None
        self.clearCallbacks()
        return

    def getExpandedFilter(self):
        return self.__expandedTierFlags

    def isExpanded(self):
        return self.__initialTierFlags != self.__expandedTierFlags

    def __getExtendDelaysByTiers(self):
        prebattleType = self.__platoonCtrl.getPrbEntityType()
        unitAssemblerConfig = self.__lobbyContext.getServerSettings().unitAssemblerConfig
        return unitAssemblerConfig.getExtendTierFilter(prebattleType)

    def __refreshCurrentlySearchedTiers(self):
        if self.__platoonCtrl.isInSearch():
            if self.__extendCurrentTierFilter():
                self.__platoonCtrl.onFilterUpdate()
                return next(self.__nextDelayGenerator, None)
        return None

    def __extendCurrentTierFilter(self):
        self.__iterations += 1
        newFilterFlags = extendTiersFilter(self.__expandedTierFlags)
        isFilterChanged = newFilterFlags != self.__expandedTierFlags
        self.__expandedTierFlags = newFilterFlags
        return isFilterChanged

    def __getNextDelayByTier(self, delayListByTiers):
        lastDelay = 0.0
        for nextDelay in delayListByTiers:
            yield nextDelay - lastDelay
            lastDelay = nextDelay


class PlatoonController(IPlatoonController, IGlobalListener, CallbackDelayer):
    QUEUE_INFO_UPDATE_DELAY = 5
    DROPDOWN_HALF_WIDTH = 205
    DROPDOWN_Y_OFFSET = 6
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(PlatoonController, self).__init__()
        CallbackDelayer.__init__(self)
        self.__channelCtrl = None
        self.__filterExpander = _FilterExpander()
        self.__isActiveSearchView = False
        self.__startAutoSearchOnUnitJoin = False
        self.__currentlyDisplayedTanks = 0
        self.__isPlatoonVisualizationEnabled = False
        self.__availablePlatoonTanks = {}
        self.__tankDisplayPosition = {}
        self.__executeQueue = False
        self.__areOtherMembersReady = False
        self.__availableTiersForSearch = 0
        self.__availableTiersInventory = None
        self.__alreadyJoinedAccountDBIDs = set()
        self.currentPlatoonLayouts = buildCurrentLayouts()
        self.onFilterUpdate = Event.Event()
        self.onPlatoonTankVisualizationChanged = Event.Event()
        self.onChannelControllerChanged = Event.Event()
        self.onAvailableTiersForSearchChanged = Event.Event()
        self.onMembersUpdate = Event.Event()
        self.onPlatoonTankUpdated = Event.Event()
        self.onAutoSearchCooldownChanged = Event.Event()
        self.onPlatoonTankRemove = Event.Event()
        self.__prevPrbEntityInfo = PrbEntityInfo(QUEUE_TYPE.UNKNOWN, PREBATTLE_TYPE.NONE)
        self.__waitingReadyAccept = False
        return

    def onLobbyInited(self, event):
        validateDisplaySettings = self.__checkForSettingsModification()
        if validateDisplaySettings:
            self.__validateSystemReq()
        self.currentPlatoonLayouts = buildCurrentLayouts(self.getPrbEntityType())
        self.__isPlatoonVisualizationEnabled = bool(self.__settingsCore.getSetting(GAME.DISPLAY_PLATOON_MEMBERS))
        self.__startListening()
        self.__cacheAvailableVehicles()

    def onLobbyStarted(self, ctx):
        self.resetUnitTierFilter()

    def onPrbEntitySwitching(self):
        queueType = self.getQueueType()
        prebattleType = self.getPrbEntityType()
        self.__destroy(hideOnly=False)
        self.__prevPrbEntityInfo = PrbEntityInfo(queueType, prebattleType)
        self.__clearPlatoonTankInfo()

    def onAccountBecomeNonPlayer(self):
        self.__stopListening()
        self.onPlatoonTankVisualizationChanged(False)
        self.destroyUI()
        self.clearCallbacks()
        self.__startAutoSearchOnUnitJoin = False
        self.__channelCtrl = None
        self.__availableTiersInventory = None
        self.__tankDisplayPosition.clear()
        return

    def getUserSearchFlags(self):
        defaults = AccountSettings.getFilterDefault(UNIT_FILTER)
        unitFilter = self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.UNIT_FILTER, defaults)
        return unitFilter[GAME.UNIT_FILTER]

    def getCurrentSearchFlags(self):
        unitMgr = prb_getters.getClientUnitMgr()
        return unitMgr.unit.getAutoSearchFlags() if unitMgr and unitMgr.unit else 0

    def saveUserSearchFlags(self, value):
        unitFilter = {GAME.UNIT_FILTER: value}
        self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.UNIT_FILTER, unitFilter)
        self.__updateExpanderSearchFlags()

    def resetUnitTierFilter(self):
        searchFlagsWithoutTiers = self.getCurrentSearchFlags() & ~UnitAssemblerSearchFlags.ALL_VEH_TIERS
        self.saveUserSearchFlags(searchFlagsWithoutTiers)

    def getPermissions(self):
        return self.prbEntity.getPermissions()

    @adisp_async
    @adisp_process
    def processPlatoonActions(self, mapID, entity, currentVehicle, callback):
        if not self.__isActiveSearchView:
            callback(False)
            return
        result = yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=True))
        self.__executeQueue = result
        callback(result)

    def onPrbEntitySwitched(self):
        prevQueueType = self.__prevPrbEntityInfo.queueType
        if prevQueueType != self.getQueueType() and self.hasSearchSupport():
            self.resetUnitTierFilter()
        self.currentPlatoonLayouts = buildCurrentLayouts(self.getPrbEntityType())
        self.__cacheAvailableVehicles(checkVehicles=True)
        if not self.__executeQueue:
            return
        self.__executeQueue = False
        self.prbDispatcher.doAction(PrbAction(''))
        self.__updatePlatoonTankInfo()

    def leavePlatoon(self, isExit=True, ignoreConfirmation=False, parent=None):
        action = LeavePrbAction(isExit=isExit, ignoreConfirmation=ignoreConfirmation, parent=parent)
        self.__tankDisplayPosition.clear()
        event = events.PrbActionEvent(action, events.PrbActionEvent.LEAVE)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)

    @adisp_process
    def createPlatoon(self, startAutoSearchOnUnitJoin=False):
        queueType = self.getQueueType()
        if queueType in QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME:
            if startAutoSearchOnUnitJoin:
                navigationPossible = yield self.__lobbyContext.isPlatoonCreationPossible()
            else:
                navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
            if navigationPossible:
                if self.prbDispatcher:
                    self.__startAutoSearchOnUnitJoin = startAutoSearchOnUnitJoin
                    self.__isActiveSearchView = startAutoSearchOnUnitJoin
                    self.__doSelect(QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME[queueType])
                    self.destroyUI(hideOnly=True)
                else:
                    _logger.error('Prebattle dispatcher is not defined or navigation not possible')
        else:
            _logger.error('QueueType not found %d', queueType)

    def startSearch(self):
        if isinstance(self.prbEntity, UnitEntity):
            if not self.isInSearch():
                ctx = AutoSearchUnitCtx('prebattle/auto_search')
                _logger.debug('Unit request: %s', str(ctx))
                searchFlags = self.getUserSearchFlags()
                if self.__isActiveSearchView:
                    searchFlags |= UnitAssemblerSearchFlags.DESTROY_UNIT_ON_ABORT
                self.prbEntity.doAutoSearch(ctx, self.__startAutoSearchCallback, searchFlags)

    def cancelSearch(self):
        if isinstance(self.prbEntity, UnitEntity) and self.isInSearch():
            ctx = AutoSearchUnitCtx('prebattle/auto_search', action=0)
            self.prbEntity.doAutoSearch(ctx, callback=None)
        return

    @adisp_async
    @adisp_process
    def togglePlayerReadyAction(self, callback):
        if self.__waitingReadyAccept:
            callback(False)
            return
        changeStatePossible = True
        notReady = not self.prbEntity.getPlayerInfo().isReady
        self.__waitingReadyAccept = True
        if notReady:
            changeStatePossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if changeStatePossible and notReady and not self.prbEntity.isCommander():
            changeStatePossible = yield functions.checkAmmoLevel((g_currentVehicle.item,))
        if changeStatePossible:
            self.prbEntity.togglePlayerReadyAction(True)
        self.__waitingReadyAccept = False
        callback(changeStatePossible)

    def getFunctionalState(self):
        return self.prbDispatcher.getFunctionalState() if self.prbDispatcher is not None else None

    def isInSearch(self):
        if isinstance(self.prbEntity, UnitEntity):
            flags = self.prbEntity.getFlags()
            return flags.isInSearch()
        return False

    def isInQueue(self):
        if isinstance(self.prbEntity, UnitEntity):
            flags = self.prbEntity.getFlags()
            return flags.isInQueue()
        return False

    def isInPlatoon(self):
        return self.prbDispatcher.getFunctionalState().isInUnit() and self.prbEntity.getEntityType() in PREBATTLE_TYPE.SQUAD_PREBATTLES if self.prbDispatcher and self.prbEntity else False

    def isSearchingForPlayersEnabled(self):
        prebattleType = self.getPrbEntityType()
        unitAssemblerConfig = self.__lobbyContext.getServerSettings().unitAssemblerConfig
        return unitAssemblerConfig.isAssemblingEnabled(prebattleType)

    def isTankLevelPreferenceEnabled(self):
        prebattleType = self.getPrbEntityType()
        unitAssemblerConfig = self.__lobbyContext.getServerSettings().unitAssemblerConfig
        return unitAssemblerConfig.isTankLevelPreferenceEnabled(prebattleType)

    def getAllowedTankLevels(self, prebattleType):
        unitAssemblerConfig = self.__lobbyContext.getServerSettings().unitAssemblerConfig
        return unitAssemblerConfig.getAllowedTankLevels(prebattleType)

    def isVOIPEnabled(self):
        voipMgr = VOIP.getVOIPManager()
        return voipMgr and voipMgr.isEnabled()

    def isInCoolDown(self, requestType):
        return self.hasDelayedCallback(self.__fireOnAutoSearchCooldownChanged) if requestType is REQUEST_TYPE.AUTO_SEARCH else self.prbEntity.isInCoolDown(requestType)

    def canStartSearch(self):
        return self.isSearchingForPlayersEnabled() and self.hasVehiclesForSearch()

    def getPlayerInfo(self):
        return self.prbEntity.getPlayerInfo() if isinstance(self.prbEntity, UnitEntity) else None

    def registerPlatoonTank(self, platoonTankRef):
        self.__availablePlatoonTanks[platoonTankRef.slotIndex] = platoonTankRef

    def evaluateVisibility(self, xPopoverOffset=None, toggleUI=False):
        if self.isAnyPlatoonUIShown() and toggleUI:
            self.destroyUI(hideOnly=True)
        elif isinstance(self.prbEntity, UnitEntity):
            if self.hasSearchSupport() and self.__isActiveSearchView:
                if not (self.isInSearch() or self.__startAutoSearchOnUnitJoin):
                    _logger.error('Invalid Platoon UI state!')
                self.__showWindow(EPlatoonLayout.SEARCH, xPopoverOffset)
            else:
                self.__showWindow(EPlatoonLayout.MEMBER)
        elif self.__shouldChangeToRandomAndShowWindow():
            self.__jumpToBattleMode(PREBATTLE_ACTION_NAME.RANDOM, EPlatoonLayout.WELCOME, xPopoverOffset)
        elif self.hasSearchSupport() or self.canSelectSquadSize():
            self.__showWindow(EPlatoonLayout.WELCOME, xPopoverOffset)
        else:
            self.createPlatoon(startAutoSearchOnUnitJoin=False)

    def isAnyPlatoonUIShown(self):
        for ePlatoonLayout in ePlatoonLayouts:
            view = self.__getView(ePlatoonLayout)
            if view and not view.getParentWindow().isHidden():
                return True

        return False

    def destroyUI(self, hideOnly=False):
        self.__destroy(hideOnly)
        if not hideOnly:
            self.__alreadyJoinedAccountDBIDs.clear()
            self.__isActiveSearchView = False
            self.__filterExpander.stop()

    def setPlatoonPopoverPosition(self, xPopoverOffset):
        position = self.__calculateDropdownMove(xPopoverOffset)
        for ePlatoonLayout in ePlatoonLayouts:
            if ePlatoonLayout != EPlatoonLayout.MEMBER:
                view = self.__getView(ePlatoonLayout)
                if view:
                    view.getParentWindow().move(position.x, position.y)

    def getExpandedSearchFlags(self):
        expander = self.__filterExpander
        if self.isInSearch():
            searchFlags = self.getCurrentSearchFlags()
        else:
            searchFlags = self.getUserSearchFlags()
        expandedTiersFilter = expander.getExpandedFilter()
        expandedSearchFlags = searchFlags | expandedTiersFilter
        return (expandedSearchFlags, expander.isExpanded())

    def hasFreeSlot(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            if unitMgr.unit.getFreeSlots():
                return True
            return False
        return False

    def getMaxSlotCount(self):
        unitMgr = prb_getters.getClientUnitMgr()
        return unitMgr.unit.getMaxSlotCount() if unitMgr and unitMgr.unit else 0

    def getPlatoonSlotsData(self):
        entity = self.prbEntity
        orderedSlots = {}
        if isinstance(entity, UnitEntity):
            unitFullData = entity.getUnitFullData(entity.getID())
            if unitFullData.unit is None:
                return orderedSlots
            _, slots = vo_converters.makeSlotsVOs(entity, entity.getID(), withPrem=True)
            squadSize = unitFullData.unit.getSquadSize() or len(slots)
            orderedSlots = self.orderSlotsBasedOnDisplaySlotsIndices(slots)[:squadSize]
        return orderedSlots

    def buildExtendedSquadInfoVo(self):
        commanderIndex = 0
        squadManStates = []
        if self.isInPlatoon():
            count = 0
            slots = self.getPlatoonSlotsData()
            for it in slots:
                player = it['player']
                role = it['role']
                squadManStates.append(self.getSquadManStates(player, role))
                if player is not None:
                    if player['isCommander']:
                        commanderIndex = count
                count += 1

        return SquadInfo(self.getPlatoonStateForSquadVO().value, squadManStates, commanderIndex)

    def getPrbEntity(self):
        return self.prbEntity

    def getQueueType(self):
        return self.prbEntity.getQueueType() if self.prbEntity else QUEUE_TYPE.UNKNOWN

    def getPrbEntityType(self):
        state = self.getFunctionalState()
        queueType = self.getQueueType()
        if state and state.isInPreQueue(queueType):
            if queueType in QUEUE_TYPE_TO_PREBATTLE_TYPE:
                return QUEUE_TYPE_TO_PREBATTLE_TYPE[queueType]
            return PREBATTLE_TYPE.NONE
        return self.prbEntity.getEntityType() if self.prbEntity else PREBATTLE_TYPE.NONE

    def isUnitWithPremium(self):
        unitData = self.prbEntity.getUnitFullData()
        return any((slot.player.hasPremium for slot in unitData.slotsIterator if slot.player))

    def getChannelController(self):
        if self.__channelCtrl is None:
            clientID = channel_num_gen.getClientID4Prebattle(self.getPrbEntityType())
            channelsCtrl = MessengerEntry.g_instance.gui.channelsCtrl
            if channelsCtrl is not None:
                self.__channelCtrl = channelsCtrl.getController(clientID)
                if self.__channelCtrl is not None:
                    self.onChannelControllerChanged(self.__channelCtrl)
        return self.__channelCtrl

    def requestPlayerQueueInfo(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            currPlayer.requestQueueInfo(QUEUE_TYPE.UNIT_ASSEMBLER)
        return

    def canSelectSquadSize(self):
        prbType = self.getPrbEntityType()
        return prbType in [PREBATTLE_TYPE.COMP7]

    def hasSelectorPopover(self):
        return self.hasWelcomeWindow() or self.canSelectSquadSize() or self.getPermissions().hasSquadArrow()

    def hasSearchSupport(self):
        prbType = self.getPrbEntityType()
        return self.__lobbyContext.getServerSettings().unitAssemblerConfig.isPrebattleSupported(prbType)

    def hasWelcomeWindow(self):
        return self.hasSearchSupport() or self.__shouldChangeToRandomAndShowWindow()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        _logger.debug('PlatoonController: onUnitFlagsChanged')
        if flags.isSearchStateChanged():
            if flags.isInSearch():
                self.__filterExpander.start(self.getCurrentSearchFlags())
                self.__closeSendInviteView()
            else:
                self.__filterExpander.stop()
        self.onMembersUpdate()

    def onUnitSearchFlagsChanged(self, _):
        self.__updateExpanderSearchFlags()

    def onUnitVehiclesChanged(self, dbID, vInfos):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        else:
            _logger.debug('PlatoonController: onUnitVehiclesChanged')
            entity = self.prbEntity
            pInfo = entity.getPlayerInfo(dbID=dbID)
            needToUpdateSlots = self.__eventsCache.isSquadXpFactorsEnabled()
            if pInfo.isInSlot:
                slotIdx = pInfo.slotIdx
                if vInfos and not vInfos[0].isEmpty():
                    vInfo = vInfos[0]
                    vehicleVO = makeVehicleVO(self.__itemsCache.items.getItemByCD(vInfo.vehTypeCD), entity.getRosterSettings().getLevelsRange(), isCurrentPlayer=pInfo.isCurrentPlayer())
                else:
                    vehicleVO = None
                if pInfo.isCurrentPlayer():
                    if len(vInfos) < slotIdx + 1:
                        needToUpdateSlots = True
                elif vehicleVO is None:
                    needToUpdateSlots = True
            if needToUpdateSlots:
                self.onMembersUpdate()
            return

    def onUnitPlayerInfoChanged(self, pInfo):
        if self.getPrbEntityType() in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            self.onMembersUpdate()

    def onUnitRosterChanged(self):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        self.onMembersUpdate()

    def onUnitMembersListChanged(self):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        _logger.debug('PlatoonController: onUnitMembersListChanged')
        self.__updatePlatoonTankInfo()

    def onUnitPlayerAdded(self, pInfo):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        _logger.debug('PlatoonController: onUnitPlayerAdded')
        self.__addPlayerJoinNotification(pInfo)
        if pInfo.isInSlot:
            SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_platoon_2_member_joined()))
        self.__areOtherMembersReady = False
        self.__onUnitPlayersListChanged()

    def onUnitPlayerRemoved(self, pInfo):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        _logger.debug('PlatoonController: onUnitPlayerRemoved')
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_REMOVED, pInfo)
            if pInfo.dbID in self.__alreadyJoinedAccountDBIDs:
                self.__alreadyJoinedAccountDBIDs.remove(pInfo.dbID)
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_platoon_2_member_left()))
        self.__updatePlatoonTankInfo()

    def onUnitPlayerStateChanged(self, pInfo):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        _logger.debug('PlatoonController: onUnitPlayerStateChanged')
        self.onMembersUpdate()
        if self.__isActiveSearchView:
            if not self.isInSearch():
                self.__isActiveSearchView = False
                self.destroyUI(hideOnly=True)
        self.__checkOtherPlatoonMembersReady(pInfo)
        self.__updatePlatoonTankInfo()

    def onUnitPlayerOnlineStatusChanged(self, pInfo):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        if pInfo.isOffline():
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_OFFLINE
        else:
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_ONLINE
        self.__addPlayerNotification(key, pInfo)
        self.onMembersUpdate()

    def onUnitPlayerBecomeCreator(self, pInfo):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        if self.getChannelController():
            self.__channelCtrl.addMessage(messages.getUnitPlayerNotification(settings.UNIT_NOTIFICATION_KEY.GIVE_LEADERSHIP, pInfo))
        self.onMembersUpdate()

    def onUnitPlayerProfileVehicleChanged(self, accountDBID):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        self.onMembersUpdate()

    def hasVehiclesForSearch(self, tierLevel=None):
        return bool(self.__availableTiersForSearch) if tierLevel is None else self.__availableTiersForSearch & 1 << tierLevel != 0

    def orderSlotsBasedOnDisplaySlotsIndices(self, slots):
        self.__updateDisplaySlotsIndices()
        emptySlot = findFirst(lambda slot: slot['player'] is None, slots)
        orderedSlots = [emptySlot] * len(slots)
        for slot in slots:
            playerAccId = slot['player']['accID'] if slot['player'] else -1
            for playerId, displayIndex in self.__tankDisplayPosition.items():
                if playerAccId == playerId:
                    if displayIndex >= len(orderedSlots):
                        _logger.warning('The number %s of display slots in the platoon is invalid', displayIndex)
                        return slots
                    orderedSlots[displayIndex] = slot
                    break

        return orderedSlots

    def getPlatoonStateForSquadVO(self):
        if isinstance(self.prbEntity, UnitEntity):
            if self.__isActiveSearchView:
                return EPlatoonButtonState.SEARCHING_STATE
            return EPlatoonButtonState.IN_PLATOON_STATE
        return EPlatoonButtonState.CREATE_STATE

    def getSquadManStates(self, player, role):
        if player is not None:
            accID = BigWorld.player().id
            if role is not None and role & UNIT_ROLE.IN_ARENA:
                return 'inBattle'
            if player['readyState']:
                return 'ready'
            if accID != player['accID']:
                return 'notReady'
            return 'notReadyPlayer'
        else:
            return 'searching' if self.isInSearch() else 'empty'

    def __addPlayerJoinNotification(self, pInfo):
        if not pInfo or pInfo.isInvite() or pInfo.isCurrentPlayer() or pInfo.dbID in self.__alreadyJoinedAccountDBIDs:
            return
        self.__alreadyJoinedAccountDBIDs.add(pInfo.dbID)
        autoSearchFlag = self.__getSearchFlagByDBID(pInfo.dbID)
        if autoSearchFlag and autoSearchFlag & UnitAssemblerSearchFlags.ALL_VEH_TIERS != UnitAssemblerSearchFlags.ALL_VEH_TIERS:
            autoSearchFlag = toRomanRangeString(convertTierFilterToList(autoSearchFlag), 1)
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED_WITH_FILTER, pInfo, autoSearchFlag)
        else:
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)

    def __getPlayers(self, unitMgrID=None):
        return self.prbEntity.getPlayers(unitMgrID) if isinstance(self.prbEntity, UnitEntity) else {}

    @staticmethod
    def __closeSendInviteView():
        g_eventBus.handleEvent(events.DestroyViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onUnitPlayersListChanged(self):
        if self.__getPlayerCount() > 1:
            self.__isActiveSearchView = False
            if not self.__getView(EPlatoonLayout.MEMBER):
                self.__showWindow(EPlatoonLayout.MEMBER)
            else:
                self.onMembersUpdate()

    @adisp_process
    def __jumpToBattleMode(self, prbActionName, ePlatoonLayout, xPopoverOffset=None):
        result = yield self.prbDispatcher.doSelectAction(PrbAction(prbActionName))
        if result:
            self.__showWindow(ePlatoonLayout, xPopoverOffset)

    def __shouldChangeToRandomAndShowWindow(self):
        return self.getPrbEntityType() in (PREBATTLE_TYPE.TRAINING, PREBATTLE_TYPE.STRONGHOLD)

    def __getPlayerCount(self):
        players = self.prbEntity.getPlayers()
        return len(players)

    def __checkOtherPlatoonMembersReady(self, pInfo):
        if pInfo.isCurrentPlayer():
            return
        numNotReadyPlayers = self.__getNotReadyPlayersCount()
        if numNotReadyPlayers > 0:
            self.__areOtherMembersReady = False
        elif numNotReadyPlayers == 0 and not self.__areOtherMembersReady:
            self.__areOtherMembersReady = True
            currentPlayerInfo = self.prbEntity.getPlayerInfo()
            if currentPlayerInfo.isCommander():
                SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_platoon_2_all_members_ready()))

    def __startAutoSearchCallback(self, isStarted):
        self.__startAutoSearchOnUnitJoin = False

    def isPlayerRoleAutoSearch(self):
        playerInfo = self.getPlayerInfo()
        if playerInfo:
            isAutoSearch = bool(playerInfo.role & UNIT_ROLE.AUTO_SEARCH)
            return isAutoSearch
        return False

    @adisp_process
    def __doSelect(self, prebattelActionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(prebattelActionName))

    def __showWindow(self, ePlatoonLayout, dropdownOffset=None):
        view = self.__getView(ePlatoonLayout)
        if self.__isViewProperPrbType(view):
            if view.getParentWindow().isHidden():
                view.getParentWindow().show()
            return
        else:
            self.__destroy(hideOnly=False)
            layout = self.currentPlatoonLayouts.get(ePlatoonLayout)
            if layout is None:
                _logger.error('Layout %s is missing.', ePlatoonLayout)
                return
            position = self.__calculateDropdownMove(dropdownOffset)
            window = layout.windowClass(position)
            if window is None:
                _logger.error('Window creation of type %s is failing', ePlatoonLayout)
                return
            window.load()
            if ePlatoonLayout == EPlatoonLayout.MEMBER:
                window.center()
                if self.__isPlatoonVisualizationEnabled:
                    self.onPlatoonTankVisualizationChanged(True)
                if not self.isInSearch() and not self.prbEntity.isInQueue() and isinstance(self.prbEntity, SquadEntity):
                    self.prbEntity.loadHangar()
            return

    def __destroy(self, hideOnly):
        for ePlatoonLayout in ePlatoonLayouts:
            view = self.__getView(ePlatoonLayout)
            if view:
                if hideOnly:
                    if not view.getParentWindow().isHidden():
                        view.getParentWindow().hide()
                else:
                    if ePlatoonLayout == EPlatoonLayout.MEMBER and self.__isPlatoonVisualizationEnabled:
                        self.onPlatoonTankVisualizationChanged(False)
                    view.getParentWindow().destroy()

        self.__closeSendInviteView()

    def __getView(self, ePlatoonLayout):
        layout = self.currentPlatoonLayouts.get(ePlatoonLayout)
        if not layout:
            return None
        else:
            uiLoader = dependency.instance(IGuiLoader)
            view = uiLoader.windowsManager.getViewByLayoutID(layoutID=layout.layoutID)
            return view

    def __isViewProperPrbType(self, view):
        if view is None:
            return False
        else:
            prbEntityType = self.getPrbEntityType()
            return prbEntityType and view.getPrbEntityType() == prbEntityType

    def __startListening(self):
        _logger.debug('PlatoonController: start listening')
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            _logger.debug('PLATOON: UnitMgr!')
            unitMgr.onUnitJoined += self.__unitMgrOnUnitJoined
            unitMgr.onUnitLeft += self.__unitMgrOnUnitLeft
        self.startGlobalListening()
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__settingsCore.onSettingsApplied += self.__onSettingsApplied
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__hangarSpace.onSpaceCreate += self.__onHangarSpaceCreate
        self.__hangarSpace.onSpaceDestroy += self.hsSpaceDestroy
        self.__itemsCache.onSyncCompleted += self.__onVehicleStateChanged
        g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__platoonTankLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__platoonTankDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__onChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def __onServerSettingsChanged(self, diff):
        if Configs.UNIT_ASSEMBLER_CONFIG.value in diff:
            self.__cacheAvailableVehicles(checkVehicles=False)
            self.__updateUserSearchFlagsOnAvailableTiers()

    def __onChannelControllerInited(self, event):
        ctx = event.ctx
        prbType = ctx.get('prbType', 0)
        if not prbType:
            _logger.debug('Prebattle type %d is not defined', prbType)
            return
        elif prbType not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        else:
            controller = ctx.get('controller')
            if controller is None:
                _logger.error('Channel controller is not defined %s', str(ctx))
                return
            ctx.clear()
            self.__channelCtrl = controller
            self.onChannelControllerChanged(self.__channelCtrl)
            players = self.__getPlayers()
            for _, pInfo in players.iteritems():
                self.__addPlayerJoinNotification(pInfo)

            return

    def __onHangarSpaceCreate(self):
        self.__currentlyDisplayedTanks = 0
        if not self.isInPlatoon():
            return
        needToShowOtherPlayers = bool([ player for player in self.prbEntity.getPlayers().values() if player.isReady and not player.isInArena() and not player.isCurrentPlayer() ])
        if not needToShowOtherPlayers:
            return
        self.__updatePlatoonTankInfo()
        cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
        if cameraManager:
            cameraManager.enablePlatoonMode(True)

    def __stopListening(self):
        _logger.debug('PlatoonController: stop listening')
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__unitMgrOnUnitJoined
            unitMgr.onUnitLeft -= self.__unitMgrOnUnitLeft
        self.stopGlobalListening()
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__settingsCore.onSettingsApplied -= self.__onSettingsApplied
        self.__hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreate
        self.__hangarSpace.onSpaceDestroy -= self.hsSpaceDestroy
        self.__itemsCache.onSyncCompleted -= self.__onVehicleStateChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__platoonTankLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__platoonTankDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__onChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.AUTO_SEARCH:
            self.__fireOnAutoSearchCooldownChanged(isInCooldown=True)
            self.delayCallback(event.coolDown, self.__fireOnAutoSearchCooldownChanged, isInCooldown=False)

    def __fireOnAutoSearchCooldownChanged(self, isInCooldown):
        self.onAutoSearchCooldownChanged(isInCooldown)

    def __unitMgrOnUnitJoined(self, unitMgrID, prbType):
        _logger.debug('PlatoonController: __unitMgrOnUnitJoined')
        if prbType not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        self.__tankDisplayPosition.clear()
        serverSettings = self.__settingsCore.serverSettings
        if not serverSettings.getOnceOnlyHintsSettings().get(OnceOnlyHints.PLATOON_BTN_HINT, False):
            self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.PLATOON_BTN_HINT: True})
        if self.hasDelayedCallback(self.destroyUI):
            self.stopCallback(self.destroyUI)
        if self.__startAutoSearchOnUnitJoin:
            self.startSearch()
        else:
            self.__onUnitPlayersListChanged()
        if self.isInSearch():
            self.__filterExpander.start(self.getCurrentSearchFlags())
        self.__updatePlatoonTankInfo()

    def __unitMgrOnUnitLeft(self, unitMgrID, isFinishedAssembling):
        _logger.debug('PlatoonController: __unitMgrOnUnitLeft')
        if isFinishedAssembling:
            self.delayCallback(0.5, self.destroyUI)
        else:
            self.destroyUI()
        self.__tankDisplayPosition.clear()

    def __calculateDropdownMove(self, xOffset):
        if xOffset is not None:
            x = xOffset - self.DROPDOWN_HALF_WIDTH
            return Position(x, self.DROPDOWN_Y_OFFSET)
        else:
            return

    def __addPlayerNotification(self, key, pInfo, tierRange=None):
        if self.getChannelController():
            msg = messages.getUnitPlayerNotification(key, pInfo, tierRange)
            self.__channelCtrl.addMessage(msg)

    def __getSearchFlagByDBID(self, accountDBID):
        unitMgr = prb_getters.getClientUnitMgr()
        return unitMgr.unit.getAutoSearchFlagsOfAccount(accountDBID) if unitMgr and unitMgr.unit else 0

    def __onAppResolutionChanged(self, event):
        ctx = event.ctx
        if 'width' not in ctx:
            _logger.error('Application width is not found: %r', ctx)
            return
        if 'height' not in ctx:
            _logger.error('Application height is not found: %r', ctx)
            return
        if 'scale' not in ctx:
            _logger.error('Application scale is not found: %r', ctx)
            return
        if isinstance(self.prbEntity, UnitEntity):
            self.onPlatoonTankVisualizationChanged(False)
            self.__updatePlatoonTankInfo()

    def __platoonTankLoaded(self, event):
        self.__currentlyDisplayedTanks += 1
        if self.__currentlyDisplayedTanks == 1:
            cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
            if cameraManager:
                cameraManager.enablePlatoonMode(True)

    def __platoonTankDestroyed(self, event):
        self.__currentlyDisplayedTanks = max(0, self.__currentlyDisplayedTanks - 1)
        if self.__currentlyDisplayedTanks <= 0:
            cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
            if cameraManager:
                cameraManager.enablePlatoonMode(False)

    def __getNotReadyPlayersCount(self):
        players = self.prbEntity.getPlayers().values()
        notReadyPlayers = [ player for player in players if not player.isReady and not player.isCurrentPlayer() ]
        return len(notReadyPlayers)

    def __onSettingsChanged(self, diff):
        displayPlatoonMembers = diff.get(GAME.DISPLAY_PLATOON_MEMBERS)
        if displayPlatoonMembers is None:
            return
        else:
            self.__isPlatoonVisualizationEnabled = displayPlatoonMembers
            isInPlatoon = self.isInPlatoon()
            self.onPlatoonTankVisualizationChanged(self.__isPlatoonVisualizationEnabled and isInPlatoon)
            self.__updatePlatoonTankInfo()
            return

    def __onSettingsApplied(self, diff):
        isDisplayMemberChanged = GAME.DISPLAY_PLATOON_MEMBERS in diff
        if isDisplayMemberChanged and self.__checkForSettingsModification():
            filters = self.__getFilters()
            filters[GuiSettingsBehavior.DISPLAY_PLATOON_MEMBER_CLICKED] = True
            self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)

    def __getFilters(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __checkForSettingsModification(self):
        filters = self.__getFilters()
        isDisplayPlatoonMembersClicked = filters[GuiSettingsBehavior.DISPLAY_PLATOON_MEMBER_CLICKED]
        return not isDisplayPlatoonMembersClicked

    def __validateSystemReq(self):
        recomPreset = BigWorld.detectGraphicsPresetFromSystemSettings()
        currentGpuMemory = BigWorld.getAutoDetectGraphicsSettingsScore(HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY)
        displayPlatoonMembersEnabled = self.__settingsCore.getSetting(GAME.DISPLAY_PLATOON_MEMBERS)
        restricted = False
        presetId = BigWorld.getSystemPerformancePresetIdFromName(_MIN_PERF_PRESET_NAME)
        if presetId == recomPreset:
            restricted = True
        changeRequired = False
        if restricted or currentGpuMemory < 500:
            if displayPlatoonMembersEnabled:
                changeRequired = True
        elif not displayPlatoonMembersEnabled:
            changeRequired = True
        if changeRequired:
            self.__settingsCore.applySetting(GAME.DISPLAY_PLATOON_MEMBERS, not displayPlatoonMembersEnabled)
            confirmations = self.__settingsCore.applyStorages(False)
            self.__settingsCore.confirmChanges(confirmations)
            self.__settingsCore.clearStorages()

    def hsSpaceDestroy(self, inited):
        if inited:
            self.__availablePlatoonTanks.clear()

    def __updatePlatoonTankInfo(self):
        entity = self.prbEntity
        if entity is None or not hasattr(entity, 'getRosterSettings'):
            return
        else:
            unitSlotCount = entity.getRosterSettings().getMaxSlots()
            isPlayerOnSlotAvailable = {i:False for i in range(unitSlotCount)}
            result = dict()
            if not self.__hasEnoughSlots(unitSlotCount) or not self.__isPlatoonVisualizationEnabled:
                self.onPlatoonTankVisualizationChanged(False)
                return
            self.__updateDisplaySlotsIndices()
            unitMgrID = entity.getID()
            for slot in entity.getSlotsIterator(*entity.getUnit(unitMgrID=unitMgrID)):
                if slot.player is not None and not slot.player.isCurrentPlayer():
                    canDisplayModel = slot.player.isReady and not slot.player.isInArena()
                    profileVehicle = slot.profileVehicle
                    player = slot.player
                    if profileVehicle and player:
                        tankInfo = PlatoonTankInfo(canDisplayModel, profileVehicle.vehCompDescr, profileVehicle.vehOutfitCD, profileVehicle.seasonType, profileVehicle.marksOnGun, player.clanDBID, player.getFullName())
                    else:
                        tankInfo = None
                    displaySlotIndex = self.__tankDisplayPosition.get(player.accID, 0)
                    result[displaySlotIndex] = tankInfo
                    isPlayerOnSlotAvailable[displaySlotIndex] = True

            for displaySlotIndex, isAvailable in isPlayerOnSlotAvailable.iteritems():
                if not isAvailable:
                    result[displaySlotIndex] = None

            self.onPlatoonTankUpdated(result)
            return

    def __clearPlatoonTankInfo(self):
        self.onPlatoonTankUpdated({i:False for i in self.__availablePlatoonTanks})

    def __hasEnoughSlots(self, slots):
        return len(self.__availablePlatoonTanks) + 1 >= slots

    def __updateDisplaySlotsIndices(self):
        players = self.prbEntity.getPlayers()
        playerIds = [ player.accID for player in players.values() if player.isInSlot ]
        maxSlotCount = self.prbEntity.getRosterSettings().getMaxSlots()
        if len(playerIds) > maxSlotCount:
            _logger.warning('The number of players in slot (%s) is higher then max slots to display (%s). This state should not happen for this type of unit.', len(playerIds), maxSlotCount)
        if maxSlotCount >= 3:
            self.__updateDisplaySlotsIndicesForPlayers(playerIds, maxSlotCount)
        elif maxSlotCount == 2:
            self.__updateDisplaySlotsIndicesFor2Players(players)

    def __updateDisplaySlotsIndicesForPlayers(self, playerIds, maxSlotCount):
        if not self.__tankDisplayPosition:
            nextDisplayIndex = 0
            if maxSlotCount == _MAX_SLOT_COUNT_FOR_PLAYER_RESORTING:
                currentPlayerIndex = 1
                accID = BigWorld.player().id
                for playerId in playerIds:
                    isCurrentPlayer = playerId == accID
                    if isCurrentPlayer:
                        displaySlot = currentPlayerIndex
                    else:
                        displaySlot = nextDisplayIndex
                        nextDisplayIndex += 1
                        if nextDisplayIndex == currentPlayerIndex:
                            nextDisplayIndex += 1
                    self.__tankDisplayPosition[playerId] = displaySlot

            else:
                for playerId in playerIds:
                    displaySlot = nextDisplayIndex
                    nextDisplayIndex += 1
                    self.__tankDisplayPosition[playerId] = displaySlot

            return
        for playerId, _ in self.__tankDisplayPosition.items():
            if playerId in playerIds:
                playerIds.remove(playerId)
                continue
            self.__removeAccFromPositions(playerId)

        availableSlotIndex = 0
        for newPlayerId in playerIds:
            while availableSlotIndex in self.__tankDisplayPosition.values():
                availableSlotIndex += 1

            self.__tankDisplayPosition[newPlayerId] = availableSlotIndex

    def __updateDisplaySlotsIndicesFor2Players(self, players):
        currentPlayer = [ player for player in players.values() if player.isInSlot and player.isCurrentPlayer() ][0]
        teamMate = [ player for player in players.values() if player.isInSlot and not player.isCurrentPlayer() ]
        if teamMate:
            teamMateAccID = teamMate[0].accID
            currentPlayerIdx = 1
            newSlotIdx, removeSlotIdx = (2, 0) if currentPlayer.isCommander() else (0, 2)
            if self.__tankDisplayPosition.get(teamMateAccID) == removeSlotIdx:
                self.onPlatoonTankRemove(removeSlotIdx)
                self.__removeAccFromPositions(teamMateAccID)
            self.__tankDisplayPosition[teamMateAccID] = newSlotIdx
        else:
            allTeams = [ data for data in self.__tankDisplayPosition.iteritems() if data[0] != currentPlayer.accID ]
            if allTeams:
                teamMateAccID, teamMateIdx = allTeams[0]
                self.onPlatoonTankRemove(teamMateIdx)
                self.__removeAccFromPositions(teamMateAccID)
            currentPlayerIdx = 0
        self.__tankDisplayPosition[currentPlayer.accID] = currentPlayerIdx

    def __removeAccFromPositions(self, accID):
        maxSlotCount = self.prbEntity.getRosterSettings().getMaxSlots()
        removedIdx = self.__tankDisplayPosition.pop(accID, None)
        currPlayerIdx = self.__tankDisplayPosition[BigWorld.player().id]
        if removedIdx is not None:
            if maxSlotCount == _MAX_SLOT_COUNT_FOR_PLAYER_RESORTING:
                for playerID, slotIdx in self.__tankDisplayPosition.iteritems():
                    if slotIdx > removedIdx:
                        if slotIdx == currPlayerIdx + 1:
                            self.__tankDisplayPosition[playerID] = slotIdx - 2
                        elif slotIdx != currPlayerIdx:
                            self.__tankDisplayPosition[playerID] = slotIdx - 1

            else:
                for playerID, slotIdx in self.__tankDisplayPosition.iteritems():
                    if slotIdx > removedIdx:
                        self.__tankDisplayPosition[playerID] = slotIdx - 1

        return

    def __onVehicleStateChanged(self, updateReason, diff):
        if updateReason == CACHE_SYNC_REASON.CLIENT_UPDATE and (not diff or GUI_ITEM_TYPE.VEHICLE not in diff):
            return
        if updateReason in (CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC):
            self.__cacheAvailableVehicles()

    def __cacheAvailableVehicles(self, checkVehicles=True):
        if not self.hasSearchSupport():
            return
        elif not self.isSearchingForPlayersEnabled():
            if self.__availableTiersForSearch != 0:
                self.__availableTiersForSearch = 0
                self.onAvailableTiersForSearchChanged()
            return
        else:
            prebattleType = self.getPrbEntityType()
            allowedLevels = self.getAllowedTankLevels(prebattleType)
            if checkVehicles or self.__availableTiersInventory is None:
                criteria = REQ_CRITERIA.INVENTORY
                criteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
                criteria |= PREBATTLE_TYPE_TO_VEH_CRITERIA.get(prebattleType, REQ_CRITERIA.EMPTY)
                allowedList = [ lvl for lvl in range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1) if allowedLevels & 1 << lvl ]
                criteria |= REQ_CRITERIA.VEHICLE.LEVELS(allowedList)
                vehicles = self.__itemsCache.items.getVehicles(criteria)
                self.__availableTiersInventory = 0
                for v in vehicles.itervalues():
                    state, vStateLvl = v.getState()
                    if state in (Vehicle.VEHICLE_STATE.LOCKED, Vehicle.VEHICLE_STATE.IN_PREBATTLE) and v.checkUndamagedState(Vehicle.VEHICLE_STATE.UNDAMAGED) == Vehicle.VEHICLE_STATE.UNDAMAGED or vStateLvl not in (Vehicle.VEHICLE_STATE_LEVEL.CRITICAL,
                     Vehicle.VEHICLE_STATE_LEVEL.WARNING,
                     Vehicle.VEHICLE_STATE_LEVEL.RENTABLE,
                     Vehicle.VEHICLE_STATE_LEVEL.ATTENTION):
                        self.__availableTiersInventory |= 1 << v.level

            availableTiers = self.__availableTiersInventory & allowedLevels
            if availableTiers != self.__availableTiersForSearch:
                self.__availableTiersForSearch = availableTiers
                self.__updateUserSearchFlagsOnAvailableTiers()
                self.onAvailableTiersForSearchChanged()
            return

    def __updateUserSearchFlagsOnAvailableTiers(self):
        userSearchFlags = self.getUserSearchFlags()
        userVehFlags = userSearchFlags & self.__availableTiersForSearch & UnitAssemblerSearchFlags.ALL_VEH_TIERS
        newUserSearchFlags = userSearchFlags & ~UnitAssemblerSearchFlags.ALL_VEH_TIERS | userVehFlags
        if userSearchFlags != newUserSearchFlags:
            self.saveUserSearchFlags(newUserSearchFlags)

    def __updateExpanderSearchFlags(self):
        if self.isInSearch():
            searchFlags = self.getCurrentSearchFlags()
        else:
            searchFlags = self.getUserSearchFlags()
        self.__filterExpander.updateSearchFlags(searchFlags)
