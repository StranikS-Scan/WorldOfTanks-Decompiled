# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/entity.py
import cgi
import time
import BigWorld
import account_helpers
from ClientUnit import ClientUnit
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from UnitBase import SORTIE_DIVISION
from UnitBase import UNIT_SLOT, INV_ID_CLEAR_VEHICLE, UNIT_ROLE
from constants import PREBATTLE_TYPE, REQUEST_COOLDOWN
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters, settings
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.actions_validator import NotSupportedActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.entity import BasePrbEntity, BasePrbEntryPoint
from gui.prb_control.entities.base.unit.actions_handler import UnitActionsHandler
from gui.prb_control.entities.base.unit.actions_validator import UnitActionsValidator
from gui.prb_control.entities.base.unit.cooldown import UnitCooldownManager
from gui.prb_control.entities.base.unit.ctx import JoinUnitModeCtx, SetVehicleUnitCtx, SetVehiclesUnitCtx, SetReadyUnitCtx
from gui.prb_control.entities.base.unit.listener import IUnitListener, IUnitIntroListener
from gui.prb_control.entities.base.unit.permissions import IUnitPermissions, UnitIntroPermissions, UnitPermissions
from gui.prb_control.entities.base.unit.requester import UnitRequestProcessor
from gui.prb_control.entities.base.unit.scheduler import UnitScheduler
from gui.prb_control.entities.base.unit.vehicles_watcher import UnitVehiclesWatcher
from gui.prb_control.items import unit_items, ValidationResult
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.shared import g_itemsCache
from gui.shared.utils.listeners_collection import ListenersCollection
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import time_utils
from items import vehicles as core_vehicles
from messenger.ext import passCensor
from shared_utils import findFirst

class BaseUnitEntity(BasePrbEntity):
    """
    Base class for unit entity.
    """

    def init(self, ctx=None):
        """
        Initializes unit entity with init context.
        Args:
            ctx: init request context
        """
        return super(BaseUnitEntity, self).init()

    def fini(self, ctx=None, woEvents=False):
        """
        Finalizes unit entity with init context.
        Args:
            ctx: init request context
            woEvents: without any events flag
        """
        return super(BaseUnitEntity, self).fini()

    def getCtrlType(self):
        return CTRL_ENTITY_TYPE.UNIT

    def getPermissions(self, dbID=None, unitIdx=None):
        return IUnitPermissions()

    def initEvents(self, listener):
        """
        Initializes event listeners
        """
        pass

    def getUnitIdx(self):
        """
        Returns index of current unit.
        """
        pass

    def getUnit(self, unitIdx=None, safe=False):
        """
        Getter for unit data by unit index in unit manager.
        Args:
            unitIdx: unit index
            safe: should it be safe getter
        
        Returns:
            unit index and client unit object
        """
        return (0, None)

    def getExtra(self, unitIdx=None):
        """
        Getter for unit extra data by unit index in unit manager.
        Args:
            unitIdx: unit index
        """
        return None

    def getUnitFullData(self, unitIdx=None):
        """
        Gets unit full data that required to gui.
        Args:
            unitIdx: unit index
        """
        return unit_items.UnitFullData()

    def getRosterSettings(self):
        """
        Returns unit roster settings object.
        """
        return unit_items.UnitRosterSettings()

    def getPlayerInfo(self, dbID=None, unitIdx=None):
        """
        Getter for player's info object
        Args:
            dbID: player's database ID
            unitIdx: unit index in which player is
        """
        return unit_items.PlayerUnitInfo(-1L, 0, None)

    def getReadyStates(self, unitIdx=None):
        """
        Returns list of player's ready states by slots. None for no player.
        Args:
            unitIdx: unit index
        """
        return []

    def getSlotState(self, slotIdx, unitIdx=None):
        """
        Getter for slot state info
        Args:
            slotIdx: slot index
            unitIdx: unit index
        """
        return unit_items.SlotState()

    def getSlotsIterator(self, unitIdx, unit):
        """
        Returns slots iterator for given unit
        Args:
            unitIdx: unit index
            unit: client unit instance
        """
        return (unit_items.SlotInfo(-1, self.getSlotState(-1)),)

    def getPlayers(self, unitIdx=None):
        """
        Returns all players that are in unit.
        Args:
            unitIdx: unit index
        
        Returns:
            dictionary with players info to databases IDs mapping
        """
        return {}

    def getCandidates(self, unitIdx=None):
        """
        Returns all candidates to unit.
        Args:
            unitIdx: unit index
        
        Returns:
            dictionary with players info to databases IDs mapping
        """
        return {}

    def getRosterType(self, unitIdx=None):
        """
        Getter for unit roster type
        Args:
            unitIdx: unit index
        """
        return None

    def getRoster(self, unitIdx=None):
        """
        Getter for unit roster
        Args:
            unitIdx: unit index
        """
        return None

    def getVehiclesInfo(self, dbID=None, unitIdx=None):
        """
        Gets vehicles info for some player
        Args:
            dbID: player database ID
            unitIdx: unit index
        """
        return (unit_items.VehicleInfo(),)

    def invalidateSelectedVehicles(self, vehCDs):
        """
        Invalidates current player's selected vehicles
        Args:
            vehCDs: list of currently selected vehicle intCD's
        
        Returns:
            set vehicles request context
        """
        return None

    def getFlags(self, unitIdx=None):
        """
        Getter for unit flags
        Args:
            unitIdx: unit index
        """
        return unit_items.UnitFlags(0)

    def getStats(self, unitIdx=None):
        """
        Getter for unit stats
        Args:
            unitIdx: unit index
        """
        return unit_items.UnitStats()

    def getComment(self, unitIdx=None):
        """
        Returns unit's comments
        Args:
            unitIdx: unit index
        """
        pass

    def getCensoredComment(self, unitIdx=None):
        """
        Returns unit's censored comments
        Args:
            unitIdx: unit index
        """
        pass

    def getShowLeadershipNotification(self):
        """
        Returns should we show give leadership notification
        """
        return False

    def doLeadershipNotificationShown(self):
        """
        Routine should be called after leadership notification shown
        """
        pass

    def validateLevels(self):
        """
        Additional validation of unit levels selection
        """
        return ValidationResult()


class _UnitIntroEntryPoint(BasePrbEntryPoint):
    """
    Base class for unit intro entry point
    """

    def __init__(self, entityFlags, modeFlags, prbType):
        super(_UnitIntroEntryPoint, self).__init__(entityFlags=entityFlags, modeFlags=modeFlags)
        self._prbType = prbType

    def makeDefCtx(self):
        return JoinUnitModeCtx(self._prbType, flags=self.getFunctionalFlags())

    def create(self, ctx, callback=None):
        raise Exception('UnitIntro is not create entity')

    def join(self, ctx, callback=None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            g_prbCtrlEvents.onUnitIntroModeJoined(ctx.getEntityType(), ctx.getFlags())
            if callback is not None:
                callback(True)
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return

    def select(self, ctx, callback=None):
        self.join(ctx, callback)


class UnitIntroEntryPoint(_UnitIntroEntryPoint):
    """
    Class for unit intro entry point
    """

    def __init__(self, modeFlags, prbType):
        super(UnitIntroEntryPoint, self).__init__(FUNCTIONAL_FLAG.UNIT_INTRO, modeFlags, prbType)


class UnitBrowserEntryPoint(_UnitIntroEntryPoint):
    """
    Class for unit browser entry point
    """

    def __init__(self, modeFlags, prbType):
        super(UnitBrowserEntryPoint, self).__init__(FUNCTIONAL_FLAG.UNIT_BROWSER, modeFlags, prbType)


class UnitEntryPoint(BasePrbEntryPoint):
    """
    Class for unit entry point
    """

    def __init__(self, modeFlags, accountsToInvite=None):
        super(UnitEntryPoint, self).__init__(entityFlags=FUNCTIONAL_FLAG.UNIT, modeFlags=modeFlags)
        self._accountsToInvite = accountsToInvite or ()

    def create(self, ctx, callback=None):
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

    def join(self, ctx, callback=None):
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

    def select(self, ctx, callback=None):
        self.create(ctx, callback)

    def setAccountsToInvite(self, accountsToInvite):
        self._accountsToInvite = accountsToInvite

    def _doCreate(self, unitMgr, ctx):
        """
        Routine must be invoked to create entity at system level
        Args:
            unitMgr: unit manager object
            ctx: create request context
        """
        unitMgr.create()


class _UnitEntity(BaseUnitEntity, ListenersCollection):
    """
    Base class for unit entity
    """

    def __init__(self, entityFlags, modeFlags, requestHandlers, listenerClass, prbType):
        """
        Args:
            entityFlags: entity specific flags
            modeFlags: mode specific flags
            requestHandlers: dict of supported requests
            listenerClass: unit listener class
            prbType: prebattle type ID
        """
        super(_UnitEntity, self).__init__(entityFlags=entityFlags, modeFlags=modeFlags)
        self._prbType = prbType
        self._setListenerClass(listenerClass)
        self._requestHandlers = requestHandlers
        self._rosterSettings = self._createRosterSettings()
        self._searchHandler = None
        return

    def fini(self, ctx=None, woEvents=False):
        self.clear()
        return super(_UnitEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def showGUI(self, ctx=None):
        return super(_UnitEntity, self).showGUI(ctx)

    def getEntityType(self):
        return self._prbType

    def getRosterSettings(self):
        return self._rosterSettings

    def invalidateSelectedVehicles(self, vehInvCDs):
        newVehicleIDs = []
        hasInvalidation = False
        for vInfo in self.getVehiclesInfo():
            if vInfo is not None:
                if vInfo.vehTypeCD and vInfo.vehTypeCD not in vehInvCDs:
                    newVehicleIDs.append(INV_ID_CLEAR_VEHICLE)
                    hasInvalidation = True
                else:
                    newVehicleIDs.append(vInfo.vehInvID)

        if hasInvalidation:
            if self._prbType == PREBATTLE_TYPE.FALLOUT:
                return SetVehiclesUnitCtx(newVehicleIDs, waitingID='prebattle/change_settings')
            return SetVehicleUnitCtx(waitingID='prebattle/change_settings')
        else:
            return

    def request(self, ctx, callback=None):
        requestType = ctx.getRequestType()
        if requestType in self._requestHandlers:
            LOG_DEBUG('Unit request', ctx)
            self._requestHandlers[requestType](ctx, callback=callback)
        else:
            LOG_ERROR('Handler not found', ctx)
            if callback:
                callback(False)

    def getUnitFullData(self, unitIdx=None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        dbID = account_helpers.getAccountDatabaseID()
        pInfo = self._buildPlayerInfo(unitIdx, unit, dbID, unit.getPlayerSlotIdx(dbID), unit.getPlayer(dbID))
        unitState = self._buildFlags(unit)
        unitStats = self._buildStats(unitIdx, unit)
        slotsIter = self.getSlotsIterator(unitIdx, unit)
        return unit_items.UnitFullData(unit, unitState, unitStats, pInfo, slotsIter)

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
                if dbID in vehicles and vehicles[dbID]:
                    vehicle = vehicles[dbID][0]
            yield unit_items.SlotInfo(slotIdx, state, player, vehicle)

        return

    def isCommander(self, dbID=None, unitIdx=None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        _, unit = self.getUnit(unitIdx=unitIdx)
        return UnitPermissions.isCommander(unit.getPlayers().get(dbID, {}).get('role', 0))

    def isParentControlActivated(self, callback=None):
        """
        Is parent control now activated
        Args:
            callback: operation callback
        """
        if prb_getters.isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback:
                callback(False)
            return True
        return False

    def _createRosterSettings(self):
        return unit_items.UnitRosterSettings()

    def _buildPlayerInfo(self, unitIdx, unit, dbID, slotIdx=-1, data=None):
        """
        Builds player info based on unit data
        Args:
            unitIdx: unit index
            unit: client unit object
            dbID: player database ID
            slotIdx: slot index
            data: player's unit data
        """
        if data is None:
            data = {}
        if slotIdx != -1:
            isReady = unit.isPlayerReadyInSlot(slotIdx)
            isInSlot = True
        else:
            isReady = False
            isInSlot = False
        return unit_items.PlayerUnitInfo(dbID, unitIdx, unit, isReady=isReady, isInSlot=isInSlot, slotIdx=slotIdx, **data)

    def _buildStats(self, unitIdx, unit):
        """
        Builds unit stats
        Args:
            unitIdx: unit index
            unit: client unit object
        """
        readyCount = 0
        occupiedSlotsCount = 0
        openedSlotsCount = 0
        curTotalLevel = unit.getPointsSum()
        freeSlotsCount = 0
        isReadyInSlot = unit.isPlayerReadyInSlot
        isSlotFree = unit.isSlotFree
        isSlotClosed = unit.isSlotClosed
        isCreator = self.isCommander(unitIdx=unitIdx)
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
            curTotalLevel += 1

        levelsSeq = []
        for vehicles in unit.getVehicles().itervalues():
            for vehicle in vehicles:
                levelsSeq.append(vehicle.vehLevel if vehicle is not None else 0)

        levelsSeq.sort()
        return unit_items.UnitStats(readyCount, occupiedSlotsCount, openedSlotsCount, freeSlotsCount, curTotalLevel, levelsSeq)

    def _buildFlags(self, unit):
        """
        Builds unit entity flags
        Args:
            unit: client unit instance
        """
        return unit_items.UnitFlags(unit.getFlags(), isReady=unit.arePlayersReady(ignored=[settings.CREATOR_SLOT_INDEX]))


class _UnitIntroEntity(_UnitEntity):
    """
    Base class for unit intro entity
    """

    def __init__(self, entityFlags, modeFlags, requestHandlers, listenerClass, prbType):
        super(_UnitIntroEntity, self).__init__(entityFlags, modeFlags, requestHandlers or {}, listenerClass, prbType)

    def init(self, ctx=None):
        super(_UnitIntroEntity, self).init(ctx=ctx)
        self._loadUnit()
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def fini(self, ctx=None, woEvents=False):
        self._requestHandlers.clear()
        if not woEvents:
            if not self.canSwitch(ctx):
                self._unloadUnit()
        else:
            g_eventDispatcher.removeUnitFromCarousel(self._prbType, closeWindow=False)
        return super(_UnitIntroEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def canKeepMode(self):
        return False

    def leave(self, ctx, callback=None):
        g_prbCtrlEvents.onUnitIntroModeLeft()
        if callback:
            callback(True)

    def getUnit(self, unitIdx=None, safe=False):
        if unitIdx is None and not safe:
            LOG_ERROR('Unit index is not defined')
            return (None, None)
        else:
            return self._getUnit(unitIdx)

    def getConfirmDialogMeta(self, ctx):
        return rally_dialog_meta.createUnitIntroLeaveMeta(ctx, self._prbType, self.canSwitch(ctx))

    def getPermissions(self, dbID=None, unitIdx=None):
        return UnitIntroPermissions(self.hasLockedState())

    def getPlayerInfo(self, dbID=None, unitIdx=None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        return unit_items.PlayerUnitInfo(dbID, unitIdx, None)

    def isPlayerJoined(self, ctx):
        return ctx.getCtrlType() is CTRL_ENTITY_TYPE.UNIT and ctx.hasFlags(self.getFunctionalFlags())

    def showGUI(self, ctx=None):
        self._showWindow()

    def _createRosterSettings(self):
        return unit_items.SupportedRosterSettings.last(self._prbType)

    def _createActionsValidator(self):
        return NotSupportedActionsValidator()

    def _getUnit(self, unitIdx=None):
        """
        Inner part that incapsulates real part of unit getting
        in intro mode
        Args:
            unitIdx: unit index
        """
        return (0, None)

    def _showWindow(self):
        """
        Routine that should be invoked when its needed to show unit intro window
        """
        raise NotImplementedError

    def _loadUnit(self):
        """
        Routine that should be invoked when its needed to load unit intro tab
        in channels carousel and load unit intro window
        """
        raise NotImplementedError

    def _unloadUnit(self):
        """
        Routine that should be invoked when its needed to unload unit intro tab
        in channels carousel and close unit intro window
        """
        raise NotImplementedError


class UnitIntroEntity(_UnitIntroEntity):
    """
    Unit intro entity class: is welcome view
    """

    def __init__(self, modeFlags, requestHandlers, listenerClass, prbType):
        super(UnitIntroEntity, self).__init__(FUNCTIONAL_FLAG.UNIT_INTRO, modeFlags, requestHandlers or {}, listenerClass, prbType)


class UnitBrowserEntity(_UnitIntroEntity):
    """
    Unit browser entity class: is list of available rooms to join
    """

    def __init__(self, modeFlags, prbType):
        super(UnitBrowserEntity, self).__init__(FUNCTIONAL_FLAG.UNIT_BROWSER, modeFlags, {}, IUnitIntroListener, prbType)

    def canKeepMode(self):
        return True

    def leave(self, ctx, callback=None):
        g_prbCtrlEvents.onUnitBrowserModeLeft(ctx.getEntityType())
        if callback:
            callback(True)

    def getBrowser(self):
        """
        Getter for units browser instance
        """
        raise NotImplementedError


class UnitEntity(_UnitEntity):
    """
    Class for unit entity
    """

    def __init__(self, modeFlags, prbType):
        handlers = self._getRequestHandlers()
        super(UnitEntity, self).__init__(FUNCTIONAL_FLAG.UNIT, modeFlags, handlers, IUnitListener, prbType)
        self._actionsHandler = self._createActionsHandler()
        self._requestsProcessor = None
        self._vehiclesWatcher = None
        self._cooldown = self._createCooldownManager()
        self._deferredReset = False
        self._scheduler = self._createScheduler()
        self._showLeadershipNotification = False
        return

    def init(self, ctx=None):
        super(UnitEntity, self).init(ctx=ctx)
        flags = self.getFlags()
        self._requestsProcessor = self._createRequestProcessor()
        self._requestsProcessor.init()
        initResult = self._actionsHandler.executeInit(ctx)
        self._vehiclesWatcher = self._createVehicelsWatcher()
        self._vehiclesWatcher.validate()
        self._vehiclesWatcher.init()
        self._addClientUnitListeners()
        idle = flags.isInIdle()
        if idle:
            timeLeftInIdle = self._getTimeLeftInIdle()
        else:
            timeLeftInIdle = 0
        for listener in self.getListenersIterator():
            if idle:
                listener.onUnitFlagsChanged(flags, timeLeftInIdle)

        g_eventDispatcher.loadHangar()
        self._scheduler.init()
        return initResult | FUNCTIONAL_FLAG.LOAD_WINDOW

    def fini(self, ctx=None, woEvents=False):
        self._scheduler.fini()
        self._requestHandlers.clear()
        if self._requestsProcessor:
            self._requestsProcessor.fini()
            self._requestsProcessor = None
        if self._vehiclesWatcher:
            self._vehiclesWatcher.fini()
            self._vehiclesWatcher = None
        if self._actionsHandler is not None:
            if not woEvents and not self.canSwitch(ctx):
                self._actionsHandler.executeFini()
            self._actionsHandler.clear()
            self._actionsHandler = None
        if woEvents:
            g_eventDispatcher.removeUnitFromCarousel(self._prbType, closeWindow=False)
        self._removeClientUnitListeners()
        self._deferredReset = False
        return super(UnitEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def restore(self):
        self._actionsHandler.executeRestore()

    def showGUI(self, ctx=None):
        self._actionsHandler.showGUI()

    def addListener(self, listener):
        super(UnitEntity, self).addListener(listener)
        flags = self.getFlags()
        idle = flags.isInIdle()
        if idle:

            def doNotify():
                listener.onUnitFlagsChanged(flags, self._getTimeLeftInIdle())

            BigWorld.callback(0.0, doNotify)

    def rejoin(self):
        self._addClientUnitListeners()
        LOG_DEBUG('onUnitRejoin')
        self._invokeListeners('onUnitRejoin')

    def initEvents(self, listener):
        flags = self.getFlags()
        idle = flags.isInIdle()
        if idle:
            g_eventDispatcher.setUnitProgressInCarousel(self._prbType, True)
        if listener in self.getListenersIterator():
            if idle:
                listener.onUnitFlagsChanged(flags, self._getTimeLeftInIdle())
        else:
            LOG_ERROR('Listener not found', listener)

    def isPlayerJoined(self, ctx):
        return ctx.getCtrlType() is settings.CTRL_ENTITY_TYPE.UNIT and ctx.getEntityType() == self._prbType and ctx.getID() == self.getID()

    def isInQueue(self):
        _, unit = self.getUnit()
        return unit.isInQueue()

    def getConfirmDialogMeta(self, ctx):
        if self.hasLockedState():
            meta = rally_dialog_meta.RallyLeaveDisabledDialogMeta(CTRL_ENTITY_TYPE.UNIT, self._prbType)
        else:
            meta = rally_dialog_meta.createUnitLeaveMeta(ctx, self._prbType, self.canSwitch(ctx))
        return meta

    def getID(self):
        return prb_getters.getUnitMgrID()

    def getUnitIdx(self):
        return prb_getters.getUnitIdx()

    def getUnit(self, unitIdx=None, safe=False):
        if unitIdx is None:
            unitIdx = self.getUnitIdx()
        return (unitIdx, prb_getters.getUnit(unitIdx, safe=True))

    def hasLockedState(self):
        pInfo = self.getPlayerInfo()
        flags = self.getFlags()
        return pInfo.isInSlot and (flags.isInSearch() or flags.isInQueue() or flags.isInPreArena() or flags.isInArena() and pInfo.isInArena())

    def validateLevels(self):
        result = self._actionsValidator.getLevelsValidator().canPlayerDoAction(ignoreEnable=True)
        return result or super(UnitEntity, self).validateLevels()

    def getPermissions(self, dbID=None, unitIdx=None):
        pDbID = account_helpers.getAccountDatabaseID()
        if dbID is None:
            dbID = pDbID
        _, unit = self.getUnit(unitIdx=unitIdx)
        isPlayerReady = False
        roles = 0
        players = unit.getPlayers()
        if dbID in players:
            roles |= players[dbID].get('role', roles)
            inSlots = unit.getPlayerSlots()
            if dbID in inSlots:
                isPlayerReady = unit.isPlayerReadyInSlot(inSlots[dbID])
        return self._buildPermissions(roles, unit._flags, pDbID == dbID, isPlayerReady)

    def getReadyStates(self, unitIdx=None):
        result = []
        _, unit = self.getUnit(unitIdx=unitIdx)
        isSlotClosed = unit.isSlotClosed
        isPlayerReady = unit.isPlayerReadyInSlot
        for slotIdx in self._rosterSettings.getAllSlotsRange():
            isClosed = isSlotClosed(slotIdx)
            result.append(isPlayerReady(slotIdx) if not isClosed else None)

        return result

    def getPlayerInfo(self, dbID=None, unitIdx=None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        return self._buildPlayerInfo(unitIdx, unit, dbID, unit.getPlayerSlotIdx(dbID), unit.getPlayer(dbID))

    def getPlayers(self, unitIdx=None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        result = {}
        slotGetter = unit.getPlayerSlotIdx
        players = unit.getPlayers()
        for dbID, data in players.iteritems():
            result[dbID] = self._buildPlayerInfo(unitIdx, unit, dbID, slotGetter(dbID), data)

        return result

    def getCandidates(self, unitIdx=None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        players = unit.getPlayers()
        memberIDs = set((value['accountDBID'] for value in unit.getMembers().itervalues()))
        dbIDs = set(players.keys()).difference(memberIDs)
        result = {}
        for dbID, data in players.iteritems():
            if dbID not in dbIDs:
                continue
            result[dbID] = unit_items.PlayerUnitInfo(dbID, unitIdx, unit, **data)

        return result

    def getRosterType(self, unitIdx=None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx, safe=True)
        return unit.getRosterType()

    def getRoster(self, unitIdx=None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx, safe=True)
        return unit.getRoster()

    def getVehiclesInfo(self, dbID=None, unitIdx=None):
        if dbID is None:
            dbID = account_helpers.getAccountDatabaseID()
        _, unit = self.getUnit(unitIdx=unitIdx)
        vehicles = unit.getVehicles()
        return map(lambda vehicle: unit_items.VehicleInfo(**vehicle._asdict()), vehicles[dbID]) if dbID in vehicles else super(UnitEntity, self).getVehiclesInfo(dbID, unitIdx)

    def getSlotState(self, slotIdx, unitIdx=None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        return unit_items.SlotState(unit.isSlotClosed(slotIdx), unit.isSlotFree(slotIdx))

    def getFlags(self, unitIdx=None):
        _, unit = self.getUnit(unitIdx=unitIdx, safe=True)
        return self._buildFlags(unit)

    def getStats(self, unitIdx=None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        return self._buildStats(unitIdx, unit)

    def getComment(self, unitIdx=None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        return unit.getComment()

    def getCensoredComment(self, unitIdx=None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        pInfo = self.getPlayerInfo(unitIdx=unitIdx)
        if not pInfo.isCommander():
            return passCensor(unit.getComment())
        else:
            return unit.getComment()

    def getExtra(self, unitIdx=None):
        _, unit = self.getUnit(unitIdx=unitIdx)
        return unit.getExtra()

    def resetPlayerState(self):
        flags = self.getFlags()
        pInfo = self.getPlayerInfo()
        if pInfo.isCommander() and flags.isInSearch():
            self._requestsProcessor.doRawRequest('stopAutoSearch')
        elif pInfo.isReady:
            if not flags.isInIdle():
                ctx = SetReadyUnitCtx(False)
                ctx.resetVehicle = True
                self.setPlayerReady(ctx)
            else:
                self._deferredReset = True
        g_eventDispatcher.updateUI()

    def getShowLeadershipNotification(self):
        return self._showLeadershipNotification

    def doLeadershipNotificationShown(self):
        self._showLeadershipNotification = False

    def doAction(self, action=None):
        if super(UnitEntity, self).doAction(action):
            return True
        self._actionsHandler.execute()
        return True

    def leave(self, ctx, callback=None):
        ctx.startProcessing(callback)
        unitMgr = prb_getters.getClientUnitMgr()
        unitMgr.leave()

    def assign(self, ctx, callback=None):
        """
        Assigns player to prebattle.
        Args:
            ctx: assign request context
            callback: operation callback
        """
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

    def invite(self, ctx, callback=None):
        """
        Invites the list of players into prebattle.
        Args:
            ctx: invite request context
            callback: operation callback
        """
        pPermissions = self.getPermissions()
        if not pPermissions.canSendInvite():
            LOG_ERROR('Player can not send invites', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'invite', ctx.getDatabaseIDs(), ctx.getComment())
        self._cooldown.process(settings.REQUEST_TYPE.SEND_INVITE, coolDown=REQUEST_COOLDOWN.PREBATTLE_INVITES)

    def kick(self, ctx, callback=None):
        """
        Kick some player from unit.
        Args:
            ctx: kick request context
            callback: operation callback
        """
        pPermissions = self.getPermissions()
        if not pPermissions.canKick():
            LOG_ERROR('Player can not can another players', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'kick', ctx.getPlayerID())

    def setVehicle(self, ctx, callback=None):
        """
        Sets vehicle for current user
        Args:
            ctx: set vehicle request context
            callback: operation callback
        """
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

    def setVehicleList(self, ctx, callback=None):
        """
        Sets vehicle list for current user
        Args:
            ctx: set vehicle list request context
            callback: operation callback
        """
        if self._isInCoolDown(settings.REQUEST_TYPE.SET_VEHICLE_LIST, coolDown=ctx.getCooldown()):
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

            self._requestsProcessor.doRequest(ctx, 'setVehicleList', vehicleList=vehsList)
            self._cooldown.process(settings.REQUEST_TYPE.SET_VEHICLE_LIST, coolDown=ctx.getCooldown())
            return

    def setPlayerReady(self, ctx, callback=None):
        """
        Sets vehicle for current user
        Args:
            ctx: set vehicle request context
            callback: operation callback
        """
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
        if not self.isVehiclesReadyToBattle():
            LOG_DEBUG('Vehicles are not ready to battle', ctx)
            if callback:
                callback(False)
            return
        if isReady:
            vehInfos = self.getVehiclesInfo()
            if vehInfos:
                g_currentVehicle.selectVehicle(vehInfos[0].vehInvID)
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

    def closeSlot(self, ctx, callback=None):
        """
        Closes/opens given slot
        Args:
            ctx: close slot request context
            callback: operation callback
        """
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
            LOG_ERROR('Player can not close given slot', ctx)
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
        self._requestsProcessor.doRequest(ctx, 'closeSlot', slotIdx, isClosed)
        self._cooldown.process(settings.REQUEST_TYPE.CLOSE_SLOT, coolDown=ctx.getCooldown())

    def changeOpened(self, ctx, callback=None):
        """
        Closes/opens unit room
        Args:
            ctx: close request context
            callback: operation callback
        """
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
        self._requestsProcessor.doRequest(ctx, 'openUnit', isOpen=ctx.isOpened())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def changeComment(self, ctx, callback=None):
        """
        Changes comment in unit room
        Args:
            ctx: change comment request context
            callback: operation callback
        """
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
        self._requestsProcessor.doRequest(ctx, 'setComment', cgi.escape(ctx.getComment()))
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def lock(self, ctx, callback=None):
        """
        Locks/unlocks unit
        Args:
            ctx: lock request context
            callback: operation callback
        """
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
        self._requestsProcessor.doRequest(ctx, 'lockUnit', isLocked=ctx.isLocked())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def setRostersSlots(self, ctx, callback=None):
        """
        Sets rosters for slots
        Args:
            ctx: roster slots request context
            callback: operation callback
        """
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change rosters', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'setAllRosterSlots', ctx.getRosterSlots())

    def doAutoSearch(self, ctx, callback=None):
        """
        Do autosearch for team/team members
        Args:
            ctx: autosearch request context
            callback: operation callback
        """
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
            if not self.isVehiclesReadyToBattle():
                LOG_ERROR('Vehicles are not ready to battle', ctx)
                if callback:
                    callback(False)
                return
            vehInfos = self.getVehiclesInfo()
            if vehInfos:
                g_currentVehicle.selectVehicle(vehInfos[0].vehInvID)
            roster = self.getRosterSettings()
            stats = self.getStats()
            if stats.curTotalLevel > roster.getMaxTotalLevel():
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

    def doBattleQueue(self, ctx, callback=None):
        """
        Do battle enqueue/dequeue
        Args:
            ctx: battle queue request context
            callback: operation callback
        """
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
            stateAllowStartBattle = self._actionsValidator.validateStateToStartBattle()
            if not stateAllowStartBattle.isValid:
                LOG_DEBUG(stateAllowStartBattle.restriction, ctx)
                if callback:
                    callback(False)
                return
            if not self.isVehiclesReadyToBattle():
                LOG_ERROR('Vehicles are not ready to battle', ctx)
                if callback:
                    callback(False)
                return
            vehInfos = self.getVehiclesInfo()
            if vehInfos:
                g_currentVehicle.selectVehicle(vehInfos[0].vehInvID)
            roster = self.getRosterSettings()
            stats = self.getStats()
            if stats.curTotalLevel > roster.getMaxTotalLevel():
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

    def giveLeadership(self, ctx, callback=None):
        """
        Give leadership to selected player
        Args:
            ctx: give leadership request context
            callback: operation callback
        """
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

    def changeDivision(self, ctx, callback=None):
        """
        Change unit division
        Args:
            ctx: change division request context
            callback: operation callback
        """
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
        self._requestsProcessor.doRequest(ctx, 'changeSortieDivision', division=ctx.getDivisionID())
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_DIVISION, coolDown=ctx.getCooldown())

    @vehicleAmmoCheck
    def togglePlayerReadyAction(self, launchChain=False):
        """
        Toggles current player ready state.
        launchChain determines chain of the following servers methods have to be launched:
        1. If player not ready selectVehicle and setReady after
        2. If player ready setNotReady and deSelectVehicle after
        Args:
            launchChain: should we proceed to next chain
        """
        notReady = not self.getPlayerInfo().isReady
        if notReady:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        if launchChain:
            if notReady:
                selVehCtx = SetVehicleUnitCtx(vTypeCD=g_currentVehicle.item.intCD, waitingID='prebattle/change_settings')
                selVehCtx.setReady = True
                self.setVehicle(selVehCtx)
            else:
                ctx = SetReadyUnitCtx(False, 'prebattle/player_not_ready')
                ctx.resetVehicle = True
                LOG_DEBUG('Unit request', ctx)
                self.setPlayerReady(ctx)
        else:
            ctx = SetReadyUnitCtx(notReady, waitingID)
            LOG_DEBUG('Unit request', ctx)
            self.setPlayerReady(ctx)

    def isVehiclesReadyToBattle(self):
        """
        Check for vehicle validation
        """
        result = self._actionsValidator.getVehiclesValidator().canPlayerDoAction()
        return result is None or result.isValid

    def isDynamic(self):
        """
        Is this entity for dynamically created unit from battle
        (squad actually)
        """
        _, unit = self.getUnit()
        return unit.isDynamic()

    def getCooldownTime(self, rqTypeID):
        """
        Getter for cooldown for operation time
        Args:
            rqTypeID: request type ID
        """
        return self._cooldown.getTime(rqTypeID)

    def exitFromQueue(self):
        """
        Routine must be invoked to exit from the queue
        """
        self._actionsHandler.exitFromQueue()

    def unit_onUnitFlagsChanged(self, prevFlags, nextFlags):
        """
        Listener for client unit flags changed event
        Args:
            prevFlags: previous flags
            nextFlags: new flags
        """
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
            self.resetPlayerState()
        self._invokeListeners('onUnitFlagsChanged', flags, timeLeftInIdle)
        if not flags.isOnlyRosterWaitChanged():
            self._actionsHandler.setUnitChanged(flags)
        members = unit.getMembers()
        diff = []
        for slotIdx in self._rosterSettings.getAllSlotsRange():
            if prevFlags is not nextFlags:
                if slotIdx not in members:
                    continue
                dbID = members[slotIdx]['accountDBID']
                pInfo = self.getPlayerInfo(dbID=dbID, unitIdx=unitIdx)
                diff.append(pInfo)

        for listener in self.getListenersIterator():
            for pInfo in diff:
                listener.onUnitPlayerStateChanged(pInfo)

        g_eventDispatcher.updateUI()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        """
        Listener for client unit vehicle changed event
        Args:
            dbID: player database ID
            vehInvID: new vehicle inventory ID
            vehTypeCD: new vehicle intCD
        """
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
        self._invokeListeners('onUnitVehiclesChanged', dbID, (vInfo,))
        g_eventDispatcher.updateUI()
        return

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        """
        Listener for client unit vehicles changed event
        Args:
            dbID: player database ID
            vehicles: new vehicles list
        """
        vInfos = []
        for vehInvID, vehTypeCD in vehicles:
            if vehTypeCD:
                _, nationID, itemID = core_vehicles.parseIntCompactDescr(vehTypeCD)
                vehLevel = core_vehicles.g_cache.vehicle(nationID, itemID).level
            else:
                vehLevel = 0
            vInfo = unit_items.VehicleInfo(vehInvID, vehTypeCD, vehLevel)
            if dbID == account_helpers.getAccountDatabaseID() and not vInfo.isEmpty():
                vehicle = g_itemsCache.items.getItemByCD(vInfo.vehTypeCD)
                if vehicle is not None:
                    g_currentVehicle.selectVehicle(vehicle.invID)
            vInfos.append(vInfo)

        LOG_DEBUG('onUnitVehiclesChanged', dbID, vInfos)
        self._invokeListeners('onUnitVehiclesChanged', dbID, vInfos)
        g_eventDispatcher.updateUI()
        return

    def unit_onUnitReadyMaskChanged(self, prevMask, nextMask):
        """
        Listener for client unit ready mask changed event
        Args:
            prevMask: previous ready mask
            nextMask: new ready mask
        """
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
        for listener in self.getListenersIterator():
            for pInfo in diff:
                listener.onUnitPlayerStateChanged(pInfo)

        self._actionsHandler.setPlayersChanged()
        g_eventDispatcher.updateUI()

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        """
        Listener for client unit ready mask changed event
        Args:
            playerID: player database ID
            prevRoleFlags: previous role flags
            nextRoleFlags: new role flags
        """
        pInfo = self.getPlayerInfo(dbID=playerID)
        pPermissions = self.getPermissions(dbID=playerID)
        diff = prevRoleFlags ^ nextRoleFlags
        isOnlineChanged = diff & UNIT_ROLE.OFFLINE > 0
        isCreatorChanged = diff & UNIT_ROLE.CREATOR > 0
        inArenaChanged = diff & UNIT_ROLE.IN_ARENA > 0
        LOG_DEBUG('onUnitPlayerRolesChanged', pInfo, pPermissions)
        for listener in self.getListenersIterator():
            if isOnlineChanged:
                listener.onUnitPlayerOnlineStatusChanged(pInfo)
            if isCreatorChanged:
                if pInfo.isCurrentPlayer():
                    self._showLeadershipNotification = True
                listener.onUnitPlayerBecomeCreator(pInfo)
            if inArenaChanged:
                listener.onUnitPlayerEnterOrLeaveArena(pInfo)
            if not g_playerEvents.isPlayerEntityChanging:
                listener.onUnitPlayerRolesChanged(pInfo, pPermissions)

        g_eventDispatcher.updateUI()

    def unit_onUnitPlayerAdded(self, playerID, playerData):
        """
        Listener for client unit player added event
        Args:
            playerID: player database ID
            playerData: player added data
        """
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, unit.getPlayerSlotIdx(playerID), playerData)
        self._invokeListeners('onUnitPlayerAdded', pInfo)

    def unit_onUnitPlayerInfoChanged(self, playerID, playerData):
        """
        Listener for client unit player changed event
        Args:
            playerID: player database ID
            playerData: player changed data
        """
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, unit.getPlayerSlotIdx(playerID), playerData)
        self._invokeListeners('onUnitPlayerInfoChanged', pInfo)
        self._actionsHandler.setPlayerInfoChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        """
        Listener for client unit player removed event
        Args:
            playerID: player database ID
            playerData: player data
        """
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, -1, playerData)
        self._invokeListeners('onUnitPlayerRemoved', pInfo)

    def unit_onUnitSettingChanged(self, opCode, value):
        """
        Listener for client unit settings update event
        Args:
            opCode: operation code form UNIT_OP
            value: new value
        """
        self._invokeListeners('onUnitSettingChanged', opCode, value)

    def unit_onUnitRosterChanged(self):
        """
        Listener for client unit roster update event
        """
        rosterSettings = self._createRosterSettings()
        if rosterSettings != self._rosterSettings:
            self._rosterSettings = rosterSettings
            self._vehiclesWatcher.validate()
        self._invokeListeners('onUnitRosterChanged')

    def unit_onUnitMembersListChanged(self):
        """
        Listener for client unit members updated event
        """
        self._invokeListeners('onUnitMembersListChanged')
        g_eventDispatcher.updateUI()

    def unit_onUnitPlayersListChanged(self):
        """
        Listener for client unit players updated event
        """
        self._actionsHandler.setPlayersChanged()
        self._invokeListeners('onUnitPlayersListChanged')

    def unit_onUnitPlayerVehDictChanged(self, playerID):
        """
        Listener for client unit player's available vehicles update event
        Args:
            playerID: player database ID
        """
        unitIdx, unit = self.getUnit()
        pInfo = self._buildPlayerInfo(unitIdx, unit, playerID, unit.getPlayerSlotIdx(playerID), unit.getPlayer(playerID))
        self._invokeListeners('onUnitPlayerVehDictChanged', pInfo)

    def unit_onUnitExtraChanged(self, extras):
        """
        Listener for client unit extra data update event
        Args:
            extras: new extra data
        """
        self._invokeListeners('onUnitExtraChanged', extras)

    def _createActionsValidator(self):
        return UnitActionsValidator(self)

    def _createRosterSettings(self):
        _, unit = self.getUnit()
        return DynamicRosterSettings(unit)

    def _switchRosterSettings(self):
        """
        Refreshes state of current roster settings
        """
        self._rosterSettings = self._createRosterSettings()

    def _buildPermissions(self, roles, flags, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False):
        """
        Builds permissions object for given players' data
        Args:
            roles: roles mask from UNIT_ROLE
            flags: flags mask from UNIT_FLAGS
            isCurrentPlayer: is this current player
            isPlayerReady: is he ready
            hasLockedState: and has unit any locked state
        """
        return UnitPermissions(roles, flags, isCurrentPlayer, isPlayerReady)

    def _getRequestHandlers(self):
        """
        Getter for available unit's requests
        Returns:
            mapping of request type ID to opertaion
        """
        RQ_TYPE = settings.REQUEST_TYPE
        return {RQ_TYPE.ASSIGN: self.assign,
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
         RQ_TYPE.CHANGE_DIVISION: self.changeDivision,
         RQ_TYPE.SET_VEHICLE_LIST: self.setVehicleList}

    def _createActionsHandler(self):
        """
        Creates unit's actions handler object.
        """
        return UnitActionsHandler(self)

    def _switchActionsValidator(self):
        """
        Refreshes state of current actions handler
        """
        self._actionsValidator = self._createActionsValidator()

    def _createScheduler(self):
        """
        Creates unit's scheduler object.
        """
        return UnitScheduler(self)

    def _createCooldownManager(self):
        """
        Creates unit's cooldown manager object.
        """
        return UnitCooldownManager()

    def _createRequestProcessor(self):
        """
        Creates unit's requests processor object.
        """
        return UnitRequestProcessor(self)

    def _createVehicelsWatcher(self):
        """
        Creates unit's vehicles watcher object.
        """
        return UnitVehiclesWatcher(self)

    def _addClientUnitListeners(self):
        """
        Adds client unit subscriptions
        """
        unit = prb_getters.getUnit(self.getUnitIdx())
        unit.onUnitFlagsChanged += self.unit_onUnitFlagsChanged
        unit.onUnitReadyMaskChanged += self.unit_onUnitReadyMaskChanged
        unit.onUnitVehicleChanged += self.unit_onUnitVehicleChanged
        unit.onUnitVehiclesChanged += self.unit_onUnitVehiclesChanged
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
        """
        Removes client unit subscriptions
        """
        unit = prb_getters.getUnit(self.getUnitIdx(), safe=True)
        if unit:
            unit.onUnitFlagsChanged -= self.unit_onUnitFlagsChanged
            unit.onUnitReadyMaskChanged -= self.unit_onUnitReadyMaskChanged
            unit.onUnitVehicleChanged -= self.unit_onUnitVehicleChanged
            unit.onUnitVehiclesChanged -= self.unit_onUnitVehiclesChanged
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

    def _unassign(self, ctx, callback=None):
        """
        Unassigns player from prebattle.
        Args:
            ctx: assign request context
            callback: operation callback
        """
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
        self._requestsProcessor.doRequest(ctx, 'unassign', dbID)

    def _assign(self, ctx, callback=None):
        """
        Assigns player to prebattle.
        Args:
            ctx: assign request context
            callback: operation callback
        """
        slotIdx = ctx.getSlotIdx()
        dbID = ctx.getPlayerID()
        pPermissions = self.getPermissions()
        if not pPermissions.canAssignToSlot(dbID):
            LOG_ERROR('Player can not assign to slot', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'assign', dbID, slotIdx)

    def _reassign(self, ctx, callback=None):
        """
        Reassigns player to the same prebattle but in different slot.
        Args:
            ctx: assign request context
            callback: operation callback
        """
        slotIdx = ctx.getSlotIdx()
        dbID = ctx.getPlayerID()
        pPermissions = self.getPermissions()
        if pPermissions.canReassignToSlot():
            self._requestsProcessor.doRequest(ctx, 'reassign', dbID, slotIdx)
        elif pPermissions.canAssignToSlot(dbID):
            self._requestsProcessor.doRequest(ctx, 'assign', dbID, slotIdx)
        else:
            LOG_ERROR('Player can not (re)assign to slot', pPermissions)
            if callback:
                callback(False)

    def _setVehicle(self, ctx, callback=None):
        """
        Sets vehicle for current user
        Args:
            ctx: set vehicle request context
            callback: operation callback
        """
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
        vInfos = self.getVehiclesInfo()
        if findFirst(lambda vInfo: vInfo.vehInvID == vehInvID, vInfos) is not None:
            LOG_DEBUG('Player already selected vehicle', ctx)
            if callback:
                callback(True)
            return
        else:
            setReadyAfterVehicleSelect = ctx.setReady
            self._requestsProcessor.doRequest(ctx, 'setVehicle', vehInvID=vehInvID, setReady=setReadyAfterVehicleSelect)
            if setReadyAfterVehicleSelect:
                self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, coolDown=ctx.getCooldown())
            return

    def _clearVehicle(self, ctx, callback=None):
        """
        Clears vehicle for current user
        Args:
            ctx: set vehicle request context
            callback: operation callback
        """
        vInfos = self.getVehiclesInfo()
        if findFirst(lambda vInfo: vInfo.vehInvID, vInfos) is None:
            LOG_DEBUG('There is not vehicle in slot', ctx)
            if callback:
                callback(True)
            return
        else:
            self._requestsProcessor.doRequest(ctx, 'setVehicle', INV_ID_CLEAR_VEHICLE)
            return

    def _getTimeLeftInIdle(self):
        """
        Gets time left value in search for enemy team
        """
        _, unit = self.getUnit()
        result = 0
        if unit:
            timestamp = unit.getModalTimestamp()
            if timestamp:
                result = max(0, int(time.time() - time_utils.makeLocalServerTime(timestamp)))
        return result

    def _isInCoolDown(self, requestType, callback=None, coolDown=None):
        """
        Is given request in cooldonw now
        """
        if self._cooldown.validate(requestType, coolDown):
            if callback:
                callback(False)
            return True
        return False
