# Embedded file name: scripts/client/gui/prb_control/functional/unit.py
import cgi
import time
import BigWorld
from CurrentVehicle import g_currentVehicle
from UnitBase import UNIT_SLOT, INV_ID_CLEAR_VEHICLE, UNIT_ROLE, UNIT_ERROR
from UnitBase import SORTIE_DIVISION
import account_helpers
from gui.prb_control.functional import action_handlers
from gui.prb_control.restrictions import createUnitActionValidator
from gui.prb_control.restrictions.permissions import IntroUnitPermissions
from gui.shared.fortifications import getClientFortMgr
from messenger.ext import passCensor
from account_helpers.AccountSettings import AccountSettings
from adisp import process
from constants import PREBATTLE_TYPE, REQUEST_COOLDOWN, FALLOUT_BATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_CURRENT_EXCEPTION
from gui.clubs import contexts as clubs_ctx
from gui.clubs.club_helpers import ClubListener
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters, settings
from gui.prb_control.context import unit_ctx
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.functional import interfaces
from gui.prb_control.functional import unit_ext
from gui.prb_control.items import unit_items, SelectResult
from gui.prb_control.prb_cooldown import UnitCooldownManager
from gui.prb_control.restrictions import permissions
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.utils.ListenersCollection import ListenersCollection
from helpers import time_utils
from items import vehicles as core_vehicles
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items.unit_items import DynamicRosterSettings

class UnitIntro(interfaces.IPrbEntry):

    def __init__(self, prbType):
        super(UnitIntro, self).__init__()
        self._prbType = prbType

    def makeDefCtx(self):
        return unit_ctx.JoinModeCtx(self._prbType)

    def create(self, ctx, callback = None):
        raise Exception('UnitIntro is not create entity')

    def join(self, ctx, callback = None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            g_prbCtrlEvents.onUnitIntroModeJoined(ctx.getEntityType(), ctx.getFlags())
            if callback is not None:
                callback(True)
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return

    def select(self, ctx, callback = None):
        self.join(ctx, callback=callback)


class UnitEntry(interfaces.IPrbEntry):

    def __init__(self, accountsToInvite = None):
        super(UnitEntry, self).__init__()
        self._accountsToInvite = accountsToInvite or ()

    def create(self, ctx, callback = None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            unitMgr = prb_getters.getClientUnitMgr()
            if unitMgr:
                ctx.startProcessing(callback=callback)
                self._doCreate(unitMgr, ctx)
            else:
                LOG_ERROR('Unit manager is not defined')
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return

    def join(self, ctx, callback = None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            unitMgr = prb_getters.getClientUnitMgr()
            if unitMgr:
                ctx.startProcessing(callback=callback)
                unitMgr.join(ctx.getID(), slotIdx=ctx.getSlotIdx())
            else:
                LOG_ERROR('Unit manager is not defined')
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return

    def select(self, ctx, callback = None):
        LOG_ERROR('Routine "select" can not be invoked for UnitEntry')

    def _doCreate(self, unitMgr, ctx):
        unitMgr.create()


class SquadEntry(UnitEntry):

    def __init__(self, accountsToInvite = None):
        super(SquadEntry, self).__init__(accountsToInvite=accountsToInvite)

    def makeDefCtx(self):
        return unit_ctx.SquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def join(self, ctx, callback = None):
        super(SquadEntry, self).join(ctx, callback)
        LOG_ERROR('Player can join to squad by invite only')
        if callback:
            callback(False)

    def select(self, ctx, callback = None):
        self.create(ctx, callback=callback)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquad()


class EventSquadEntry(UnitEntry):

    def __init__(self, battleType, accountsToInvite = None):
        super(EventSquadEntry, self).__init__(accountsToInvite=accountsToInvite)
        self.__battleType = battleType

    def makeDefCtx(self):
        return unit_ctx.SquadSettingsCtx(waitingID='prebattle/create', flags=FUNCTIONAL_FLAG.SWITCH, accountsToInvite=self._accountsToInvite)

    def select(self, ctx, callback = None):
        self.create(ctx, callback=callback)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad(self.__battleType)


class FortBattleEntry(interfaces.IPrbEntry):

    def __init__(self):
        super(FortBattleEntry, self).__init__()

    def create(self, ctx, callback = None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            fortMgr = getClientFortMgr()
            if fortMgr:
                ctx.startProcessing(callback=callback)
                fortMgr.createOrJoinFortBattle(ctx.getID(), slotIdx=ctx.getSlotIdx())
            else:
                LOG_ERROR('Fort provider is not defined')
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return

    def join(self, ctx, callback = None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            fortMgr = getClientFortMgr()
            if fortMgr:
                ctx.startProcessing(callback=callback)
                fortMgr.createOrJoinFortBattle(ctx.getID(), slotIdx=ctx.getSlotIdx())
            else:
                LOG_ERROR('Fort provider is not defined')
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return

    def select(self, ctx, callback = None):
        LOG_ERROR('Routine "select" can not be invoked for FortBattleEntry')


class ClubBattleEntry(interfaces.IPrbEntry, ClubListener):

    def create(self, ctx, callback = None):
        self.__createOrJoin(ctx, callback)

    def join(self, ctx, callback = None):
        self.__createOrJoin(ctx, callback)

    @process
    def __createOrJoin(self, ctx, callback = None):
        yield lambda callback: callback(None)
        if not prb_getters.hasModalEntity() or ctx.isForced():
            yield self.clubsCtrl.sendRequest(clubs_ctx.JoinUnitCtx(ctx.getClubDbID(), ctx.getJoiningTime()), allowDelay=ctx.isAllowDelay())
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return


class NoUnitFunctional(interfaces.IUnitFunctional):

    def getFunctionalFlags(self):
        return FUNCTIONAL_FLAG.NO_UNIT

    def exitFromQueue(self):
        return False


class _UnitFunctional(ListenersCollection, interfaces.IUnitFunctional):

    def __init__(self, requestHandlers, listenerClass, prbType, rosterSettings, flags = settings.FUNCTIONAL_FLAG.UNDEFINED):
        super(_UnitFunctional, self).__init__()
        self._flags = flags
        self._listReq = None
        self._setListenerClass(listenerClass)
        self._requestHandlers = requestHandlers
        self._rosterSettings = rosterSettings
        self._searchHandler = None
        self._prbType = prbType
        self._hasEntity = False
        self._showLeadershipNotification = False
        return

    def getFunctionalFlags(self):
        return self._flags

    def setFunctionalFlags(self, flags):
        self._flags = flags

    def showGUI(self, ctx = None):
        g_eventDispatcher.showUnitWindow(self._prbType)

    def setEntityType(self, prbType):
        self._prbType = prbType

    def getEntityType(self):
        return self._prbType

    def hasEntity(self):
        return self._hasEntity

    def getPlayerInfo(self, dbID = None, unitIdx = None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            pInfo = self._buildPlayerInfo(unitIdx, unit, dbID, unit.getPlayerSlotIdx(dbID), unit.getPlayer(dbID))
        else:
            pInfo = unit_items.PlayerUnitInfo(dbID, unitIdx, unit)
        return pInfo

    def getReadyStates(self, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        result = []
        if unit:
            isSlotClosed = unit.isSlotClosed
            isPlayerReady = unit.isPlayerReadyInSlot
            for slotIdx in self._rosterSettings.getAllSlotsRange():
                isClosed = isSlotClosed(slotIdx)
                result.append(isPlayerReady(slotIdx) if not isClosed else None)

        return result

    def getPermissions(self, dbID = None, unitIdx = None):
        pDbID = account_helpers.getAccountDatabaseID()
        if dbID is None:
            dbID = pDbID
        _, unit = self.getUnit(unitIdx=unitIdx, safe=True)
        if unit:
            isPlayerReady = False
            roles = 0
            players = unit.getPlayers()
            if dbID in players:
                roles |= players[dbID].get('role', roles)
                inSlots = unit.getPlayerSlots()
                if dbID in inSlots:
                    isPlayerReady = unit.isPlayerReadyInSlot(inSlots[dbID])
            if self.getEntityType() == PREBATTLE_TYPE.SQUAD:
                return permissions.SquadPermissions(roles, unit._flags, pDbID == dbID, isPlayerReady)
            else:
                return permissions.UnitPermissions(roles, unit._flags, pDbID == dbID, isPlayerReady)
        else:
            return IntroUnitPermissions()
        return

    def isCreator(self, dbID = None, unitIdx = None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        _, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            result = permissions.UnitPermissions.isCreator(unit.getPlayers().get(dbID, {}).get('role', 0))
        else:
            result = False
        return result

    def getRosterSettings(self):
        return self._rosterSettings

    def getSlotState(self, slotIdx, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            slotState = unit_items.SlotState(unit.isSlotClosed(slotIdx), unit.isSlotFree(slotIdx))
        else:
            slotState = unit_items.SlotState()
        return slotState

    def getPlayers(self, unitIdx = None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        result = {}
        if unit:
            slotGetter = unit.getPlayerSlotIdx
            players = unit.getPlayers()
            for dbID, data in players.iteritems():
                result[dbID] = self._buildPlayerInfo(unitIdx, unit, dbID, slotGetter(dbID), data)

        return result

    def getCandidates(self, unitIdx = None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        if not unit:
            return {}
        players = unit.getPlayers()
        memberIDs = set((value['accountDBID'] for value in unit.getMembers().itervalues()))
        dbIDs = set(players.keys()).difference(memberIDs)
        result = {}
        for dbID, data in players.iteritems():
            if dbID not in dbIDs:
                continue
            result[dbID] = unit_items.PlayerUnitInfo(dbID, unitIdx, unit, **data)

        return result

    def getRoster(self, unitIdx = None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            return unit.getRoster()
        else:
            return None

    def getVehicleInfo(self, dbID = None, unitIdx = None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        _, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            extra = unit.getExtra()
            if unit.isSquad() and extra.eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
                vehicles = extra.accountVehicles.get(dbID, ())
                vehInvIDs, vehCDs = (), ()
                if vehicles:
                    vehInvIDs, vehCDs = zip(*extra.accountVehicles.get(dbID, ()))
                result = unit_items.FalloutVehiclesInfo(vehInvIDs, vehCDs)
            else:
                vehicles = unit.getVehicles()
                if dbID in vehicles:
                    result = unit_items.VehicleInfo(**vehicles[dbID])
                else:
                    result = unit_items.VehicleInfo()
        else:
            result = unit_items.VehicleInfo()
        return result

    def getUnitFullData(self, unitIdx = None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        if not unit:
            return None
        else:
            dbID = account_helpers.getAccountDatabaseID()
            pInfo = self._buildPlayerInfo(unitIdx, unit, dbID, unit.getPlayerSlotIdx(dbID), unit.getPlayer(dbID))
            unitState = self._buildFlags(unit)
            unitStats = self._buildStats(unitIdx, unit)
            slotsIter = self.getSlotsIterator(unitIdx, unit)
            return (unit,
             unitState,
             unitStats,
             pInfo,
             slotsIter)

    def getFlags(self, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx, safe=True)
        if unit:
            unitFlags = self._buildFlags(unit)
        else:
            unitFlags = unit_items.UnitFlags(0)
        return unitFlags

    def getStats(self, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        if not unit:
            return unit_items.UnitStats(0, 0, 0, 0, 0, [], 0, 0)
        return self._buildStats(unitIdx, unit)

    def getComment(self, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            return unit.getComment()
        return ''

    def getCensoredComment(self, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            pInfo = self.getPlayerInfo(unitIdx=unitIdx)
            if not pInfo.isCreator():
                return passCensor(unit.getComment())
            else:
                return unit.getComment()
        return ''

    def getExtra(self, unitIdx = None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        if unit:
            return unit.getExtra()
        else:
            return None

    def request(self, ctx, callback = None):
        requestType = ctx.getRequestType()
        if requestType in self._requestHandlers:
            LOG_DEBUG('Unit request', ctx)
            self._requestHandlers[requestType](ctx, callback=callback)
        else:
            LOG_ERROR('Handler not found', ctx)
            if callback:
                callback(False)

    def getSelectedVehicles(self, section, useAll = True):
        accSettings = dict(AccountSettings.getSettings('unitWindow'))
        vehicles = accSettings.get(section, [])
        if vehicles or not useAll:
            selectedVehicles = []
            for vehCD in vehicles:
                vehicle = g_itemsCache.items.getItemByCD(int(vehCD))
                if vehicle.isInInventory:
                    selectedVehicles.append(int(vehCD))

        else:
            criteria = REQ_CRITERIA.INVENTORY
            selectedVehicles = [ k for k, v in g_itemsCache.items.getVehicles(criteria).iteritems() if v.level in self._rosterSettings.getLevelsRange() ]
        return selectedVehicles

    def setSelectedVehicles(self, section, vehicles):
        settings = dict(AccountSettings.getSettings('unitWindow'))
        settings[section] = vehicles
        AccountSettings.setSettings('unitWindow', settings)

    def getShowLeadershipNotification(self):
        return self._showLeadershipNotification

    def doLeadershipNotificationShown(self):
        self._showLeadershipNotification = False

    def _buildPlayerInfo(self, unitIdx, unit, dbID, slotIdx = -1, data = None):
        if data is None:
            data = {}
        if slotIdx != -1:
            isReady = unit.isPlayerReadyInSlot(slotIdx)
            isInSlot = True
        else:
            isReady = False
            isInSlot = False
        return unit_items.PlayerUnitInfo(dbID, unitIdx, unit, isReady=isReady, isInSlot=isInSlot, slotIdx=slotIdx, **data)

    def _buildFlags(self, unit):
        return unit_items.UnitFlags(unit.getFlags(), isReady=unit.arePlayersReady(ignored=[settings.CREATOR_SLOT_INDEX]))

    def _buildStats(self, unitIdx, unit):
        readyCount = 0
        occupiedSlotsCount = 0
        openedSlotsCount = 0
        curTotalLevel = unit.getPointsSum()
        freeSlotsCount = 0
        isReadyInSlot = unit.isPlayerReadyInSlot
        isSlotFree = unit.isSlotFree
        isSlotClosed = unit.isSlotClosed
        isCreator = self.isCreator(unitIdx=unitIdx)
        for slotIdx in self._rosterSettings.getAllSlotsRange():
            if isCreator and slotIdx == settings.CREATOR_SLOT_INDEX:
                readyCount += 1
            elif isReadyInSlot(slotIdx):
                readyCount += 1
            if not isSlotClosed(slotIdx):
                if not isSlotFree(slotIdx):
                    occupiedSlotsCount += 1
                else:
                    freeSlotsCount += 1
                openedSlotsCount += 1
            else:
                curTotalLevel += 1

        levelsSeq = map(lambda vehicle: vehicle.get('vehLevel', 0), unit.getVehicles().itervalues())
        levelsSeq.sort()
        return unit_items.UnitStats(readyCount, occupiedSlotsCount, openedSlotsCount, freeSlotsCount, curTotalLevel, levelsSeq, self._rosterSettings.getMinTotalLevel(), self._rosterSettings.getMaxTotalLevel())

    def getSlotsIterator(self, unitIdx, unit):
        players = unit.getPlayers()
        members = unit.getMembers()
        vehicles = unit.getVehicles()
        isPlayerReady = unit.isPlayerReadyInSlot
        isSlotClosed = unit.isSlotClosed
        isSlotFree = unit.isSlotFree
        isSlotDisabled = unit.isSlotDisabled
        for slotIdx in self._rosterSettings.getAllSlotsRange():
            if isSlotDisabled(slotIdx):
                continue
            state = unit_items.SlotState(isSlotClosed(slotIdx), isSlotFree(slotIdx))
            player = None
            vehicle = None
            if not state.isFree and slotIdx in members:
                dbID = members[slotIdx].get('accountDBID', -1L)
                if dbID in players:
                    player = unit_items.PlayerUnitInfo(dbID, unitIdx, unit, isReady=isPlayerReady(slotIdx), isInSlot=True, slotIdx=slotIdx, **players[dbID])
                if dbID in vehicles:
                    vehicle = vehicles.get(dbID)
            yield unit_items.SlotInfo(slotIdx, state, player, vehicle)

        return

    def isParentControlActivated(self, callback = None):
        result = False
        if prb_getters.isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback:
                callback(False)
            result = True
        return result


class IntroFunctional(_UnitFunctional):

    def __init__(self, prbType, flags, rosterSettings):
        RQ_TYPE = settings.REQUEST_TYPE
        handlers = {RQ_TYPE.AUTO_SEARCH: self.doAutoSearch,
         RQ_TYPE.ACCEPT_SEARCH: self.acceptSearch,
         RQ_TYPE.DECLINE_SEARCH: self.declineSearch}
        super(IntroFunctional, self).__init__(handlers, interfaces.IIntroUnitListener, prbType, rosterSettings, flags | FUNCTIONAL_FLAG.UNIT_INTRO)
        self._clubsPaginator = None
        self._clubsFinder = None
        return

    def init(self, ctx = None):
        self._hasEntity = True
        self._searchHandler = unit_ext.UnitAutoSearchHandler(self)
        self._searchHandler.init()
        if g_currentVehicle.isPresent():
            selectedVehs = [g_currentVehicle.item.intCD]
        else:
            selectedVehs = []
        self.setSelectedVehicles('selectedIntroVehicles', selectedVehs)
        from gui.clubs.ClubsController import g_clubsCtrl
        from gui.clubs.club_helpers import ClubListPaginator, ClubFinder
        self._clubsPaginator = ClubListPaginator(g_clubsCtrl)
        self._clubsPaginator.init()
        self._clubsFinder = ClubFinder(g_clubsCtrl)
        self._clubsFinder.init()
        g_eventDispatcher.loadUnit(self._prbType, self._flags & FUNCTIONAL_FLAG.ACTIONS_BITMASK)
        for listener in self._listeners:
            listener.onIntroUnitFunctionalInited()

        g_eventDispatcher.updateUI()
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def fini(self, woEvents = False):
        if self._searchHandler is not None:
            self._searchHandler.fini()
            self._searchHandler = None
        if self._clubsPaginator is not None:
            self._clubsPaginator.fini()
            self._clubsPaginator = None
        if self._clubsFinder is not None:
            self._clubsFinder.fini()
            self._clubsFinder = None
        self._requestHandlers.clear()
        self._hasEntity = False
        for listener in self._listeners:
            listener.onIntroUnitFunctionalFinished()

        if self._flags & FUNCTIONAL_FLAG.SWITCH == 0:
            g_eventDispatcher.unloadUnit(self._prbType)
            g_eventDispatcher.updateUI()
        unit_ext.destroyListReq()
        return FUNCTIONAL_FLAG.UNDEFINED

    def canPlayerDoAction(self):
        return (not self._hasEntity, '')

    def getExtra(self, unitIdx = None):
        return None

    def getUnit(self, unitIdx = None, safe = False):
        if unitIdx is None and not safe:
            LOG_ERROR('Unit index is not defined')
            return (None, None)
        else:
            return unit_ext.getUnitFromStorage(self._prbType, unitIdx)

    def getConfirmDialogMeta(self, ctx):
        return rally_dialog_meta.createUnitIntroLeaveMeta(ctx, self._prbType)

    def isPlayerJoined(self, ctx):
        result = False
        if isinstance(ctx, unit_ctx.JoinModeCtx):
            result = ctx.getEntityType() == self._prbType
        return result

    def showGUI(self, ctx = None):
        if ctx is not None:
            flags = ctx.getFlags() & FUNCTIONAL_FLAG.ACTIONS_BITMASK
        else:
            flags = FUNCTIONAL_FLAG.UNDEFINED
        g_eventDispatcher.showUnitWindow(self._prbType, flags)
        return

    def initEvents(self, listener):
        if listener in self._listeners:
            if self._searchHandler:
                self._searchHandler.initEvents(listener)
        else:
            LOG_ERROR('Listener not found', listener)

    def reset(self):
        if self._searchHandler and self._searchHandler.isInSearch():
            self._searchHandler.stop()

    def leave(self, ctx, callback = None):
        g_prbCtrlEvents.onUnitIntroModeLeft()
        if callback:
            callback(True)

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.FORT and self._prbType in [PREBATTLE_TYPE.SORTIE, PREBATTLE_TYPE.FORT_BATTLE]:
            g_eventDispatcher.showUnitWindow(self._prbType)
            result = True
        if action.actionName == PREBATTLE_ACTION_NAME.UNIT and self._prbType in [PREBATTLE_TYPE.CLUBS]:
            g_eventDispatcher.showUnitWindow(self._prbType)
            result = True
        return SelectResult(result)

    def doAutoSearch(self, ctx, callback = None):
        if ctx.isRequestToStart():
            if self.isParentControlActivated(callback=callback):
                return
            result = self._searchHandler.start(ctx.getVehTypes())
        else:
            result = self._searchHandler.stop()
        if callback:
            callback(result)

    def acceptSearch(self, _, callback = None):
        result = self._searchHandler.accept()
        if callback:
            callback(result)

    def declineSearch(self, _, callback = None):
        result = self._searchHandler.decline()
        if callback:
            callback(result)

    def getClubsPaginator(self):
        return self._clubsPaginator

    def getClubsFinder(self, pattern = ''):
        if self._clubsFinder is not None:
            self._clubsFinder.setPattern(pattern)
        return self._clubsFinder


class UnitFunctional(_UnitFunctional):

    def __init__(self, prbType, rosterSettings, flags = FUNCTIONAL_FLAG.UNIT):
        RQ_TYPE = settings.REQUEST_TYPE
        handlers = {RQ_TYPE.ASSIGN: self.assign,
         RQ_TYPE.LOCK: self.lock,
         RQ_TYPE.CHANGE_OPENED: self.changeOpened,
         RQ_TYPE.CHANGE_COMMENT: self.changeComment,
         RQ_TYPE.SET_VEHICLE: self.setVehicle,
         RQ_TYPE.SET_PLAYER_STATE: self.setPlayerReady,
         RQ_TYPE.SET_ROSTERS_SLOTS: self.setRostersSlots,
         RQ_TYPE.CLOSE_SLOT: self.closeSlot,
         RQ_TYPE.SEND_INVITE: self.invite,
         RQ_TYPE.KICK: self.kick,
         RQ_TYPE.AUTO_SEARCH: self.doAutoSearch,
         RQ_TYPE.BATTLE_QUEUE: self.doBattleQueue,
         RQ_TYPE.GIVE_LEADERSHIP: self.giveLeadership,
         RQ_TYPE.CHANGE_RATED: self.changeRated,
         RQ_TYPE.CHANGE_DIVISION: self.changeDivision,
         RQ_TYPE.SET_ES_VEHICLE_LIST: self.setEventSquadVehicleList,
         RQ_TYPE.SET_ES_PLAYER_STATE: self.setEventSquadReady,
         RQ_TYPE.CHANGE_ES_TYPE: self.changeEventSquadType}
        if prbType == PREBATTLE_TYPE.SQUAD:
            self._actionHandler = action_handlers.SquadActionsHandler(self)
        else:
            self._actionHandler = action_handlers.CommonUnitActionsHandler(self)
        super(UnitFunctional, self).__init__(handlers, interfaces.IUnitListener, prbType, rosterSettings, flags & FUNCTIONAL_FLAG.UNIT_BITMASK)
        self._requestsProcessor = None
        self._vehiclesWatcher = None
        self._lastErrorCode = UNIT_ERROR.OK
        self._cooldown = UnitCooldownManager()
        self._actionValidator = createUnitActionValidator(prbType, rosterSettings, self)
        self._deferredReset = False
        self._scheduler = unit_ext.createUnitScheduler(self)
        return

    def canPlayerDoAction(self):
        return self._actionValidator.canDoAction(self)

    def init(self, ctx = None):
        self._hasEntity = True
        flags = self.getFlags()
        self._requestsProcessor = unit_ext.UnitRequestProcessor(self)
        self._requestsProcessor.init()
        initResult = self._actionHandler.executeInit(ctx)
        self._vehiclesWatcher = unit_ext.InventoryVehiclesWatcher(self)
        self._vehiclesWatcher.init()
        self._addClientUnitListeners()
        idle = flags.isInIdle()
        if idle:
            timeLeftInIdle = self._getTimeLeftInIdle()
        else:
            timeLeftInIdle = 0
        for listener in self._listeners:
            listener.onUnitFunctionalInited()
            if idle:
                listener.onUnitFlagsChanged(flags, timeLeftInIdle)

        unit_ext.destroyListReq()
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.updateUI()
        self._scheduler.init()
        return initResult | FUNCTIONAL_FLAG.LOAD_WINDOW

    def fini(self, woEvents = False):
        flags = self.getFlags()
        pInfo = self.getPlayerInfo()
        self._scheduler.fini()
        self._requestHandlers.clear()
        self._hasEntity = False
        if not woEvents:
            try:
                for listener in self._listeners:
                    listener.onUnitFunctionalFinished()

            except:
                LOG_CURRENT_EXCEPTION()

        if self._requestsProcessor:
            self._requestsProcessor.fini()
            self._requestsProcessor = None
        if self._vehiclesWatcher:
            self._vehiclesWatcher.fini()
            self._vehiclesWatcher = None
        if self._actionHandler is not None:
            self._actionHandler.clear()
            self._actionHandler = None
        self._removeClientUnitListeners()
        if self._flags & FUNCTIONAL_FLAG.SWITCH > 0:
            g_eventDispatcher.requestToDestroyPrbChannel(PREBATTLE_TYPE.UNIT)
            return
        else:
            if not woEvents:
                if flags.isInPreArena() and pInfo.isInSlot:
                    g_eventDispatcher.unloadPreArenaUnit()
                else:
                    g_eventDispatcher.unloadUnit(self._prbType)
            else:
                if not (flags.isInPreArena() and pInfo.isInSlot):
                    g_eventDispatcher.removeUnitFromCarousel(self._prbType)
                g_eventDispatcher.requestToDestroyPrbChannel(PREBATTLE_TYPE.UNIT)
            g_eventDispatcher.updateUI()
            self._deferredReset = False
            return FUNCTIONAL_FLAG.UNDEFINED

    def addListener(self, listener):
        super(UnitFunctional, self).addListener(listener)
        flags = self.getFlags()
        idle = flags.isInIdle()
        if idle:

            def doNotify():
                listener.onUnitFlagsChanged(flags, self._getTimeLeftInIdle())

            BigWorld.callback(0.0, doNotify)

    def rejoin(self):
        self._addClientUnitListeners()
        LOG_DEBUG('onUnitRejoin')
        for listener in self._listeners:
            listener.onUnitRejoin()

    def initEvents(self, listener):
        flags = self.getFlags()
        idle = flags.isInIdle()
        if idle:
            g_eventDispatcher.setUnitProgressInCarousel(self._prbType, True)
        if listener in self._listeners:
            if idle:
                listener.onUnitFlagsChanged(flags, self._getTimeLeftInIdle())
        else:
            LOG_ERROR('Listener not found', listener)

    def isPlayerJoined(self, ctx):
        result = ctx.getCtrlType() is settings.CTRL_ENTITY_TYPE.UNIT and ctx.getID() == self.getID()
        if result and hasattr(ctx, 'getEntityType'):
            result = ctx.getEntityType() == self._prbType
        return result

    def setLastError(self, errorCode):
        self._lastErrorCode = errorCode

    def canSwitchToIntro(self):
        _, unit = self.getUnit()
        result = True
        if unit.isSortie():
            result = not self.getPlayerInfo().isLegionary()
        elif unit.isSquad():
            result = False
        return result

    def isKicked(self):
        return self._lastErrorCode in (UNIT_ERROR.KICKED_CANDIDATE, UNIT_ERROR.KICKED_PLAYER, UNIT_ERROR.CLAN_CHANGED)

    def getConfirmDialogMeta(self, ctx):
        if self.hasLockedState():
            meta = rally_dialog_meta.RallyLeaveDisabledDialogMeta(CTRL_ENTITY_TYPE.UNIT, self._prbType)
        else:
            meta = rally_dialog_meta.createUnitLeaveMeta(ctx, self._prbType)
        return meta

    def getID(self):
        return prb_getters.getUnitMgrID()

    def getUnitIdx(self):
        return prb_getters.getUnitIdx()

    def getUnit(self, unitIdx = None, safe = False):
        if unitIdx is None:
            unitIdx = self.getUnitIdx()
        return (unitIdx, prb_getters.getUnit(unitIdx, safe=True))

    def hasLockedState(self):
        pInfo = self.getPlayerInfo()
        flags = self.getFlags()
        return pInfo.isInSlot and (flags.isInSearch() or flags.isInQueue() or flags.isInPreArena() or flags.isInArena() and pInfo.isInArena())

    def isVehicleReadyToBattle(self):
        valid, restriction = self._actionValidator.validateVehicles(self.getVehicleInfo(), self.getFlags())
        return valid

    def validateLevels(self, stats = None, flags = None, vInfo = None, pInfo = None, slots = None):
        stats = stats or self.getStats()
        flags = flags or self.getFlags()
        vInfo = vInfo or self.getVehicleInfo()
        pInfo = pInfo or self.getPlayerInfo()
        slots = slots or self.getSlotsIterator(*self.getUnit())
        return (self._actionValidator.canCreatorDoAction(pInfo, stats, flags, vInfo, slots)[0], self._actionValidator.getRestrictionByLevel(stats, flags))

    def getUnitInvalidLevels(self, stats = None):
        return self._actionValidator.getUnitInvalidLevels(stats or self.getStats())

    def leave(self, ctx, callback = None):
        ctx.startProcessing(callback)
        unitMgr = prb_getters.getClientUnitMgr()
        unitMgr.leave()

    def assign(self, ctx, callback = None):
        slotIdx = ctx.getSlotIdx()
        dbID = ctx.getPlayerID()
        pInfo = self.getPlayerInfo(dbID=dbID)
        if pInfo.dbID == -1:
            LOG_ERROR('Player is not in unit', ctx)
            if callback:
                callback(False)
            return
        if slotIdx == UNIT_SLOT.REMOVE:
            self._unassign(ctx, callback=callback)
        elif slotIdx == UNIT_SLOT.ANY:
            if pInfo.isInSlot:
                LOG_DEBUG('Player already assigned to slot', ctx)
                if callback:
                    callback(True)
                return
            self._assign(ctx, callback=callback)
        else:
            if slotIdx not in self._rosterSettings.getAllSlotsRange():
                LOG_ERROR('Index of slot is invalid', ctx)
                if callback:
                    callback(False)
                return
            if pInfo.isInSlot or not self.getSlotState(slotIdx).isFree:
                if pInfo.slotIdx == slotIdx:
                    LOG_DEBUG('Player already assigned to slot', ctx)
                    if callback:
                        callback(True)
                    return
                self._reassign(ctx, callback=callback)
            else:
                self._assign(ctx, callback=callback)

    def invite(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        if not pPermissions.canSendInvite():
            LOG_ERROR('Player can not send invites', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'invite', ctx.getDatabaseIDs(), ctx.getComment())
        self._cooldown.process(settings.REQUEST_TYPE.SEND_INVITE, coolDown=REQUEST_COOLDOWN.PREBATTLE_INVITES)

    def kick(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        if not pPermissions.canKick():
            LOG_ERROR('Player can not can another players', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'kick', ctx.getPlayerID())

    def setVehicle(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        if not pPermissions.canSetVehicle():
            LOG_ERROR('Player can not set vehicle', pPermissions)
            if callback:
                callback(False)
            return
        if ctx.getVehTypeCD() or ctx.getVehInvID():
            self._setVehicle(ctx, callback=callback)
        else:
            self._clearVehicle(ctx, callback=callback)

    def setPlayerReady(self, ctx, callback = None):
        isReady = ctx.isReady()
        pInfo = self.getPlayerInfo()
        if isReady and self.isParentControlActivated(callback=callback):
            return
        if not pInfo.isInSlot:
            LOG_ERROR('Player is not in slot', ctx)
            if callback:
                callback(False)
            return
        if pInfo.isReady is isReady:
            LOG_DEBUG('Player already ready', ctx)
            if callback:
                callback(True)
            return
        if not self.isVehicleReadyToBattle():
            LOG_DEBUG('Vehicle is not ready to battle', ctx)
            if callback:
                callback(False)
            return
        if isReady:
            vehInfo = self.getVehicleInfo()
            g_currentVehicle.selectVehicle(vehInfo.vehInvID)
        if self._isInCoolDown(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canSetReady():
            LOG_ERROR('Player can not set ready state', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'setReady', isReady, ctx.resetVehicle)
        self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown())

    def closeSlot(self, ctx, callback = None):
        if self._isInCoolDown(settings.REQUEST_TYPE.CLOSE_SLOT, coolDown=ctx.getCooldown()):
            return
        slotIdx = ctx.getSlotIdx()
        rosterSettings = self.getRosterSettings()
        if slotIdx not in rosterSettings.getPlayersSlotsRange():
            LOG_ERROR('Index of slot is invalid', ctx)
            if callback:
                callback(False)
            return
        if not 1 << slotIdx & settings.UNIT_CLOSED_SLOTS_MASK:
            LOG_ERROR('Player can close given slot', ctx)
            if callback:
                callback(False)
            return
        isClosed = ctx.isClosed()
        slotState = self.getSlotState(slotIdx)
        if isClosed:
            if slotState.isClosed:
                LOG_DEBUG('Slot already is closed', ctx)
                if callback:
                    callback(True)
                return
            if not slotState.isFree:
                LOG_ERROR('Player can close a free slot', ctx)
                if callback:
                    callback(False)
                return
        elif not slotState.isClosed:
            LOG_DEBUG('Slot already is opened', ctx)
            if callback:
                callback(True)
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeClosedSlots():
            LOG_ERROR('Player can not change closed slots', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'closeSlot', slotIdx, isClosed, unitIdx=ctx.getUnitIdx())
        self._cooldown.process(settings.REQUEST_TYPE.CLOSE_SLOT, coolDown=ctx.getCooldown())

    def changeOpened(self, ctx, callback = None):
        isOpened = self.getFlags().isOpened()
        if isOpened is ctx.isOpened():
            LOG_DEBUG('Unit already is opened/closed', ctx)
            if callback:
                callback(True)
            return
        if self._isInCoolDown(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeUnitState():
            LOG_ERROR('Player can not change unit state', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'openUnit', isOpen=ctx.isOpened(), unitIdx=ctx.getUnitIdx())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def changeComment(self, ctx, callback = None):
        _, unit = self.getUnit()
        if not ctx.isCommentChanged(unit):
            if callback:
                callback(False)
            return
        if self._isInCoolDown(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeComment():
            LOG_ERROR('Player can not change comment', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'setComment', cgi.escape(ctx.getComment()), unitIdx=ctx.getUnitIdx())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def lock(self, ctx, callback = None):
        isLocked = self.getFlags().isLocked()
        if isLocked is ctx.isLocked():
            LOG_DEBUG('Unit already is locked/unlocked', ctx)
            if callback:
                callback(True)
            return
        if self._isInCoolDown(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeUnitState():
            LOG_ERROR('Player can not change unit state', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'lockUnit', isLocked=ctx.isLocked(), unitIdx=ctx.getUnitIdx())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def setRostersSlots(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change rosters', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'setAllRosterSlots', ctx.getRosterSlots(), unitIdx=ctx.getUnitIdx())

    def doAutoSearch(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        if not pPermissions.canInvokeAutoSearch():
            LOG_ERROR('Player can not start/stop auto search', pPermissions)
            if callback:
                callback(False)
            return
        _, unit = self.getUnit()
        flags = self.getFlags()
        if unit.isSortie():
            LOG_ERROR('Auto search is not enabled in sortie')
            if callback:
                callback(False)
            return
        if ctx.isRequestToStart():
            if self.isParentControlActivated(callback=callback):
                return
            if flags.isInSearch():
                LOG_DEBUG('Unit already started auto search')
                if callback:
                    callback(True)
                return
            if not self.isVehicleReadyToBattle():
                LOG_ERROR('Vehicle is not ready to battle', ctx)
                if callback:
                    callback(False)
                return
            vehInfo = self.getVehicleInfo()
            g_currentVehicle.selectVehicle(vehInfo.vehInvID)
            stats = self.getStats()
            if stats.curTotalLevel >= stats.maxTotalLevel:
                LOG_ERROR('Total level is invalid', stats)
                if callback:
                    callback(False)
                return
            self._requestsProcessor.doRequest(ctx, 'startAutoSearch')
        elif not flags.isInSearch():
            LOG_DEBUG('Unit did not start auto search')
            if callback:
                callback(True)
        else:
            self._requestsProcessor.doRequest(ctx, 'stopAutoSearch')

    def doBattleQueue(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        flags = self.getFlags()
        if ctx.isRequestToStart():
            if self.isParentControlActivated(callback=callback):
                return
            if not pPermissions.canStartBattleQueue():
                LOG_ERROR('Player can not start battle queue', pPermissions)
                if callback:
                    callback(False)
                return
            if flags.isInQueue():
                LOG_DEBUG('Unit already started battle queue')
                if callback:
                    callback(True)
                return
            stateAllowStartBattle = self._actionValidator.validateStateToStartBattle(flags)
            if not stateAllowStartBattle[0]:
                LOG_DEBUG(stateAllowStartBattle[1], ctx)
                if callback:
                    callback(False)
                return
            if not self.isVehicleReadyToBattle():
                LOG_ERROR('Vehicle is not ready to battle', ctx)
                if callback:
                    callback(False)
                return
            vehInfo = self.getVehicleInfo()
            g_currentVehicle.selectVehicle(vehInfo.vehInvID)
            stats = self.getStats()
            if stats.curTotalLevel > stats.maxTotalLevel:
                LOG_ERROR('Total level is invalid', stats)
                if callback:
                    callback(False)
                return
            self._requestsProcessor.doRequest(ctx, 'startBattle', vehInvID=ctx.selectVehInvID, gameplaysMask=ctx.getGamePlayMask())
        else:
            if not pPermissions.canStopBattleQueue():
                LOG_ERROR('Player can not stop battle queue', pPermissions)
                if callback:
                    callback(False)
                return
            if not flags.isInQueue():
                LOG_DEBUG('Unit did not start battle queue')
                if callback:
                    callback(True)
            else:
                self._requestsProcessor.doRequest(ctx, 'stopBattle')

    def reset(self):
        flags = self.getFlags()
        pInfo = self.getPlayerInfo()
        if pInfo.isCreator() and flags.isInSearch():
            self._requestsProcessor.doRawRequest('stopAutoSearch')
        elif pInfo.isReady:
            if not flags.isInIdle():
                if self.getEntityType() == PREBATTLE_TYPE.SQUAD and self.getExtra().eventType:
                    ctx = unit_ctx.SetReadyEventSquadCtx(False)
                    self.setEventSquadReady(ctx)
                else:
                    ctx = unit_ctx.SetReadyUnitCtx(False)
                    ctx.resetVehicle = True
                    self.setPlayerReady(ctx)
            else:
                self._deferredReset = True
        g_eventDispatcher.updateUI()

    def togglePlayerReadyAction(self, launchChain = False):
        notReady = not self.getPlayerInfo().isReady
        if notReady:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        if self.getEntityType() == PREBATTLE_TYPE.SQUAD and self.getExtra().eventType:
            ctx = unit_ctx.SetReadyEventSquadCtx(notReady, waitingID=waitingID)
            self.setEventSquadReady(ctx)
            return
        if launchChain:
            if notReady:
                selVehCtx = unit_ctx.SetVehicleUnitCtx(vTypeCD=g_currentVehicle.item.intCD, waitingID='prebattle/change_settings')
                selVehCtx.setReady = True
                self.setVehicle(selVehCtx)
            else:
                ctx = unit_ctx.SetReadyUnitCtx(False, 'prebattle/player_not_ready')
                ctx.resetVehicle = True
                LOG_DEBUG('Unit request', ctx)
                self.setPlayerReady(ctx)
        else:
            ctx = unit_ctx.SetReadyUnitCtx(notReady, waitingID)
            LOG_DEBUG('Unit request', ctx)
            self.setPlayerReady(ctx)

    def doSelectAction(self, action):
        result = False
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.FORT and self._prbType in (PREBATTLE_TYPE.SORTIE, PREBATTLE_TYPE.FORT_BATTLE):
            g_eventDispatcher.showUnitWindow(self._prbType)
            result = True
        if name == PREBATTLE_ACTION_NAME.UNIT and self._prbType in (PREBATTLE_TYPE.CLUBS,):
            g_eventDispatcher.showUnitWindow(self._prbType)
            result = True
        if name == PREBATTLE_ACTION_NAME.FALLOUT and self._prbType in (PREBATTLE_TYPE.SQUAD,):
            extra = self.getExtra()
            if extra is not None and extra.eventType:
                g_eventDispatcher.showFalloutWindow()
                result = True
        return SelectResult(result)

    def doAction(self, action = None):
        if super(UnitFunctional, self).doAction(action):
            return True
        self._actionHandler.execute(customData={'rosterSettings': self._rosterSettings})
        return True

    def giveLeadership(self, ctx, callback = None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeLeadership():
            LOG_ERROR('Player can not give leadership to player players', pPermissions)
            if callback:
                callback(False)
            return
        otherPPermissions = self.getPermissions(ctx.getPlayerID())
        if not otherPPermissions.canLead():
            LOG_ERROR('Player can not take leadership', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'giveLeadership', ctx.getPlayerID())

    def getCooldownTime(self, rqTypeID):
        return self._cooldown.getTime(rqTypeID)

    def changeRated(self, ctx, callback = None):
        extra = self.getExtra()
        if extra is None or not hasattr(extra, 'isRatedBattle'):
            LOG_DEBUG('Unit has no extra data or extra does not contain isRanked', ctx)
            if callback:
                callback(True)
            return
        else:
            isRated = extra.isRatedBattle
            if isRated is ctx.isRated():
                LOG_DEBUG('Unit already is rated/rated', ctx)
                if callback:
                    callback(True)
                return
            if self._isInCoolDown(settings.REQUEST_TYPE.CHANGE_RATED, coolDown=ctx.getCooldown()):
                return
            pPermissions = self.getPermissions()
            if not pPermissions.canChangeRated():
                LOG_ERROR('Player can not change rated', pPermissions)
                if callback:
                    callback(False)
                return
            self._requestsProcessor.doRequest(ctx, 'setRatedBattle', isRatedBattle=ctx.isRated(), unitIdx=ctx.getUnitIdx())
            self._cooldown.process(settings.REQUEST_TYPE.CHANGE_RATED, coolDown=ctx.getCooldown())
            return

    def changeDivision(self, ctx, callback = None):
        if ctx.getDivisionID() not in SORTIE_DIVISION._ORDER:
            LOG_ERROR('Incorrect value of division', ctx.getDivisionID())
            if callback:
                callback(False)
            return
        if self._isInCoolDown(settings.REQUEST_TYPE.CHANGE_DIVISION, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change division', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'changeSortieDivision', division=ctx.getDivisionID(), unitIdx=ctx.getUnitIdx())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_DIVISION, coolDown=ctx.getCooldown())

    def exitFromQueue(self):
        self._actionHandler.exitFromQueue()

    def setEventSquadVehicleList(self, ctx, callback = None):
        if self._isInCoolDown(settings.REQUEST_TYPE.SET_ES_VEHICLE_LIST, coolDown=ctx.getCooldown()):
            return
        else:
            pPermissions = self.getPermissions()
            if not pPermissions.canSetVehicle():
                LOG_ERROR('Player can not set vehicle', pPermissions)
                if callback:
                    callback(False)
                return
            vehsList = ctx.getVehsList()
            if vehsList:
                for vehInvID in vehsList:
                    if vehInvID != INV_ID_CLEAR_VEHICLE and g_itemsCache.items.getVehicle(vehInvID) is None:
                        LOG_ERROR('Vehicle is not in inventory', ctx)
                        if callback:
                            callback(False)
                        return

            self._requestsProcessor.doRequest(ctx, 'setEventSquadVehicleList', vehicleList=vehsList)
            self._cooldown.process(settings.REQUEST_TYPE.SET_ES_VEHICLE_LIST, coolDown=ctx.getCooldown())
            return

    def setEventSquadReady(self, ctx, callback = None):
        isReady = ctx.isReady()
        pInfo = self.getPlayerInfo()
        if isReady and self.isParentControlActivated(callback=callback):
            return
        if not pInfo.isInSlot:
            LOG_ERROR('Player is not in slot', ctx)
            if callback:
                callback(False)
            return
        if pInfo.isReady is isReady:
            LOG_DEBUG('Player already ready', ctx)
            if callback:
                callback(True)
            return
        if not self.isVehicleReadyToBattle():
            LOG_DEBUG('Vehicle is not ready to battle', ctx)
            if callback:
                callback(False)
            return
        if self._isInCoolDown(settings.REQUEST_TYPE.SET_ES_PLAYER_STATE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canSetReady():
            LOG_ERROR('Player can not set ready state', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'setEventSquadReady', isReady)
        self._cooldown.process(settings.REQUEST_TYPE.SET_ES_PLAYER_STATE, coolDown=ctx.getCooldown())

    def changeEventSquadType(self, ctx, callback = None):
        battleType = ctx.getBattleType()
        if battleType not in FALLOUT_BATTLE_TYPE.ALL:
            LOG_ERROR('Incorrect value of battle type', battleType)
            if callback:
                callback(False)
            return
        if self._isInCoolDown(settings.REQUEST_TYPE.CHANGE_ES_TYPE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change battle type', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'changeEventSquadType', newEventType=battleType)
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_ES_TYPE, coolDown=ctx.getCooldown())

    def unit_onUnitFlagsChanged(self, prevFlags, nextFlags):
        unitIdx, unit = self.getUnit()
        isReady = unit.arePlayersReady(ignored=[settings.CREATOR_SLOT_INDEX])
        flags = unit_items.UnitFlags(nextFlags, prevFlags, isReady)
        if flags.isInIdle():
            timeLeftInIdle = self._getTimeLeftInIdle()
            g_eventDispatcher.setUnitProgressInCarousel(self._prbType, True)
        else:
            timeLeftInIdle = 0
            g_eventDispatcher.setUnitProgressInCarousel(self._prbType, False)
        LOG_DEBUG('onUnitFlagsChanged', flags, timeLeftInIdle)
        if not flags.isInIdle() and self._deferredReset:
            self._deferredReset = False
            self.reset()
        for listener in self._listeners:
            listener.onUnitFlagsChanged(flags, timeLeftInIdle)

        if not flags.isOnlyRosterWaitChanged():
            self._actionHandler.setUnitChanged(flags)
        members = unit.getMembers()
        diff = []
        for slotIdx in self._rosterSettings.getAllSlotsRange():
            if prevFlags is not nextFlags:
                if slotIdx not in members:
                    continue
                dbID = members[slotIdx]['accountDBID']
                pInfo = self.getPlayerInfo(dbID=dbID, unitIdx=unitIdx)
                diff.append(pInfo)

        for listener in self._listeners:
            for pInfo in diff:
                listener.onUnitPlayerStateChanged(pInfo)

        g_eventDispatcher.updateUI()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        if vehTypeCD:
            _, nationID, itemID = core_vehicles.parseIntCompactDescr(vehTypeCD)
            vehLevel = core_vehicles.g_cache.vehicle(nationID, itemID).level
        else:
            vehLevel = 0
        vInfo = unit_items.VehicleInfo(vehInvID, vehTypeCD, vehLevel)
        LOG_DEBUG('onUnitVehicleChanged', dbID, vInfo)
        if dbID == account_helpers.getAccountDatabaseID() and not vInfo.isEmpty():
            vehicle = g_itemsCache.items.getItemByCD(vInfo.vehTypeCD)
            if vehicle is not None:
                g_currentVehicle.selectVehicle(vehicle.invID)
        for listener in self._listeners:
            listener.onUnitVehicleChanged(dbID, vInfo)

        g_eventDispatcher.updateUI()
        return

    def unit_onUnitReadyMaskChanged(self, prevMask, nextMask):
        unitIdx, unit = self.getUnit()
        isReadyInSlot = unit.isPlayerReadyInSlot
        members = unit.getMembers()
        players = unit.getPlayers()
        diff = []
        for slotIdx in self._rosterSettings.getAllSlotsRange():
            prevValue = isReadyInSlot(slotIdx, mask=prevMask)
            nextValue = isReadyInSlot(slotIdx, mask=nextMask)
            if prevValue is not nextValue:
                if slotIdx not in members:
                    continue
                dbID = members[slotIdx]['accountDBID']
                data = players.get(dbID, {})
                pInfo = unit_items.PlayerUnitInfo(dbID, unitIdx, unit, isReady=nextValue, isInSlot=True, slotIdx=slotIdx, **data)
                diff.append(pInfo)

        LOG_DEBUG('onUnitPlayerStateChanged', diff)
        for listener in self._listeners:
            for pInfo in diff:
                listener.onUnitPlayerStateChanged(pInfo)

        self._actionHandler.setUsersChanged()
        g_eventDispatcher.updateUI()

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        pInfo = self.getPlayerInfo(dbID=playerID)
        pPermissions = self.getPermissions(dbID=playerID)
        diff = prevRoleFlags ^ nextRoleFlags
        isOnlineChanged = diff & UNIT_ROLE.OFFLINE > 0
        isCreatorChanged = diff & UNIT_ROLE.CREATOR > 0
        inArenaChanged = diff & UNIT_ROLE.IN_ARENA > 0
        LOG_DEBUG('onUnitPlayerRolesChanged', pInfo, pPermissions)
        for listener in self._listeners:
            if isOnlineChanged:
                listener.onUnitPlayerOnlineStatusChanged(pInfo)
            if isCreatorChanged:
                if pInfo.isCurrentPlayer():
                    self._showLeadershipNotification = True
                listener.onUnitPlayerBecomeCreator(pInfo)
            if inArenaChanged:
                listener.onUnitPlayerEnterOrLeaveArena(pInfo)
            listener.onUnitPlayerRolesChanged(pInfo, pPermissions)

        g_eventDispatcher.updateUI()

    def unit_onUnitPlayerAdded(self, playerID, playerData):
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, unit.getPlayerSlotIdx(playerID), playerData)
        self._invokeListeners('onUnitPlayerAdded', pInfo)

    def unit_onUnitPlayerInfoChanged(self, playerID, playerData):
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, unit.getPlayerSlotIdx(playerID), playerData)
        self._invokeListeners('onUnitPlayerInfoChanged', pInfo)
        self._actionHandler.setPlayerInfoChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, -1, playerData)
        self._invokeListeners('onUnitPlayerRemoved', pInfo)

    def unit_onUnitSettingChanged(self, opCode, value):
        self._invokeListeners('onUnitSettingChanged', opCode, value)

    def unit_onUnitRosterChanged(self):
        unitIdx, unit = self.getUnit()
        self._rosterSettings = DynamicRosterSettings(unit)
        self._actionValidator = createUnitActionValidator(self._prbType, self._rosterSettings, self)
        self._vehiclesWatcher.validate()
        self._invokeListeners('onUnitRosterChanged')

    def unit_onUnitMembersListChanged(self):
        self._invokeListeners('onUnitMembersListChanged')
        g_eventDispatcher.updateUI()

    def unit_onUnitPlayersListChanged(self):
        self._actionHandler.setUsersChanged()
        self._invokeListeners('onUnitPlayersListChanged')

    def unit_onUnitPlayerVehDictChanged(self, playerID):
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, unit.getPlayerSlotIdx(playerID), unit.getPlayer(playerID))
        self._invokeListeners('onUnitPlayerVehDictChanged', pInfo)

    def unit_onUnitExtraChanged(self, extras):
        self._invokeListeners('onUnitExtraChanged', extras)

    def _addClientUnitListeners(self):
        unit = prb_getters.getUnit(self.getUnitIdx())
        unit.onUnitFlagsChanged += self.unit_onUnitFlagsChanged
        unit.onUnitReadyMaskChanged += self.unit_onUnitReadyMaskChanged
        unit.onUnitVehicleChanged += self.unit_onUnitVehicleChanged
        unit.onUnitSettingChanged += self.unit_onUnitSettingChanged
        unit.onUnitPlayerRoleChanged += self.unit_onUnitPlayerRoleChanged
        unit.onUnitMembersListChanged += self.unit_onUnitMembersListChanged
        unit.onUnitPlayersListChanged += self.unit_onUnitPlayersListChanged
        unit.onUnitRosterChanged += self.unit_onUnitRosterChanged
        unit.onUnitPlayerVehDictChanged += self.unit_onUnitPlayerVehDictChanged
        unit.onUnitPlayerAdded += self.unit_onUnitPlayerAdded
        unit.onUnitPlayerRemoved += self.unit_onUnitPlayerRemoved
        unit.onUnitPlayerInfoChanged += self.unit_onUnitPlayerInfoChanged
        unit.onUnitExtraChanged += self.unit_onUnitExtraChanged

    def _removeClientUnitListeners(self):
        unit = prb_getters.getUnit(self.getUnitIdx(), safe=True)
        if unit:
            unit.onUnitFlagsChanged -= self.unit_onUnitFlagsChanged
            unit.onUnitReadyMaskChanged -= self.unit_onUnitReadyMaskChanged
            unit.onUnitVehicleChanged -= self.unit_onUnitVehicleChanged
            unit.onUnitSettingChanged -= self.unit_onUnitSettingChanged
            unit.onUnitPlayerRoleChanged -= self.unit_onUnitPlayerRoleChanged
            unit.onUnitMembersListChanged -= self.unit_onUnitMembersListChanged
            unit.onUnitPlayersListChanged -= self.unit_onUnitPlayersListChanged
            unit.onUnitRosterChanged -= self.unit_onUnitRosterChanged
            unit.onUnitPlayerVehDictChanged -= self.unit_onUnitPlayerVehDictChanged
            unit.onUnitPlayerAdded -= self.unit_onUnitPlayerAdded
            unit.onUnitPlayerRemoved -= self.unit_onUnitPlayerRemoved
            unit.onUnitPlayerInfoChanged -= self.unit_onUnitPlayerInfoChanged
            unit.onUnitExtraChanged -= self.unit_onUnitExtraChanged

    def _unassign(self, ctx, callback = None):
        slotIdx = ctx.getSlotIdx()
        dbID = ctx.getPlayerID()
        pPermissions = self.getPermissions()
        if not pPermissions.canAssignToSlot(dbID):
            LOG_ERROR('Player can not unassign from slot', pPermissions)
            if callback:
                callback(False)
            return
        if slotIdx == settings.CREATOR_SLOT_INDEX:
            LOG_ERROR('In first slot can be creator only')
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'unassign', dbID, self.getUnitIdx())

    def _assign(self, ctx, callback = None):
        slotIdx = ctx.getSlotIdx()
        dbID = ctx.getPlayerID()
        pPermissions = self.getPermissions()
        if not pPermissions.canAssignToSlot(dbID):
            LOG_ERROR('Player can not assign to slot', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'assign', dbID, slotIdx, unitIdx=ctx.getUnitIdx())

    def _reassign(self, ctx, callback = None):
        slotIdx = ctx.getSlotIdx()
        dbID = ctx.getPlayerID()
        unitIdx = self.getUnitIdx()
        pPermissions = self.getPermissions()
        if pPermissions.canReassignToSlot():
            self._requestsProcessor.doRequest(ctx, 'reassign', dbID, slotIdx, unitIdx)
        elif pPermissions.canAssignToSlot(dbID):
            self._requestsProcessor.doRequest(ctx, 'assign', dbID, slotIdx, unitIdx=unitIdx)
        else:
            LOG_ERROR('Player can not (re)assign to slot', pPermissions)
            if callback:
                callback(False)

    def _setVehicle(self, ctx, callback = None):
        vehTypeCD = ctx.getVehTypeCD()
        vehInvID = ctx.getVehInvID()
        invVehs = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        if vehInvID:
            invMap = invVehs.inventoryMap()
            if vehInvID not in invMap.keys():
                LOG_ERROR('Vehicle is not in inventory', ctx)
                if callback:
                    callback(False)
                return
        elif vehTypeCD:
            if vehTypeCD not in invVehs:
                LOG_ERROR('Vehicle is not in inventory', ctx)
                if callback:
                    callback(False)
                return
            vehicle = invVehs[vehTypeCD]
            vehInvID = vehicle.inventoryID
        else:
            LOG_ERROR('Context is invalid', ctx)
            if callback:
                callback(False)
            return
        vInfo = self.getVehicleInfo()
        if vInfo.vehInvID == vehInvID:
            LOG_DEBUG('Player already selected vehicle', ctx)
            if callback:
                callback(True)
            return
        setReadyAfterVehicleSelect = ctx.setReady
        self._requestsProcessor.doRequest(ctx, 'setVehicle', vehInvID=vehInvID, setReady=setReadyAfterVehicleSelect)
        if setReadyAfterVehicleSelect:
            self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown())

    def _clearVehicle(self, ctx, callback = None):
        vInfo = self.getVehicleInfo()
        if not vInfo.vehInvID:
            LOG_DEBUG('There is not vehicle in slot', ctx)
            if callback:
                callback(True)
            return
        self._requestsProcessor.doRequest(ctx, 'setVehicle', INV_ID_CLEAR_VEHICLE)

    def _getTimeLeftInIdle(self):
        _, unit = self.getUnit()
        result = 0
        if unit:
            timestamp = unit.getModalTimestamp()
            if timestamp:
                result = max(0, int(time.time() - time_utils.makeLocalServerTime(timestamp)))
        return result

    def _isInCoolDown(self, requestType, callback = None, coolDown = None):
        if self._cooldown.validate(requestType, coolDown):
            if callback:
                callback(False)
            return True
        return False
