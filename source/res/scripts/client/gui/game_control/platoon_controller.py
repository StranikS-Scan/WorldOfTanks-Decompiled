# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/platoon_controller.py
import logging
from collections import namedtuple
from enum import Enum
from typing import TYPE_CHECKING
import BigWorld
import Event
import SoundGroups
import VOIP
from UnitBase import UNIT_ROLE, UnitAssemblerSearchFlags
from constants import EPlatoonButtonState, MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from PlatoonTank import PlatoonTank, PlatoonTankInfo
from account_helpers.AccountSettings import AccountSettings, UNIT_FILTER, GUI_START_BEHAVIOR
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GAME, GuiSettingsBehavior
from adisp import process, async
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.platoon_helpers import convertTierFilterToList
from gui.impl.lobby.platoon.view.platoon_members_view import MembersWindow
from gui.impl.lobby.platoon.view.platoon_search_view import SearchWindow
from gui.impl.lobby.platoon.view.platoon_welcome_view import SelectionWindow
from gui.prb_control import prb_getters
from gui.prb_control import settings
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.unit.ctx import AutoSearchUnitCtx
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.formatters import messages
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.statistics import HARDWARE_SCORE_PARAMS
from messenger import MessengerEntry
from messenger.ext import channel_num_gen
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPlatoonController, IEventProgressionController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, PREBATTLE_TYPE
from gui.prb_control.entities.base.unit.permissions import UnitPermissions
from gui.prb_control.entities.base.unit.entity import UnitEntity
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import Vehicle
from gui.prb_control.settings import REQUEST_TYPE
if TYPE_CHECKING:
    from typing import Optional as TOptional
    from UnitBase import ProfileVehicle
_logger = logging.getLogger(__name__)
_QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME = {QUEUE_TYPE.EVENT_BATTLES: PREBATTLE_ACTION_NAME.SQUAD,
 QUEUE_TYPE.RANDOMS: PREBATTLE_ACTION_NAME.SQUAD,
 QUEUE_TYPE.EPIC: PREBATTLE_ACTION_NAME.SQUAD,
 QUEUE_TYPE.BATTLE_ROYALE: PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD}
_QUEUE_TYPE_TO_PREBATTLE_TYPE = {QUEUE_TYPE.EVENT_BATTLES: PREBATTLE_TYPE.EVENT,
 QUEUE_TYPE.RANDOMS: PREBATTLE_TYPE.SQUAD,
 QUEUE_TYPE.EPIC: PREBATTLE_TYPE.EPIC,
 QUEUE_TYPE.BATTLE_ROYALE: PREBATTLE_TYPE.BATTLE_ROYALE}
_PREBATTLE_TYPE_TO_VEH_CRITERIA = {PREBATTLE_TYPE.SQUAD: ~(REQ_CRITERIA.VEHICLE.EPIC_BATTLE ^ REQ_CRITERIA.VEHICLE.BATTLE_ROYALE ^ REQ_CRITERIA.VEHICLE.EVENT_BATTLE),
 PREBATTLE_TYPE.EPIC: ~(REQ_CRITERIA.VEHICLE.BATTLE_ROYALE ^ REQ_CRITERIA.VEHICLE.EVENT_BATTLE),
 PREBATTLE_TYPE.BATTLE_ROYALE: REQ_CRITERIA.VEHICLE.BATTLE_ROYALE,
 PREBATTLE_TYPE.EVENT: REQ_CRITERIA.VEHICLE.EVENT_BATTLE}
_MIN_PERF_PRESET_NAME = 'MIN'
SquadInfo = namedtuple('SquadInfo', ['platoonState', 'squadManStates', 'commanderIndex'])
Position = namedtuple('Position', ['x', 'y'])
_PlatoonLayout = namedtuple('_PlatoonLayout', ('layoutID', 'windowClass'))
_PrbEntityInfo = namedtuple('_PrbEntityInfo', ['queueType', 'prebattleType'])

class _EPlatoonLayout(Enum):
    WELCOME = 0
    SEARCH = 1
    MEMBER = 2


class _FilterExpander(CallbackDelayer):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(_FilterExpander, self).__init__()
        self.__filter = None
        self.__nextDelayGenerator = None
        return

    def start(self, unitFilter):
        self.clearCallbacks()
        self.__filter = convertTierFilterToList(unitFilter)
        delayListByTiers = self.__getExtendDelaysByTiers()
        self.__nextDelayGenerator = self.__getNextDelayByTier(delayListByTiers)
        delayByTier = next(self.__nextDelayGenerator, None)
        if delayByTier is not None:
            self.delayCallback(delayByTier, self.__refreshCurrentlySearchedTiers)
        return

    def __getExtendDelaysByTiers(self):
        queueType = self.__platoonCtrl.getQueueType()
        if queueType == QUEUE_TYPE.RANDOMS:
            return self.__lobbyContext.getServerSettings().unitAssemblerConfig.squad['extendTierFilter']
        return self.__lobbyContext.getServerSettings().unitAssemblerConfig.epic['extendTierFilter'] if queueType == QUEUE_TYPE.EPIC else []

    def __refreshCurrentlySearchedTiers(self):
        if self.__platoonCtrl.isInSearch():
            if self.__extendCurrentTierFilter():
                self.__platoonCtrl.setNewTierFilter(self.__filter, isExpanded=True)
                return next(self.__nextDelayGenerator, None)
        return None

    def __extendCurrentTierFilter(self):
        copy = self.__filter[:]
        for it in copy:
            plus = it + 1
            minus = it - 1
            if it > 1 and minus not in self.__filter:
                self.__filter.append(minus)
            if it < 10 and plus not in self.__filter:
                self.__filter.append(plus)

        self.__filter.sort()
        return copy != self.__filter

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
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self):
        super(PlatoonController, self).__init__()
        CallbackDelayer.__init__(self)
        self.__ePlatoonLayouts = {_EPlatoonLayout.WELCOME: _PlatoonLayout(R.views.lobby.platoon.PlatoonDropdown(), SelectionWindow),
         _EPlatoonLayout.SEARCH: _PlatoonLayout(R.views.lobby.platoon.SearchingDropdown(), SearchWindow),
         _EPlatoonLayout.MEMBER: _PlatoonLayout(R.views.lobby.platoon.MembersWindow(), MembersWindow)}
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
        self.onFilterUpdate = Event.Event()
        self.onPlatoonTankVisualizationChanged = Event.Event()
        self.onChannelControllerChanged = Event.Event()
        self.onMembersUpdate = Event.Event()
        self.onPlatoonTankUpdated = Event.Event()
        self.onAutoSearchCooldownChanged = Event.Event()
        self.__prevPrbEntityInfo = _PrbEntityInfo(QUEUE_TYPE.UNKNOWN, PREBATTLE_TYPE.NONE)
        return

    def onLobbyInited(self, event):
        validateDisplaySettings = self.__checkForSettingsModification()
        if validateDisplaySettings:
            self.__validateSystemReq()
        self.__isPlatoonVisualizationEnabled = bool(self.__settingsCore.getSetting(GAME.DISPLAY_PLATOON_MEMBERS))
        self.__startListening()

    def onLobbyStarted(self, ctx):
        self.resetUnitTierFilter()

    def onPrbEntitySwitching(self):
        queueType = self.getQueueType()
        prebattleType = self.getPrbEntityType()
        self.__prevPrbEntityInfo = _PrbEntityInfo(queueType, prebattleType)

    def onAccountBecomeNonPlayer(self):
        self.__stopListening()
        self.onPlatoonTankVisualizationChanged(False)
        self.destroyUI()
        self.clearCallbacks()
        self.__isActiveSearchView = False
        self.__startAutoSearchOnUnitJoin = False
        self.__channelCtrl = None
        self.__tankDisplayPosition.clear()
        return

    def getUnitFilter(self):
        defaults = AccountSettings.getFilterDefault(UNIT_FILTER)
        unitFilter = self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.UNIT_FILTER, defaults)
        return unitFilter[GAME.UNIT_FILTER]

    def saveUnitFilter(self, value):
        unitFilter = {GAME.UNIT_FILTER: value}
        self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.UNIT_FILTER, unitFilter)

    def resetUnitTierFilter(self):
        unitFilter = self.getUnitFilter()
        resetedUnitFilter = unitFilter & 1
        self.saveUnitFilter(resetedUnitFilter)

    def getPermissions(self):
        return self.prbEntity.getPermissions()

    @async
    @process
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
        if not self.__executeQueue:
            return
        self.__executeQueue = False
        self.prbDispatcher.doAction(PrbAction(''))

    def leavePlatoon(self, isExit=True, ignoreConfirmation=False):
        action = LeavePrbAction(isExit=isExit, ignoreConfirmation=ignoreConfirmation)
        self.__tankDisplayPosition.clear()
        event = events.PrbActionEvent(action, events.PrbActionEvent.LEAVE)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)

    @process
    def createPlatoon(self, startAutoSearchOnUnitJoin=False):
        queueType = self.getQueueType()
        if queueType in _QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME:
            navigationPossible = startAutoSearchOnUnitJoin
            if not navigationPossible:
                navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
            if navigationPossible:
                if self.prbDispatcher:
                    self.__startAutoSearchOnUnitJoin = startAutoSearchOnUnitJoin
                    self.__isActiveSearchView = startAutoSearchOnUnitJoin
                    self.__doSelect(_QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME[queueType])
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
                searchFlags = self.getUnitFilter()
                if self.__isActiveSearchView:
                    searchFlags |= UnitAssemblerSearchFlags.DESTROY_UNIT_ON_ABORT
                self.prbEntity.doAutoSearch(ctx, self.__startAutoSearchCallback, searchFlags)

    def cancelSearch(self):
        if isinstance(self.prbEntity, UnitEntity) and self.isInSearch():
            ctx = AutoSearchUnitCtx('prebattle/auto_search', action=0)
            self.prbEntity.doAutoSearch(ctx, callback=None)
            self.onFilterUpdate(None, False)
        return

    @async
    @process
    def togglePlayerReadyAction(self, callback):
        changeStatePossible = True
        if not self.prbEntity.getPlayerInfo().isReady:
            changeStatePossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if changeStatePossible:
            self.prbEntity.togglePlayerReadyAction(True)
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
        return unitAssemblerConfig.isAssemblingEnabled(prebattleType) if unitAssemblerConfig.isPrebattleSupported(prebattleType) else False

    def isTankLevelPreferenceEnabled(self):
        prebattleType = self.getPrbEntityType()
        unitAssemblerConfig = self.__lobbyContext.getServerSettings().unitAssemblerConfig
        return unitAssemblerConfig.isTankLevelPreferenceEnabled(prebattleType) if unitAssemblerConfig.isPrebattleSupported(prebattleType) else False

    def getAllowedTankLevels(self, prebattleType):
        unitAssemblerConfig = self.__lobbyContext.getServerSettings().unitAssemblerConfig
        return unitAssemblerConfig.getAllowedTankLevels(prebattleType) if unitAssemblerConfig.isPrebattleSupported(prebattleType) else 0

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
                self.__showWindow(_EPlatoonLayout.SEARCH, xPopoverOffset)
            else:
                self.__showWindow(_EPlatoonLayout.MEMBER)
        elif self.__shouldChangeToRandomAndShowWindow():
            self.__jumpToBattleMode(PREBATTLE_ACTION_NAME.RANDOM, _EPlatoonLayout.WELCOME, xPopoverOffset)
        elif self.hasSearchSupport():
            self.__showWindow(_EPlatoonLayout.WELCOME, xPopoverOffset)
        else:
            self.createPlatoon(startAutoSearchOnUnitJoin=False)

    def isAnyPlatoonUIShown(self):
        for ePlatoonLayout in self.__ePlatoonLayouts:
            view = self.__getView(ePlatoonLayout)
            if view and not view.getParentWindow().isHidden():
                return True

        return False

    def destroyUI(self, hideOnly=False):
        self.__destroy(hideOnly)

    def setPlatoonPopoverPosition(self, xPopoverOffset):
        position = self.__calculateDropdownMove(xPopoverOffset)
        for ePlatoonLayout in self.__ePlatoonLayouts:
            if ePlatoonLayout != _EPlatoonLayout.MEMBER:
                view = self.__getView(ePlatoonLayout)
                if view:
                    view.getParentWindow().move(position.x, position.y)

    def setNewTierFilter(self, newTierFilter, isExpanded):
        _logger.debug('PlatoonController: Expanded tier filter %s', str(newTierFilter))
        if newTierFilter is None:
            newTierFilter = convertTierFilterToList(self.getUnitFilter())
        self.onFilterUpdate(newTierFilter, isExpanded)
        return

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
        if isinstance(self.prbEntity, UnitEntity):
            unitFullData = entity.getUnitFullData(entity.getID())
            if unitFullData.unit is None:
                return orderedSlots
            _, slots = vo_converters.makeSlotsVOs(entity, entity.getID(), withPrem=True)
            self.__updateDisplaySlotsIndices()
            orderedSlots = self.__sortPlatoonSlots(slots)
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
                squadManStates.append(self.__getSquadManStates(player, role))
                if player is not None:
                    if player['isCommander']:
                        commanderIndex = count
                count += 1

        return SquadInfo(self.__getPlatoonStateForSquadVO().value, squadManStates, commanderIndex)

    def getPrbEntity(self):
        return self.prbEntity

    def getQueueType(self):
        return self.prbEntity.getQueueType() if self.prbEntity else QUEUE_TYPE.UNKNOWN

    def getPrbEntityType(self):
        state = self.getFunctionalState()
        queueType = self.getQueueType()
        if state and state.isInPreQueue(queueType):
            if queueType in _QUEUE_TYPE_TO_PREBATTLE_TYPE:
                return _QUEUE_TYPE_TO_PREBATTLE_TYPE[queueType]
            _logger.warning('Queuetype %d is not mapped to prebattletype', queueType)
        return self.prbEntity.getEntityType() if self.prbEntity else PREBATTLE_TYPE.NONE

    def isUnitWithPremium(self):
        unitData = self.prbEntity.getUnitFullData()
        return any((slot.player.hasPremium for slot in unitData.slotsIterator if slot.player))

    def getChannelController(self):
        if self.__channelCtrl is None:
            clientID = channel_num_gen.getClientID4Prebattle(self.getPrbEntityType())
            self.__channelCtrl = MessengerEntry.g_instance.gui.channelsCtrl.getController(clientID)
            if self.__channelCtrl is not None:
                self.onChannelControllerChanged(self.__channelCtrl)
        return self.__channelCtrl

    def requestPlayerQueueInfo(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            currPlayer.requestQueueInfo(QUEUE_TYPE.UNIT_ASSEMBLER)
        return

    def hasSearchSupport(self):
        prbType = self.getPrbEntityType()
        return self.__lobbyContext.getServerSettings().unitAssemblerConfig.isPrebattleSupported(prbType)

    def hasWelcomeWindow(self):
        return self.hasSearchSupport() or self.__shouldChangeToRandomAndShowWindow()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.getPrbEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            return
        _logger.debug('PlatoonController: onUnitFlagsChanged')
        if flags.isSearchStateChanged() and flags.isInSearch():
            self.__closeSendInviteView()
        self.onMembersUpdate()

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
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)
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

    def hasVehiclesForSearch(self, tierLevel=None):
        prebattleType = self.getPrbEntityType()
        allowedLevels = self.getAllowedTankLevels(prebattleType)
        if tierLevel is not None:
            tierAllowed = bool(allowedLevels & 1 << tierLevel)
            if not tierAllowed:
                return False
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.HIDDEN
        criteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        criteria |= _PREBATTLE_TYPE_TO_VEH_CRITERIA.get(prebattleType, REQ_CRITERIA.EMPTY)
        if tierLevel is not None:
            criteria |= REQ_CRITERIA.VEHICLE.LEVEL(tierLevel)
        else:
            allowedList = [ lvl for lvl in range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1) if allowedLevels & 1 << lvl ]
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS(allowedList)
        vehicles = self.__itemsCache.items.getVehicles(criteria)
        for v in vehicles.itervalues():
            state, vStateLvl = v.getState()
            if state in (Vehicle.VEHICLE_STATE.LOCKED, Vehicle.VEHICLE_STATE.IN_PREBATTLE) and v.checkUndamagedState(Vehicle.VEHICLE_STATE.UNDAMAGED) == Vehicle.VEHICLE_STATE.UNDAMAGED:
                return True
            if vStateLvl not in (Vehicle.VEHICLE_STATE_LEVEL.CRITICAL, Vehicle.VEHICLE_STATE_LEVEL.WARNING, Vehicle.VEHICLE_STATE_LEVEL.RENTABLE):
                return True

        return False

    @staticmethod
    def __closeSendInviteView():
        g_eventBus.handleEvent(events.DestroyViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY), scope=EVENT_BUS_SCOPE.LOBBY)

    def __sortPlatoonSlots(self, slots):
        orderedSlots = [ slot for slot in slots ]
        for slot in slots:
            switch = False
            playerAccId = slot['player']['accID'] if slot['player'] else -1
            for playerId, displayIndex in self.__tankDisplayPosition.items():
                if playerAccId == playerId:
                    if displayIndex >= len(orderedSlots):
                        _logger.warning('The number %s of display slots in the platoon is invalid', displayIndex)
                        return slots
                    orderedSlots[displayIndex] = slot
                    switch = True
                    break

            if not switch:
                availableSlotIndex = 0
                while availableSlotIndex in self.__tankDisplayPosition.values():
                    availableSlotIndex += 1

                if availableSlotIndex >= len(orderedSlots):
                    continue
                orderedSlots[availableSlotIndex] = slot
                self.__tankDisplayPosition[playerAccId] = availableSlotIndex

        return orderedSlots

    def __onUnitPlayersListChanged(self):
        if self.__getPlayerCount() > 1:
            self.__isActiveSearchView = False
            if not self.__getView(_EPlatoonLayout.MEMBER):
                self.__showWindow(_EPlatoonLayout.MEMBER)
            else:
                self.onMembersUpdate()

    @process
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
        if isStarted:
            self.__filterExpander.start(self.getUnitFilter())

    @process
    def __doSelect(self, prebattelActionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(prebattelActionName))

    def __showWindow(self, ePlatoonLayout, dropdownOffset=None):
        view = self.__getView(ePlatoonLayout)
        if view:
            if view.getParentWindow().isHidden():
                view.getParentWindow().show()
            return
        else:
            self.__destroy(hideOnly=False, allowPreload=False)
            layout = self.__ePlatoonLayouts.get(ePlatoonLayout)
            if layout is None:
                _logger.error('Layout %s is missing.', ePlatoonLayout)
                return
            position = self.__calculateDropdownMove(dropdownOffset)
            window = layout.windowClass(position)
            if window is None:
                _logger.error('Window creation of type %s is failing', ePlatoonLayout)
                return
            window.load()
            if ePlatoonLayout == _EPlatoonLayout.MEMBER:
                window.center()
                if self.__isPlatoonVisualizationEnabled:
                    self.onPlatoonTankVisualizationChanged(True)
                from gui.prb_control.events_dispatcher import g_eventDispatcher
                if not self.isInSearch():
                    g_eventDispatcher.loadHangar()
            return

    def __destroy(self, hideOnly, allowPreload=True):
        canPreloadWelcomeLayout = False
        for ePlatoonLayout in self.__ePlatoonLayouts:
            view = self.__getView(ePlatoonLayout)
            if view:
                if hideOnly and not view.getParentWindow().isHidden():
                    view.getParentWindow().hide()
                else:
                    canPreloadWelcomeLayout = ePlatoonLayout != _EPlatoonLayout.WELCOME
                    if ePlatoonLayout == _EPlatoonLayout.MEMBER and self.__isPlatoonVisualizationEnabled:
                        self.onPlatoonTankVisualizationChanged(False)
                    view.getParentWindow().destroy()

        if allowPreload and canPreloadWelcomeLayout:
            self.__preloadLayout(_EPlatoonLayout.WELCOME)
        self.__closeSendInviteView()

    def __preloadLayout(self, ePlatoonLayout):
        layout = self.__ePlatoonLayouts.get(ePlatoonLayout)
        welcomeWindow = layout.windowClass()
        welcomeWindow.preload()

    def __getPlatoonStateForSquadVO(self):
        if isinstance(self.prbEntity, UnitEntity):
            if self.__isActiveSearchView:
                return EPlatoonButtonState.SEARCHING_STATE
            return EPlatoonButtonState.IN_PLATOON_STATE
        return EPlatoonButtonState.CREATE_STATE

    def __getSquadManStates(self, player, role):
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

    def __getView(self, ePlatoonLayout):
        layout = self.__ePlatoonLayouts.get(ePlatoonLayout)
        uiLoader = dependency.instance(IGuiLoader)
        return uiLoader.windowsManager.getViewByLayoutID(layoutID=layout.layoutID)

    def __startListening(self):
        _logger.debug('PlatoonController: start listening')
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            _logger.debug('PLATOON: UnitMgr!')
            unitMgr.onUnitJoined += self.__unitMgrOnUnitJoined
            unitMgr.onUnitLeft += self.__unitMgrOnUnitLeft
        self.startGlobalListening()
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__hangarSpace.onSpaceCreate += self.__onHangarSpaceCreate
        self.__hangarSpace.onSpaceDestroy += self.hsSpaceDestroy
        self.__eventProgression.onUpdated += self.__onEventProgressionUpdated
        g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__platoonTankLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__platoonTankDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__onChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

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
            return

    def __onHangarSpaceCreate(self):
        self.__currentlyDisplayedTanks = 0
        if self.isInPlatoon() and self.__getNotReadyPlayersCount() < self.__getPlayerCount() - 1:
            self.__updatePlatoonTankInfo()
            cameraManager = self.__hangarSpace.space.getCameraManager()
            cameraManager.setPlatoonStartingCameraPosition()

    def __stopListening(self):
        _logger.debug('PlatoonController: stop listening')
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__unitMgrOnUnitJoined
            unitMgr.onUnitLeft -= self.__unitMgrOnUnitLeft
        self.stopGlobalListening()
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreate
        self.__hangarSpace.onSpaceDestroy -= self.hsSpaceDestroy
        self.__eventProgression.onUpdated -= self.__onEventProgressionUpdated
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
        self.__tankDisplayPosition.clear()
        if self.hasDelayedCallback(self.destroyUI):
            self.stopCallback(self.destroyUI)
        if self.__startAutoSearchOnUnitJoin:
            self.startSearch()
        else:
            self.__onUnitPlayersListChanged()
        self.__updatePlatoonTankInfo()

    def __unitMgrOnUnitLeft(self, unitMgrID, isFinishedAssembling):
        _logger.debug('PlatoonController: __unitMgrOnUnitLeft')
        if isFinishedAssembling:
            self.delayCallback(0.5, self.destroyUI)
        else:
            self.destroyUI()
        self.__tankDisplayPosition.clear()
        self.__isActiveSearchView = False

    def __calculateDropdownMove(self, xOffset):
        if xOffset is not None:
            x = xOffset - self.DROPDOWN_HALF_WIDTH
            return Position(x, self.DROPDOWN_Y_OFFSET)
        else:
            return

    def __addPlayerNotification(self, key, pInfo):
        if self.getChannelController() and not pInfo.isCurrentPlayer():
            self.__channelCtrl.addMessage(messages.getUnitPlayerNotification(key, pInfo))

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
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
             'setIdle': True,
             'setParallax': False}), EVENT_BUS_SCOPE.LOBBY)
            cameraManager = self.__hangarSpace.space.getCameraManager()
            cameraManager.setPlatoonCameraDistance(enable=True)

    def __platoonTankDestroyed(self, event):
        self.__currentlyDisplayedTanks = max(0, self.__currentlyDisplayedTanks - 1)
        if self.__currentlyDisplayedTanks <= 0:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
             'setIdle': True,
             'setParallax': False}), EVENT_BUS_SCOPE.LOBBY)
            cameraManager = self.__hangarSpace.space.getCameraManager()
            cameraManager.setPlatoonCameraDistance(enable=False)

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
            isInPlatoon = self.prbDispatcher.getFunctionalState().isInUnit()
            self.onPlatoonTankVisualizationChanged(self.__isPlatoonVisualizationEnabled and isInPlatoon)
            self.__updatePlatoonTankInfo()
            if displayPlatoonMembers and self.__checkForSettingsModification():
                filters = self.__getFilters()
                filters[GuiSettingsBehavior.DISPLAY_PLATOON_MEMBER_CLICKED] = True
                self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)
            return

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
                    displaySlotIndex = self.__tankDisplayPosition[player.accID]
                    result[displaySlotIndex] = tankInfo
                    isPlayerOnSlotAvailable[displaySlotIndex] = True

            for displaySlotIndex, isAvailable in isPlayerOnSlotAvailable.iteritems():
                if not isAvailable:
                    result[displaySlotIndex] = None

            self.onPlatoonTankUpdated(result)
            return

    def __hasEnoughSlots(self, slots):
        return len(self.__availablePlatoonTanks) + 1 >= slots

    def __updateDisplaySlotsIndices(self):
        players = self.prbEntity.getPlayers()
        playerIds = [ player.accID for player in players.values() ]
        if not self.__tankDisplayPosition:
            nextDisplayIndex = 0
            if self.prbEntity.getRosterSettings().getMaxSlots() == 3:
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
        freeDisplayIndices = []
        for playerId, displayIndex in self.__tankDisplayPosition.items():
            if playerId in playerIds:
                playerIds.remove(playerId)
                continue
            freeDisplayIndices.append(displayIndex)
            self.__tankDisplayPosition.pop(playerId)

        availableSlotIndex = 0
        for newPlayerId in playerIds:
            while availableSlotIndex in self.__tankDisplayPosition.values():
                availableSlotIndex += 1

            self.__tankDisplayPosition[newPlayerId] = availableSlotIndex

    def __onEventProgressionUpdated(self, _):
        entityType = self.getPrbEntityType()
        if entityType == PREBATTLE_TYPE.EPIC and not self.__eventProgression.isFrontLine or entityType == PREBATTLE_TYPE.EPIC and not self.__eventProgression.modeIsAvailable():
            self.leavePlatoon()
