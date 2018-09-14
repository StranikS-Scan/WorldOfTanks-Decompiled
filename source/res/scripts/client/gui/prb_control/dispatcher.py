# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/dispatcher.py
import types
import time
from functools import partial
import BigWorld
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from adisp import async, process
from constants import IGR_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from FortifiedRegionBase import FORT_ERROR
from gui import SystemMessages, DialogsInterface, GUI_SETTINGS, game_control
from gui.LobbyContext import g_lobbyContext
from gui.prb_control import functional, prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.factories import ControlFactoryDecorator
from gui.prb_control.functional.battle_session import AutoInvitesNotifier
from gui.prb_control.functional.FunctionalCollection import FunctionalCollection
from gui.prb_control.invites import InvitesManager
from gui.prb_control.formatters import messages
from gui.prb_control.functional.interfaces import IGlobalListener
from gui.prb_control.context import PrbCtrlRequestCtx, CreateFunctionalCtx
from gui.prb_control.storage import PrbStorageDecorator
from gui.prb_control.settings import PREBATTLE_RESTRICTION, FUNCTIONAL_FLAG
from gui.prb_control.settings import CTRL_ENTITY_TYPE as _CTRL_TYPE
from gui.prb_control.settings import REQUEST_TYPE as _RQ_TYPE
from gui.prb_control.settings import IGNORED_UNIT_MGR_ERRORS
from gui.prb_control.settings import IGNORED_UNIT_BROWSER_ERRORS
from gui.prb_control.settings import RETURN_INTRO_UNIT_MGR_ERRORS
from PlayerEvents import g_playerEvents
from gui.server_events import g_eventsCache
from gui.shared import actions
from gui.shared.fortifications import getClientFortMgr
from gui.shared.utils.listeners_collection import ListenersCollection
from UnitBase import UNIT_ERROR

class _PrebattleDispatcher(ListenersCollection):

    def __init__(self):
        super(_PrebattleDispatcher, self).__init__()
        self.__requestCtx = None
        self.__collection = FunctionalCollection()
        self.__factories = ControlFactoryDecorator()
        self.__nextPrbFunctional = None
        self._setListenerClass(IGlobalListener)
        return

    def __del__(self):
        LOG_DEBUG('_PrebattleDispatcher deleted')

    def start(self):
        g_eventDispatcher.init(self)
        result = self.__setFunctional(CreateFunctionalCtx())
        self.__requestCtx = PrbCtrlRequestCtx()
        self.__startListening()
        functional.initDevFunctional()
        if result & FUNCTIONAL_FLAG.LOAD_PAGE == 0:
            BigWorld.callback(0.001, lambda : g_eventDispatcher.loadHangar())
        g_eventDispatcher.updateUI()
        if GUI_SETTINGS.specPrebatlesVisible and not prb_getters.areSpecBattlesHidden():
            g_eventDispatcher.addSpecBattlesToCarousel()

    def stop(self):
        self.__nextPrbFunctional = None
        self.__stopListening()
        functional.finiDevFunctional()
        self.__clear(woEvents=True)
        g_eventDispatcher.fini()
        return

    def getPrbFunctional(self):
        return self.__collection.getItem(_CTRL_TYPE.PREBATTLE)

    def getUnitFunctional(self):
        return self.__collection.getItem(_CTRL_TYPE.UNIT)

    def getPreQueueFunctional(self):
        return self.__collection.getItem(_CTRL_TYPE.PREQUEUE)

    def getFunctional(self, ctrlType):
        return self.__collection.getItem(ctrlType)

    def getFunctionalCollection(self):
        return self.__collection

    def getControlFactories(self):
        return self.__factories

    def hasModalEntity(self):
        return self.__collection.hasModalEntity()

    def getFunctionalState(self):
        return self.__collection.getState(self.__factories)

    @async
    @process
    def create(self, ctx, callback=None):
        if ctx.getRequestType() == _RQ_TYPE.CREATE:
            if not self.__requestCtx.isProcessing():
                result = yield self.unlock(ctx)
                if result:
                    entry = self.__factories.createEntry(ctx)
                    if entry:
                        LOG_DEBUG('Request to create', ctx)
                        self.__requestCtx = ctx
                        entry.create(ctx, callback=callback)
                    else:
                        LOG_ERROR('Entry not found', ctx)
                        if callback is not None:
                            callback(False)
                elif callback is not None:
                    callback(False)
            else:
                LOG_ERROR('Request is processing', self.__requestCtx)
                if callback is not None:
                    callback(False)
                yield lambda callback=None: callback
        else:
            LOG_ERROR('Invalid context to create', ctx)
            if callback is not None:
                callback(False)
            yield lambda callback=None: callback
        return

    @async
    @process
    def join(self, ctx, callback=None):
        if self.__validateJoinOp(ctx):
            result = yield self.unlock(ctx)
            ctx.setForced(result)
            if result:
                entry = self.__factories.createEntry(ctx)
                if entry:
                    LOG_DEBUG('Request to join', ctx)
                    self.__requestCtx = ctx
                    entry.join(ctx, callback=callback)
                else:
                    LOG_ERROR('Entry not found', ctx)
                    if callback is not None:
                        callback(False)
        else:
            if callback is not None:
                callback(False)
            yield lambda callback=None: callback
        return

    @async
    def leave(self, ctx, callback=None):
        if ctx.getRequestType() != _RQ_TYPE.LEAVE:
            LOG_ERROR('Invalid context to leave prebattle/unit', ctx)
            if callback is not None:
                callback(False)
            return
        elif self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            if callback is not None:
                callback(False)
            return
        else:
            ctrlType = ctx.getCtrlType()
            formation = self.__collection.getItem(ctx.getCtrlType())
            if formation is not None:
                if formation.hasLockedState():
                    entityType = formation.getEntityType()
                    SystemMessages.pushI18nMessage(messages.getLeaveDisabledMessage(ctrlType, entityType), type=SystemMessages.SM_TYPE.Warning)
                    if callback is not None:
                        callback(False)
                    return
                LOG_DEBUG('Request to leave formation', ctx)
                self.__requestCtx = ctx
                formation.leave(ctx, callback=callback)
            else:
                LOG_ERROR('Functional not found', ctx)
                if callback is not None:
                    callback(False)
            return

    @async
    @process
    def unlock(self, unlockCtx, callback=None):
        state = self.getFunctionalState()
        result = True
        if not state.isIntroMode:
            canDoLeave = True
        elif unlockCtx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            if state.ctrlTypeID == unlockCtx.getCtrlType() and state.entityTypeID != unlockCtx.getEntityType():
                canDoLeave = True
                unlockCtx.removeFlags(FUNCTIONAL_FLAG.SWITCH)
            else:
                canDoLeave = False
        else:
            canDoLeave = True
        if canDoLeave:
            factory = self.__factories.get(state.ctrlTypeID)
            result = False
            if factory:
                ctx = factory.createLeaveCtx(unlockCtx.getFlags())
                if ctx:
                    meta = self.__collection.getConfirmDialogMeta(state.ctrlTypeID, unlockCtx)
                    if meta:
                        result = yield DialogsInterface.showDialog(meta)
                    else:
                        result = True
                    if result:
                        result = yield self.leave(ctx)
                else:
                    LOG_ERROR('Can not create leave ctx', state)
            else:
                LOG_ERROR('Factory is not found', state)
        if callback is not None:
            callback(result)
        yield lambda callback=None: callback
        return

    @async
    @process
    def select(self, entry, callback=None):
        ctx = entry.makeDefCtx()
        if ctx and self.__validateJoinOp(ctx):
            result = yield self.unlock(ctx)
            ctx.setForced(result)
            if result:
                LOG_DEBUG('Request to select', ctx)
                self.__requestCtx = ctx
                entry.select(ctx, callback=callback)
            elif callback is not None:
                callback(False)
        else:
            if callback is not None:
                callback(False)
            yield lambda callback=None: callback
        return

    @async
    def sendPrbRequest(self, ctx, callback=None):
        prbFunctional = self.getFunctional(_CTRL_TYPE.PREBATTLE)
        if prbFunctional:
            prbFunctional.request(ctx, callback=callback)
        else:
            LOG_ERROR('prbFunctional is not found', ctx)
            if callback is not None:
                callback(False)
        return

    @async
    def sendUnitRequest(self, ctx, callback=None):
        unitFunctional = self.getFunctional(_CTRL_TYPE.UNIT)
        if unitFunctional:
            unitFunctional.request(ctx, callback=callback)
        else:
            LOG_ERROR('unitFunctional is not found', ctx)
            if callback is not None:
                callback(False)
        return

    @async
    def sendPreQueueRequest(self, ctx, callback=None):
        preQueueFunctional = self.getFunctional(_CTRL_TYPE.PREQUEUE)
        if preQueueFunctional is not None:
            preQueueFunctional.request(ctx, callback=callback)
        else:
            LOG_ERROR('preQueueFunctional is not found', ctx)
            if callback is not None:
                callback(False)
        return

    def exitFromQueue(self):
        self.__collection.exitFromQueue()

    def canPlayerDoAction(self):
        canDo, restriction = self.__collection.canPlayerDoAction(False)
        if canDo:
            if g_currentPreviewVehicle.isPresent():
                canDo = False
                restriction = PREBATTLE_RESTRICTION.PREVIEW_VEHICLE_IS_PRESENT
            elif not g_currentVehicle.isReadyToFight():
                if not g_currentVehicle.isPresent():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT
                elif g_currentVehicle.isInBattle():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE
                elif not g_currentVehicle.isCrewFull():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.CREW_NOT_FULL
                elif g_currentVehicle.isBroken():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_BROKEN
                elif g_currentVehicle.isFalloutOnly() and not game_control.getFalloutCtrl().isSelected():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_FALLOUT_ONLY
                elif g_currentVehicle.isDisabledInRoaming():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_ROAMING
                elif g_currentVehicle.isDisabledInPremIGR():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_IN_PREMIUM_IGR_ONLY
                elif g_currentVehicle.isDisabledInRent():
                    unit = self.getUnitFunctional()
                    if unit is not None and unit.getFlags().isInPreArena():
                        canDo = True
                    else:
                        canDo = False
                        if g_currentVehicle.isPremiumIGR():
                            restriction = PREBATTLE_RESTRICTION.VEHICLE_IGR_RENTALS_IS_OVER
                        else:
                            restriction = PREBATTLE_RESTRICTION.VEHICLE_RENTALS_IS_OVER
            if canDo:
                canDo, restriction = self.__collection.canPlayerDoAction(True)
        return (canDo, restriction)

    def getPlayerInfo(self):
        return self.__collection.getPlayerInfo(self.__factories)

    def doAction(self, action=None):
        if not g_currentVehicle.isPresent():
            SystemMessages.pushMessage(messages.getInvalidVehicleMessage(PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT), type=SystemMessages.SM_TYPE.Error)
            return False
        LOG_DEBUG('Do GUI action', action)
        return self.__collection.doAction(self.__factories, action)

    def doSelectAction(self, action):
        result = self.__collection.doSelectAction(action)
        if result.isProcessed:
            if result.newEntry is not None:
                self.__doSelect(result.newEntry)
            return True
        else:
            entry = self.__factories.createEntryByAction(action)
            if entry is not None:
                self.__doSelect(entry)
                return True
            return False

    @process
    def doLeaveAction(self, ctx):
        meta = self.__collection.getConfirmDialogMeta(ctx.getCtrlType(), ctx)
        if meta is not None:
            isConfirmed = yield DialogsInterface.showDialog(meta)
        else:
            isConfirmed = yield lambda callback: callback(True)
        if isConfirmed:
            yield self.leave(ctx)
        return

    def getGUIPermissions(self):
        return self.__collection.getGUIPermissions()

    def onCompanyStateChanged(self, _):
        if not self.getPrbFunctional().hasLockedState():
            g_eventDispatcher.updateUI()

    def setRequestCtx(self, ctx):
        result = True
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            result = False
        else:
            self.__requestCtx = ctx
        return result

    def pe_onArenaJoinFailure(self, errorCode, _):
        self.__collection.reset()
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onKickedFromArena(self, reasonCode):
        self.__collection.reset()
        SystemMessages.pushMessage(messages.getKickReasonMessage(reasonCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onPrebattleAutoInvitesChanged(self):
        if GUI_SETTINGS.specPrebatlesVisible:
            isHidden = prb_getters.areSpecBattlesHidden()
            if isHidden:
                g_eventDispatcher.removeSpecBattlesFromCarousel()
            else:
                g_eventDispatcher.addSpecBattlesToCarousel()
        g_eventDispatcher.updateUI()

    def pe_onPrebattleJoined(self):
        if prb_getters.getClientPrebattle() is not None:
            flags = self.__requestCtx.getFlags()
            self.__setFunctional(CreateFunctionalCtx(_CTRL_TYPE.PREBATTLE, flags=flags))
        else:
            LOG_ERROR('ClientPrebattle is not defined')
            self.__requestCtx.stopProcessing(result=False)
        return

    def pe_onPrebattleJoinFailure(self, errorCode):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)
        self.__requestCtx.stopProcessing(result=False)
        self.__requestCtx.clearFlags()
        g_eventDispatcher.updateUI()

    def pe_onPrebattleLeft(self):
        if self.__nextPrbFunctional is not None:
            self.__nextPrbFunctional()
            self.__nextPrbFunctional = None
            return
        else:
            flags = self.__requestCtx.getFlags()
            flags |= FUNCTIONAL_FLAG.LEAVE_ENTITY
            prbType = 0
            if flags & FUNCTIONAL_FLAG.SWITCH > 0:
                prbFunctional = self.getFunctional(_CTRL_TYPE.PREBATTLE)
                if prbFunctional is not None:
                    prbType = prbFunctional.getEntityType()
            self.__changePrbFunctional(flags=flags, prbType=prbType, stop=False)
            return

    def pe_onKickedFromPrebattle(self, _):
        self.__changePrbFunctional(stop=True)

    def gs_onTillBanNotification(self, isPlayTimeBan, timeTillBlock):
        if prb_getters.isParentControlActivated():
            self.__collection.reset()
            key = '#system_messages:gameSessionControl/korea/{0:>s}'
            if isPlayTimeBan:
                SystemMessages.g_instance.pushI18nMessage(key.format('playTimeNotification'), timeTillBlock, type=SystemMessages.SM_TYPE.Warning)
            else:
                gameSession = game_control.g_instance.gameSession
                notifyStartTime, blockTime = gameSession.getCurfewBlockTime()
                formatter = lambda t: time.strftime('%H:%M', time.localtime(t))
                SystemMessages.g_instance.pushI18nMessage(key.format('midnightNotification'), type=SystemMessages.SM_TYPE.Warning, preBlockTime=formatter(notifyStartTime), blockTime=formatter(blockTime))

    def rc_onRentChange(self, vehicles):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.intCD in vehicles and g_currentVehicle.isDisabledInRent() and g_currentVehicle.isInPrebattle():
            self.__collection.reset()

    def igr_onRoomChange(self, roomType, _):
        if roomType != IGR_TYPE.PREMIUM:
            if g_currentVehicle.isPremiumIGR() and g_currentVehicle.isInPrebattle():
                self.__collection.reset()

    def ctrl_onPrebattleIntroModeJoined(self, prbType, isLeaving):
        flags = self.__requestCtx.getFlags()
        if not isLeaving:
            self.__changePrbFunctional(flags=flags, prbType=prbType)
        else:
            self.__nextPrbFunctional = partial(self.__changePrbFunctional, flags=flags, prbType=prbType)

    def ctrl_onPrebattleIntroModeLeft(self):
        flags = self.__requestCtx.getFlags()
        flags |= FUNCTIONAL_FLAG.LEAVE_INTRO
        self.__changePrbFunctional(flags=flags)

    def ctrl_onPrebattleInited(self):
        self.__requestCtx.stopProcessing(result=True)
        self.__setFunctional(CreateFunctionalCtx(_CTRL_TYPE.PREBATTLE, flags=self.__requestCtx.getFlags(), initCtx=self.__requestCtx))
        g_eventDispatcher.updateUI()

    def ctrl_onUnitIntroModeJoined(self, prbType, flags):
        self.__changeUnitFunctional(flags=flags, prbType=prbType)

    def ctrl_onUnitIntroModeLeft(self):
        flags = self.__requestCtx.getFlags()
        flags |= FUNCTIONAL_FLAG.LEAVE_INTRO
        self.__changeUnitFunctional(flags=flags)

    def ctrl_onPreQueueFunctionalCreated(self, queueType):
        self.__changePreQueueFunctional(flags=self.__requestCtx.getFlags(), queueType=queueType)
        g_eventDispatcher.updateUI()

    def ctrl_onPreQueueFunctionalDestroyed(self):
        flags = self.__requestCtx.getFlags()
        flags |= FUNCTIONAL_FLAG.LEAVE_PRE_QUEUE
        self.__changePreQueueFunctional(flags=flags)

    def unitMgr_onUnitJoined(self, unitMgrID, unitIdx):
        unitFunctional = self.getFunctional(_CTRL_TYPE.UNIT)
        if unitFunctional is not None and unitFunctional.getID() == unitMgrID and unitFunctional.getUnitIdx() == unitIdx:
            unitFunctional.rejoin()
        else:
            if unitFunctional is not None:
                prbType = unitFunctional.getEntityType()
            else:
                prbType = 0
            self.__changeUnitFunctional(flags=self.__requestCtx.getFlags(), prbType=prbType)
        return

    def unitMgr_onUnitLeft(self, unitMgrID, unitIdx):
        flags = self.__requestCtx.getFlags()
        flags |= FUNCTIONAL_FLAG.LEAVE_ENTITY
        prbType = 0
        if flags & FUNCTIONAL_FLAG.SWITCH > 0:
            unitFunctional = self.getFunctional(_CTRL_TYPE.UNIT)
            if unitFunctional is not None:
                prbType = unitFunctional.getEntityType()
        self.__changeUnitFunctional(flags=flags, prbType=prbType)
        g_eventDispatcher.updateUI()
        return

    def unitMgr_onUnitRestored(self, unitMgrID, unitIdx):
        unitFunctional = self.getFunctional(_CTRL_TYPE.UNIT)
        flags = unitFunctional.getFlags()
        pInfo = unitFunctional.getPlayerInfo()
        if flags.isInPreArena() and pInfo.isInSlot:
            g_eventDispatcher.loadHangar()

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, unitIdx, errorCode, errorString):
        unitFunctional = self.getFunctional(_CTRL_TYPE.UNIT)
        if unitFunctional is not None:
            unitFunctional.setLastError(errorCode)
            if errorCode in RETURN_INTRO_UNIT_MGR_ERRORS and unitFunctional.canSwitchToIntro():
                self.__requestCtx.addFlags(FUNCTIONAL_FLAG.SWITCH)
            if errorCode == UNIT_ERROR.CANT_PICK_LEADER:
                self.__requestCtx.removeFlags(FUNCTIONAL_FLAG.SWITCH)
            elif errorCode == UNIT_ERROR.REMOVED_PLAYER:
                if self.__requestCtx.getCtrlType() == _CTRL_TYPE.UNIT and unitFunctional.getEntityType() != self.__requestCtx.getEntityType():
                    self.__requestCtx.removeFlags(FUNCTIONAL_FLAG.SWITCH)
        else:
            LOG_ERROR('Unit functional is not found')
        if errorCode not in IGNORED_UNIT_MGR_ERRORS:
            msgType, msgBody = messages.getUnitMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            self.__requestCtx.stopProcessing(result=False)
            g_eventDispatcher.updateUI()
        return

    def unitBrowser_onErrorReceived(self, errorCode, errorString):
        if errorCode not in IGNORED_UNIT_BROWSER_ERRORS:
            msgType, msgBody = messages.getUnitBrowserMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)

    def forMgr_onFortStateChanged(self):
        g_eventDispatcher.updateUI()

    def fortMgr_onFortResponseReceived(self, requestID, resultCode, _):
        self.__requestCtx.stopProcessing(result=resultCode in (FORT_ERROR.OK,))
        g_eventDispatcher.updateUI()

    def __startListening(self):
        """
        Subscribes to player events.
        """
        g_playerEvents.onPrebattleJoined += self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure += self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft += self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle += self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaJoinFailure += self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena += self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged += self.pe_onPrebattleAutoInvitesChanged
        gameSession = game_control.g_instance.gameSession
        rentCtr = game_control.g_instance.rentals
        igrCtr = game_control.g_instance.igr
        if gameSession.lastBanMsg is not None:
            self.gs_onTillBanNotification(*gameSession.lastBanMsg)
        gameSession.onTimeTillBan += self.gs_onTillBanNotification
        rentCtr.onRentChangeNotify += self.rc_onRentChange
        igrCtr.onIgrTypeChanged += self.igr_onRoomChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft += self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored += self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived += self.unitMgr_onUnitErrorReceived
        else:
            LOG_ERROR('Unit manager is not defined')
        unitBrowser = prb_getters.getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived += self.unitBrowser_onErrorReceived
        else:
            LOG_ERROR('Unit browser is not defined')
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortStateChanged += self.forMgr_onFortStateChanged
            fortMgr.onFortResponseReceived += self.fortMgr_onFortResponseReceived
        else:
            LOG_ERROR('Fort manager is not defined')
        g_prbCtrlEvents.onPrebattleIntroModeJoined += self.ctrl_onPrebattleIntroModeJoined
        g_prbCtrlEvents.onPrebattleIntroModeLeft += self.ctrl_onPrebattleIntroModeLeft
        g_prbCtrlEvents.onPrebattleInited += self.ctrl_onPrebattleInited
        g_prbCtrlEvents.onUnitIntroModeJoined += self.ctrl_onUnitIntroModeJoined
        g_prbCtrlEvents.onUnitIntroModeLeft += self.ctrl_onUnitIntroModeLeft
        g_prbCtrlEvents.onPreQueueFunctionalCreated += self.ctrl_onPreQueueFunctionalCreated
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed += self.ctrl_onPreQueueFunctionalDestroyed
        g_eventsCache.companies.onCompanyStateChanged += self.onCompanyStateChanged
        return

    def __stopListening(self):
        """
        Unsubscribe from player events.
        """
        g_eventsCache.companies.onCompanyStateChanged -= self.onCompanyStateChanged
        g_playerEvents.onPrebattleJoined -= self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure -= self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft -= self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle -= self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaJoinFailure -= self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena -= self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.pe_onPrebattleAutoInvitesChanged
        game_control.g_instance.gameSession.onTimeTillBan -= self.gs_onTillBanNotification
        game_control.g_instance.rentals.onRentChangeNotify -= self.rc_onRentChange
        game_control.g_instance.igr.onIgrTypeChanged -= self.igr_onRoomChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft -= self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored -= self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        unitBrowser = prb_getters.getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived -= self.unitBrowser_onErrorReceived
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortResponseReceived -= self.fortMgr_onFortResponseReceived
            fortMgr.onFortStateChanged -= self.forMgr_onFortStateChanged
        g_prbCtrlEvents.clear()

    def __clear(self, woEvents=False):
        if self.__requestCtx:
            self.__requestCtx.clear()
            self.__requestCtx = None
        if self.__collection is not None:
            self.__collection.clear(woEvents=woEvents)
            self.__collection = None
        if self.__factories is not None:
            self.__factories.clear()
            self.__factories = None
        g_eventDispatcher.removeSpecBattlesFromCarousel()
        self.clear()
        return

    def __changePrbFunctional(self, flags=FUNCTIONAL_FLAG.UNDEFINED, prbType=0, stop=True):
        self.__setFunctional(CreateFunctionalCtx(_CTRL_TYPE.PREBATTLE, prbType, flags=flags))
        if stop:
            self.__requestCtx.stopProcessing(result=True)

    def __changeUnitFunctional(self, flags=FUNCTIONAL_FLAG.UNDEFINED, prbType=0):
        self.__setFunctional(CreateFunctionalCtx(_CTRL_TYPE.UNIT, prbType, flags=flags, initCtx=self.__requestCtx))
        self.__requestCtx.stopProcessing(result=True)

    def __changePreQueueFunctional(self, flags=FUNCTIONAL_FLAG.UNDEFINED, queueType=0):
        self.__setFunctional(CreateFunctionalCtx(_CTRL_TYPE.PREQUEUE, queueType, flags=flags))
        self.__requestCtx.stopProcessing(result=True)

    def __validateJoinOp(self, ctx):
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            return False
        for func in self.__collection.getIterator():
            if func.isPlayerJoined(ctx):
                LOG_DEBUG('Player already joined', ctx)
                func.showGUI(ctx)
                return False
            if func.hasLockedState():
                SystemMessages.pushI18nMessage('#system_messages:prebattle/hasLockedState', type=SystemMessages.SM_TYPE.Warning)
                return False

        return True

    @process
    def __doSelect(self, entry):
        yield self.select(entry)

    def __setFunctional(self, ctx):
        ctx.addFlags(self.__collection.getFunctionalFlags())
        items = []
        for created in self.__factories.createFunctional(ctx):
            if ctx.hasFlags(FUNCTIONAL_FLAG.SET_GLOBAL_LISTENERS):
                created.addMutualListeners(self)
            items.append(created)

        for item in items:
            ctrlType = item.getCtrlType()
            self.__collection.setFunctionalFlags(ctrlType, ctx.getFlags())
            flag = self.__collection.setItem(item.getCtrlType(), item, ctx.getInitCtx())
            ctx.addFlags(flag)

        LOG_DEBUG('Functionals have been updated', ctx.getFlagsToStrings())
        ctx.clear()
        return ctx.getFlags()


class _PrbPeripheriesHandler(object):

    def __init__(self, loader):
        super(_PrbPeripheriesHandler, self).__init__()
        self.__joinChain = None
        self.__joinCtx = None
        self.__enableAction = actions.WaitFlagActivation()
        self.__loader = loader
        return

    def __del__(self):
        LOG_DEBUG('_PrbPeripheriesHandler deleted')

    def fini(self):
        if self.__joinChain is not None:
            self.__joinChain.onStopped -= self.__onJoinChainStopped
            self.__joinChain.stop()
            self.__joinChain = None
        self.__joinCtx = None
        self.__loader = None
        self.__enableAction = None
        return

    def join(self, peripheryID, ctx, postActions=None, finishActions=None):
        if not g_lobbyContext.isAnotherPeriphery(peripheryID):
            LOG_ERROR('Player is in given periphery', peripheryID)
            return
        else:
            if postActions:
                if type(postActions) is types.ListType:
                    actionsList = postActions
                else:
                    LOG_ERROR('Argument "postActions" is invalid', postActions)
                    return
            else:
                actionsList = []
            actionsList.extend([actions.DisconnectFromPeriphery(), actions.ConnectToPeriphery(peripheryID), self.__enableAction])
            if finishActions:
                if type(finishActions) is types.ListType:
                    actionsList.extend(finishActions)
                else:
                    LOG_ERROR('Argument "finishActions" is invalid', finishActions)
                    return
            self.__joinCtx = ctx
            if self.__joinChain is not None:
                self.__joinChain.onStopped -= self.__onJoinChainStopped
                self.__joinChain.stop()
            self.__enableAction.inactivate()
            self.__joinChain = actions.ActionsChain(actionsList)
            self.__joinChain.onStopped += self.__onJoinChainStopped
            self.__joinChain.start()
            return

    def activate(self):
        self.__enableAction.activate()

    def hasJoinAction(self):
        return self.__joinCtx is not None

    def __onJoinChainStopped(self, isCompleted):
        if isCompleted and self.__joinCtx:
            ctx, self.__joinCtx = self.__joinCtx, None
            self.__doJoin(ctx)
        else:
            self.__joinCtx = None
        return

    @process
    def __doJoin(self, ctx):
        dispatcher = self.__loader.getDispatcher()
        if dispatcher:
            yield dispatcher.join(ctx)
        else:
            yield lambda callback: callback(None)


class _PrbControlLoader(object):
    __slots__ = ('__prbDispatcher', '__invitesManager', '__autoNotifier', '__peripheriesHandler', '__storage', '__isEnabled')

    def __init__(self):
        super(_PrbControlLoader, self).__init__()
        self.__prbDispatcher = None
        self.__invitesManager = None
        self.__autoNotifier = None
        self.__peripheriesHandler = None
        self.__storage = None
        self.__isEnabled = False
        return

    def init(self):
        if self.__invitesManager is None:
            self.__invitesManager = InvitesManager(self)
            self.__invitesManager.init()
        if self.__autoNotifier is None:
            self.__autoNotifier = AutoInvitesNotifier(self)
        if self.__peripheriesHandler is None:
            self.__peripheriesHandler = _PrbPeripheriesHandler(self)
        if self.__storage is None:
            self.__storage = PrbStorageDecorator()
            self.__storage.init()
        return

    def fini(self):
        self.__removeDispatcher()
        if self.__invitesManager is not None:
            self.__invitesManager.fini()
            self.__invitesManager = None
        if self.__autoNotifier is not None:
            self.__autoNotifier.fini()
            self.__autoNotifier = None
        if self.__peripheriesHandler is not None:
            self.__peripheriesHandler.fini()
            self.__peripheriesHandler = None
        if self.__storage is not None:
            self.__storage.fini()
            self.__storage = None
        return

    def getDispatcher(self):
        return self.__prbDispatcher

    def getInvitesManager(self):
        return self.__invitesManager

    def getAutoInvitesNotifier(self):
        return self.__autoNotifier

    def getPeripheriesHandler(self):
        return self.__peripheriesHandler

    def getStorage(self):
        return self.__storage

    def isEnabled(self):
        return self.__isEnabled

    def setEnabled(self, enabled):
        if self.__isEnabled ^ enabled:
            self.__isEnabled = enabled
            if self.__isEnabled and self.__prbDispatcher is not None:
                self.__doStart()
        return

    def onAccountShowGUI(self, ctx):
        if self.__prbDispatcher is None:
            self.__prbDispatcher = _PrebattleDispatcher()
        if self.__isEnabled:
            self.__doStart()
        return

    def onAvatarBecomePlayer(self):
        self.__isEnabled = False
        self.__removeDispatcher()
        self.__invitesManager.onAvatarBecomePlayer()

    def onDisconnected(self):
        self.__isEnabled = False
        self.__removeDispatcher()
        self.__autoNotifier.stop()
        if self.__invitesManager is not None:
            self.__invitesManager.clear()
        if self.__autoNotifier is not None:
            self.__autoNotifier.stop()
        if self.__storage is not None:
            self.__storage.clear()
        return

    def __doStart(self):
        self.__storage.swap()
        self.__prbDispatcher.start()
        self.__invitesManager.start()
        self.__autoNotifier.start()
        self.__peripheriesHandler.activate()

    def __removeDispatcher(self):
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.stop()
            self.__prbDispatcher = None
        return


g_prbLoader = _PrbControlLoader()
