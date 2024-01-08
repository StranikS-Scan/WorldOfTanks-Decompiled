# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/dispatcher.py
import typing
import logging
import time
import types
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from adisp import adisp_async, adisp_process
from constants import IGR_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, GUI_SETTINGS
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities import initDevFunctional, finiDevFunctional
from gui.prb_control.entities.base.squad.entity import SquadEntity
from gui.prb_control.entities.base.unit.ctx import JoinUnitCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.factories import ControlFactoryComposite
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.ctx import CreatePrbEntityCtx, PrbCtrlRequestCtx
from gui.prb_control.entities.base.entity import NotSupportedEntity
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.invites import InvitesManager, AutoInvitesNotifier
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import CTRL_ENTITY_TYPE as _CTRL_TYPE, ENTER_UNIT_MGR_RESTORE_ERRORS, ENTER_UNIT_MGR_RESET_ERRORS
from gui.prb_control.settings import IGNORED_UNIT_BROWSER_ERRORS
from gui.prb_control.settings import IGNORED_UNIT_MGR_ERRORS
from gui.prb_control.settings import PREBATTLE_RESTRICTION, FUNCTIONAL_FLAG
from gui.prb_control.settings import UNIT_NOTIFICATION_TO_DISPLAY
from gui.prb_control.settings import REQUEST_TYPE as _RQ_TYPE
from gui.prb_control.storages import PrbStorageDecorator
from gui.shared import actions, events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.listeners_collection import ListenersCollection
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController, IRentalsController, IWinbackController
from skeletons.gui.game_control import IIGRController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.prb_control import IPrbControlLoader
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Any
_logger = logging.getLogger(__name__)

class _PreBattleDispatcher(ListenersCollection):
    gameSession = dependency.descriptor(IGameSessionController)
    rentals = dependency.descriptor(IRentalsController)
    igrCtrl = dependency.descriptor(IIGRController)
    eventsCache = dependency.descriptor(IEventsCache)
    winbackCtrl = dependency.descriptor(IWinbackController)

    def __init__(self):
        super(_PreBattleDispatcher, self).__init__()
        self.__requestCtx = PrbCtrlRequestCtx()
        self.__factories = ControlFactoryComposite()
        self.__entity = NotSupportedEntity()
        self.__prevEntity = NotSupportedEntity()
        self.__isStarted = False
        self._setListenerClass(IGlobalListener)

    def __del__(self):
        LOG_DEBUG('_PreBattleDispatcher deleted')

    def start(self):
        if self.__isStarted:
            return
        self.__isStarted = True
        g_eventDispatcher.init(self)
        result = self.__setDefault()
        self.__startListening()
        initDevFunctional()
        if result & FUNCTIONAL_FLAG.LOAD_PAGE == 0:
            g_eventDispatcher.loadHangar()
        if GUI_SETTINGS.specPrebatlesVisible and not prb_getters.areSpecBattlesHidden():
            g_eventDispatcher.addSpecBattlesToCarousel()

    def stop(self):
        if not self.__isStarted:
            return
        self.__isStarted = False
        self.__stopListening()
        finiDevFunctional()
        self.__clear(woEvents=True)
        g_eventDispatcher.fini()

    def getEntity(self):
        return self.__entity

    def getControlFactories(self):
        return self.__factories

    def getFunctionalState(self):
        factory = self.__factories.get(self.__entity.getCtrlType())
        return factory.createStateEntity(self.__entity) if factory is not None else FunctionalState()

    @adisp_async
    @adisp_process
    def create(self, ctx, callback=None):
        if ctx.getRequestType() != _RQ_TYPE.CREATE:
            LOG_ERROR('Invalid context to create prebattle/unit', ctx)
            if callback is not None:
                callback(False)
            return
        elif prb_getters.isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback is not None:
                callback(False)
            return
        else:
            entry = self.__factories.createEntry(ctx)
            if entry is None:
                LOG_ERROR('Entry not found', ctx)
                if callback is not None:
                    callback(False)
                return
            elif not entry.canCreate():
                if callback is not None:
                    callback(False)
                return
            ctx.addFlags(entry.getFunctionalFlags() | FUNCTIONAL_FLAG.SWITCH)
            if not self.__validateJoinOp(ctx):
                if callback is not None:
                    callback(False)
                return
            result = yield self.unlock(ctx)
            if not result:
                if callback is not None:
                    callback(False)
                return
            ctx.setForced(True)
            LOG_DEBUG('Request to create', ctx)
            self.__requestCtx = ctx
            entry.create(ctx, callback=callback)
            return

    @adisp_async
    @adisp_process
    def join(self, ctx, callback=None):
        if ctx.getRequestType() != _RQ_TYPE.JOIN:
            LOG_ERROR('Invalid context to join prebattle/unit', ctx)
            if callback is not None:
                callback(False)
            return
        else:
            entry = self.__factories.createEntry(ctx)
            if entry is None:
                LOG_ERROR('Entry not found', ctx)
                if callback is not None:
                    callback(False)
                return
            if not entry.canJoin():
                if callback is not None:
                    callback(False)
                return
            ctx.addFlags(entry.getFunctionalFlags() | FUNCTIONAL_FLAG.SWITCH)
            if not self.__validateJoinOp(ctx):
                if callback is not None:
                    callback(False)
                return
            result = yield self.unlock(ctx)
            if not result:
                if callback is not None:
                    callback(False)
                return
            ctx.setForced(True)
            LOG_DEBUG('Request to join', ctx)
            self.__requestCtx = ctx
            entry.join(ctx, callback=callback)
            return

    @adisp_async
    def leave(self, ctx, callback=None, ignoreConfirmation=False, parent=None):
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
            entity = self.__entity
            if not ignoreConfirmation:
                meta = entity.getConfirmDialogMeta(ctx)
                if meta:
                    entity.showDialog(meta, lambda result: self.__leaveCallback(result, ctx, callback), parent=parent)
                    return
            self.__leaveLogic(ctx, callback)
            return

    def __leaveCallback(self, result, ctx, callback=None):
        if not result:
            if callback is not None:
                callback(False)
            return
        else:
            self.__leaveLogic(ctx, callback)
            return

    def __leaveLogic(self, ctx, callback):
        entity = self.__entity
        if not entity.isActive():
            if callback is not None:
                callback(False)
            return
        else:
            ctrlType = ctx.getCtrlType()
            if entity.hasLockedState():
                entityType = entity.getEntityType()
                SystemMessages.pushI18nMessage(messages.getLeaveDisabledMessage(ctrlType, entityType), type=SystemMessages.SM_TYPE.Warning)
                if callback is not None:
                    callback(False)
                return
            LOG_DEBUG('Request to leave formation', ctx)
            self.__requestCtx = ctx
            entity.leave(ctx, callback=callback)
            return

    @adisp_async
    @adisp_process
    def unlock(self, unlockCtx, callback=None):
        if isinstance(self.__entity, NotSupportedEntity):
            if callback is not None:
                callback(True)
            return
        else:
            state = self.getFunctionalState()
            ctrlType = state.ctrlTypeID
            factory = self.__factories.get(ctrlType)
            if factory is None:
                LOG_ERROR('Factory is not found', state)
                if callback is not None:
                    callback(True)
                return
            ctx = factory.createLeaveCtx(unlockCtx.getFlags(), self.__entity.getEntityType())
            result = yield self.leave(ctx)
            if callback is not None:
                callback(result)
            return

    @adisp_async
    @adisp_process
    def select(self, entry, callback=None):
        ctx = entry.makeDefCtx()
        ctx.addFlags(entry.getModeFlags() & FUNCTIONAL_FLAG.LOAD_PAGE | FUNCTIONAL_FLAG.SWITCH)
        if not self.__validateJoinOp(ctx):
            if callback is not None:
                callback(False)
            return
        else:
            if entry.isVisualOnly():
                result = True
            else:
                result = yield self.unlock(ctx)
            if not result:
                if callback is not None:
                    callback(False)
                return
            ctx.setForced(True)
            LOG_DEBUG('Request to select', ctx)
            self.__requestCtx = ctx
            entry.select(ctx, callback=callback)
            return

    @adisp_async
    def sendPrbRequest(self, ctx, callback=None):
        self.__entity.request(ctx, callback=callback)

    def getPlayerInfo(self):
        factory = self.__factories.get(self.__entity.getCtrlType())
        return factory.createPlayerInfo(self.__entity) if factory is not None else PlayerDecorator()

    def doAction(self, action=None):
        if not (g_currentVehicle.isPresent() or g_currentPreviewVehicle.isPresent()):
            SystemMessages.pushMessage(messages.getInvalidVehicleMessage(PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT), type=SystemMessages.SM_TYPE.Error)
            return False
        LOG_DEBUG('Do GUI action', action)
        return self.__entity.doAction(action)

    @adisp_async
    @adisp_process
    def doSelectAction(self, action, callback=None):
        selectResult = self.__entity.doSelectAction(action)
        if selectResult.isProcessed:
            result = True
            if selectResult.newEntry is not None:
                result = yield self.select(selectResult.newEntry)
            if callback is not None:
                callback(result)
            g_eventDispatcher.dispatchSwitchResult(result)
            return
        else:
            entry = self.__factories.createEntryByAction(action)
            if entry is not None:
                if hasattr(entry, 'configure'):
                    entry.configure(action)
                result = yield self.select(entry)
                if callback is not None:
                    callback(result)
                g_eventDispatcher.dispatchSwitchResult(result)
                return
            if callback is not None:
                callback(False)
            g_eventDispatcher.dispatchSwitchResult(False)
            return

    @adisp_async
    @adisp_process
    def doLeaveAction(self, action, callback=None):
        factory = self.__factories.get(self.__entity.getCtrlType())
        if factory is None:
            LOG_ERROR('Factory is not found', self.__entity)
            if callback is not None:
                callback(True)
            g_eventDispatcher.dispatchSwitchResult(True)
            return
        else:
            flags = FUNCTIONAL_FLAG.UNDEFINED
            if action.isExit:
                flags = FUNCTIONAL_FLAG.EXIT
            elif self.__entity.canKeepMode():
                flags = self.__entity.getModeFlags()
            ctx = factory.createLeaveCtx(flags, entityType=self.__entity.getEntityType())
            if self.__entity.isInCoolDown(ctx.getRequestType()):
                if callback is not None:
                    callback(True)
                g_eventDispatcher.dispatchSwitchResult(True)
                return
            self.__entity.setCoolDown(ctx.getRequestType(), ctx.getCooldown())
            result = yield self.leave(ctx, ignoreConfirmation=action.ignoreConfirmation, parent=action.parent)
            if callback is not None:
                callback(result)
            g_eventDispatcher.dispatchSwitchResult(result)
            return

    def getGUIPermissions(self):
        return self.__entity.getPermissions()

    def isRequestInProcess(self):
        return self.__requestCtx.isProcessing()

    def restorePrevious(self):
        return self.__setEntity(CreatePrbEntityCtx(self.__prevEntity.getCtrlType(), self.__prevEntity.getEntityType(), flags=self.__prevEntity.getFunctionalFlags()))

    def pe_onArenaCreated(self):
        if self.__entity.hasLockedState():
            g_eventDispatcher.updateUI()

    def pe_onArenaJoinFailure(self, errorCode, errorStr):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onKickedFromArena(self, reasonCode):
        self.__entity.resetPlayerState()
        SystemMessages.pushMessage(messages.getKickReasonMessage(reasonCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onClientUpdated(self, diff, _):
        queueType = self.__entity.getQueueType()
        if queueType not in (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.WINBACK):
            return
        isSquadMode = isinstance(self.__entity, SquadEntity)
        isWinbackAvailable = self.winbackCtrl.isModeAvailable()
        needToUpdate = queueType == QUEUE_TYPE.RANDOMS and isWinbackAvailable and not isSquadMode or queueType == QUEUE_TYPE.WINBACK and not isWinbackAvailable
        if needToUpdate:
            self.__unsetEntity()
            self.__setDefault()

    def pe_onPrebattleAutoInvitesChanged(self):
        if GUI_SETTINGS.specPrebatlesVisible:
            isHidden = prb_getters.areSpecBattlesHidden()
            if isHidden:
                g_eventDispatcher.removeSpecBattlesFromCarousel()
            else:
                g_eventDispatcher.addSpecBattlesToCarousel()
        g_eventDispatcher.updateUI()

    def pe_onPrebattleInviteError(self, inviteID, errorCode, errorStr):
        self.__unsetEntity()
        self.__setDefault()

    def pe_onPrebattleJoined(self):
        if prb_getters.getClientPrebattle() is not None:
            self.__setLegacy(self.__requestCtx.getFlags())
        else:
            LOG_ERROR('ClientPrebattle is not defined')
            self.__setDefault()
            g_eventDispatcher.loadHangar()
        return

    def pe_onPrebattleJoinFailure(self, errorCode):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)
        self.__setDefault()
        g_eventDispatcher.loadHangar()

    def pe_onPrebattleLeft(self):
        flags = self.__requestCtx.getFlags()
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            prbType = 0
            if flags & FUNCTIONAL_FLAG.EXIT == 0:
                prbType = self.__entity.getEntityType()
            self.__unsetEntity(self.__requestCtx)
            self.__setLegacy(flags=flags, prbType=prbType)
        else:
            self.__unsetEntity(self.__requestCtx)

    def pe_onKickedFromPrebattle(self, kickReason):
        self.__unsetEntity()
        self.__setDefault()

    def ctrl_onLegacyIntroModeJoined(self, prbType):
        self.__setLegacy(flags=self.__requestCtx.getFlags(), prbType=prbType)

    def ctrl_onLegacyIntroModeLeft(self):
        flags = self.__requestCtx.getFlags()
        self.__unsetEntity(self.__requestCtx)
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            self.__setDefault()

    def ctrl_onLegacyInited(self):
        self.__setLegacy(flags=self.__requestCtx.getFlags())

    def ctrl_onUnitIntroModeJoined(self, prbType, flags):
        self.__setUnit(flags=flags, prbType=prbType)

    def ctrl_onUnitBrowserModeLeft(self, prbType):
        flags = self.__requestCtx.getFlags()
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            prbType = 0
            if flags & FUNCTIONAL_FLAG.EXIT == 0:
                unitEntity = self.__entity
                if unitEntity.canKeepMode():
                    prbType = unitEntity.getIntroType()
                    flags |= unitEntity.getModeFlags()
            self.__unsetEntity(self.__requestCtx)
            self.__setUnit(flags=flags, prbType=prbType)
        else:
            self.__unsetEntity(self.__requestCtx)

    def ctrl_onUnitIntroModeLeft(self):
        flags = self.__requestCtx.getFlags()
        self.__unsetEntity(self.__requestCtx)
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            self.__setDefault()

    def unitMgr_onUnitJoined(self, unitMgrID, prbType):
        entity = self.__entity
        ctx = JoinUnitCtx(unitMgrID, prbType)
        if entity.isPlayerJoined(ctx):
            entity.rejoin()
        else:
            self.__setUnit(flags=self.__requestCtx.getFlags(), prbType=self.__requestCtx.getEntityType())

    def unitMgr_onUnitLeft(self, unitMgrID, isFinishedAssembling):
        flags = self.__requestCtx.getFlags()
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            prbType = 0
            if flags & FUNCTIONAL_FLAG.EXIT == 0:
                unitEntity = self.__entity
                if unitEntity.canKeepMode():
                    prbType = unitEntity.getEntityType()
                    flags |= unitEntity.getModeFlags() | FUNCTIONAL_FLAG.UNIT_BROWSER
            self.__unsetEntity(self.__requestCtx)
            self.__setUnit(flags=flags, prbType=prbType)
        else:
            self.__unsetEntity(self.__requestCtx)

    def unitMgr_onUnitRestored(self, unitMgrID):
        self.__entity.restore()

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, errorCode, errorString):
        if errorCode not in IGNORED_UNIT_MGR_ERRORS:
            msgType, msgBody = messages.getUnitMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            self.__requestCtx.stopProcessing()
        if errorCode in ENTER_UNIT_MGR_RESTORE_ERRORS:
            self.restorePrevious()
        elif errorCode in ENTER_UNIT_MGR_RESET_ERRORS:
            if isinstance(self.__entity, NotSupportedEntity):
                self.__setDefault()

    def unitMgr_onUnitNotifyReceived(self, unitMgrID, notifyCode, notifyString, argsList):
        if notifyCode in UNIT_NOTIFICATION_TO_DISPLAY:
            msgType, msgBody = messages.getUnitMessage(notifyCode, notifyString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            self.__requestCtx.stopProcessing()

    def unitBrowser_onErrorReceived(self, errorCode, errorString):
        if errorCode not in IGNORED_UNIT_BROWSER_ERRORS:
            msgType, msgBody = messages.getUnitBrowserMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            self.__unsetEntity()
            self.__setDefault()

    def ctrl_onPreQueueJoined(self, queueType):
        self.__setPreQueue(flags=self.__requestCtx.getFlags(), queueType=queueType)

    def ctrl_onPreQueueJoinFailure(self, errorCode):
        self.__setDefault()

    def ctrl_onPreQueueLeft(self):
        flags = self.__requestCtx.getFlags()
        self.__unsetEntity(self.__requestCtx)
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            self.__setDefault()

    def ctrl_onUnitCreationFailure(self, _):
        self.__setDefault()

    def gs_onTillBanNotification(self, isPlayTimeBan, timeTillBlock):
        if prb_getters.isParentControlActivated():
            self.__entity.resetPlayerState()
            key = '#system_messages:gameSessionControl/korea/{0:>s}'
            if isPlayTimeBan:
                SystemMessages.pushI18nMessage(key.format('playTimeNotification'), timeTillBlock, type=SystemMessages.SM_TYPE.Warning)
            else:
                _, blockTime = self.gameSession.getCurfewBlockTime()
                formatter = lambda t: time.strftime('%H:%M', time.localtime(t))
                SystemMessages.pushI18nMessage(key.format('midnightNotification'), type=SystemMessages.SM_TYPE.Warning, blockTime=formatter(blockTime))

    def rc_onRentChange(self, vehicles):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.intCD in vehicles and g_currentVehicle.isDisabledInRent() and g_currentVehicle.isInPrebattle():
            self.__entity.resetPlayerState()

    def igr_onRoomChange(self, roomType, xpFactor):
        if roomType != IGR_TYPE.PREMIUM:
            if g_currentVehicle.isPremiumIGR() and g_currentVehicle.isInPrebattle():
                self.__entity.resetPlayerState()

    def notifyPrbEntitySwitched(self):
        if self.__isStarted:
            self._invokeListeners('onPrbEntitySwitched')

    def __startListening(self):
        g_playerEvents.onPrebattleJoined += self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure += self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft += self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle += self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaCreated += self.pe_onArenaCreated
        g_playerEvents.onArenaJoinFailure += self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena += self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged += self.pe_onPrebattleAutoInvitesChanged
        g_playerEvents.onPrebattleInvitationsError += self.pe_onPrebattleInviteError
        g_playerEvents.onUpdateSpecBattlesWindow += self.pe_onPrebattleAutoInvitesChanged
        g_playerEvents.onClientUpdated += self.pe_onClientUpdated
        if self.gameSession.lastBanMsg is not None:
            self.gs_onTillBanNotification(*self.gameSession.lastBanMsg)
        self.gameSession.onTimeTillBan += self.gs_onTillBanNotification
        self.rentals.onRentChangeNotify += self.rc_onRentChange
        self.igrCtrl.onIgrTypeChanged += self.igr_onRoomChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft += self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored += self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived += self.unitMgr_onUnitErrorReceived
            unitMgr.onUnitNotifyReceived += self.unitMgr_onUnitNotifyReceived
        else:
            LOG_ERROR('Unit manager is not defined')
        unitBrowser = prb_getters.getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived += self.unitBrowser_onErrorReceived
        else:
            LOG_ERROR('Unit browser is not defined')
        g_prbCtrlEvents.onLegacyIntroModeJoined += self.ctrl_onLegacyIntroModeJoined
        g_prbCtrlEvents.onLegacyIntroModeLeft += self.ctrl_onLegacyIntroModeLeft
        g_prbCtrlEvents.onLegacyInited += self.ctrl_onLegacyInited
        g_prbCtrlEvents.onUnitIntroModeJoined += self.ctrl_onUnitIntroModeJoined
        g_prbCtrlEvents.onUnitIntroModeLeft += self.ctrl_onUnitIntroModeLeft
        g_prbCtrlEvents.onUnitBrowserModeLeft += self.ctrl_onUnitBrowserModeLeft
        g_prbCtrlEvents.onUnitCreationFailure += self.ctrl_onUnitCreationFailure
        g_prbCtrlEvents.onPreQueueJoined += self.ctrl_onPreQueueJoined
        g_prbCtrlEvents.onPreQueueJoinFailure += self.ctrl_onPreQueueJoinFailure
        g_prbCtrlEvents.onPreQueueLeft += self.ctrl_onPreQueueLeft
        g_eventBus.addListener(events.PrbActionEvent.SELECT, self.__onDoSelectAction, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.PrbActionEvent.LEAVE, self.__onDoLeaveAction, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __stopListening(self):
        g_playerEvents.onPrebattleJoined -= self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure -= self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft -= self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle -= self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaCreated -= self.pe_onArenaCreated
        g_playerEvents.onArenaJoinFailure -= self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena -= self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.pe_onPrebattleAutoInvitesChanged
        g_playerEvents.onPrebattleInvitationsError -= self.pe_onPrebattleInviteError
        g_playerEvents.onUpdateSpecBattlesWindow -= self.pe_onPrebattleAutoInvitesChanged
        g_playerEvents.onClientUpdated -= self.pe_onClientUpdated
        self.gameSession.onTimeTillBan -= self.gs_onTillBanNotification
        self.rentals.onRentChangeNotify -= self.rc_onRentChange
        self.igrCtrl.onIgrTypeChanged -= self.igr_onRoomChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft -= self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored -= self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
            unitMgr.onUnitNotifyReceived -= self.unitMgr_onUnitNotifyReceived
        unitBrowser = prb_getters.getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived -= self.unitBrowser_onErrorReceived
        g_prbCtrlEvents.clear()
        g_eventBus.removeListener(events.PrbActionEvent.SELECT, self.__onDoSelectAction, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.PrbActionEvent.LEAVE, self.__onDoLeaveAction, scope=EVENT_BUS_SCOPE.LOBBY)

    def __clear(self, woEvents=False):
        if self.__requestCtx:
            self.__requestCtx.clear()
            self.__requestCtx = None
        if self.__factories is not None:
            self.__factories.clear()
            self.__factories = None
        if self.__entity is not None:
            self.__entity.fini(woEvents=woEvents)
            self.__entity = None
        self.__prevEntity = None
        g_eventDispatcher.removeSpecBattlesFromCarousel()
        self.clear()
        return

    def __setLegacy(self, flags=FUNCTIONAL_FLAG.UNDEFINED, prbType=0):
        return self.__setEntity(CreatePrbEntityCtx(_CTRL_TYPE.LEGACY, prbType, flags=flags, initCtx=self.__requestCtx))

    def __setUnit(self, flags=FUNCTIONAL_FLAG.UNDEFINED, prbType=0):
        return self.__setEntity(CreatePrbEntityCtx(_CTRL_TYPE.UNIT, prbType, flags=flags, initCtx=self.__requestCtx))

    def __setPreQueue(self, flags=FUNCTIONAL_FLAG.UNDEFINED, queueType=0):
        return self.__setEntity(CreatePrbEntityCtx(_CTRL_TYPE.PREQUEUE, queueType, flags=flags, initCtx=self.__requestCtx))

    def __setDefault(self):
        return self.__setEntity(CreatePrbEntityCtx(flags=FUNCTIONAL_FLAG.DEFAULT))

    def __validateJoinOp(self, ctx):
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            return False
        if self.__entity.isPlayerJoined(ctx):
            LOG_DEBUG('Player already joined', ctx)
            self.__entity.showGUI(ctx)
            return False
        if self.__entity.hasLockedState():
            SystemMessages.pushI18nMessage('#system_messages:prebattle/hasLockedState', type=SystemMessages.SM_TYPE.Warning)
            return False
        return True

    def __unsetEntity(self, ctx=None):
        if not isinstance(self.__entity, NotSupportedEntity):
            self._invokeListeners('onPrbEntitySwitching')
            self.__entity.fini(ctx=ctx)
            self.__prevEntity = self.__entity
            self.__entity = NotSupportedEntity()
            self.__requestCtx.stopProcessing(result=True)

    def __setEntity(self, ctx):
        created = self.__factories.createEntity(ctx)
        if created is not None:
            if created.getEntityFlags() & FUNCTIONAL_FLAG.SET_GLOBAL_LISTENERS > 0:
                created.addMutualListeners(self)
            if self.__entity is not None and not isinstance(self.__entity, NotSupportedEntity):
                factory = self.__factories.get(self.__entity.getCtrlType())
                if factory is not None:
                    _logger.info("__setEntity() new entity '%r' was created, previous entity '%r' was stopped", created, self.__entity)
                    leaveCtx = factory.createLeaveCtx(flags=self.__entity.getModeFlags() | FUNCTIONAL_FLAG.EXIT, entityType=self.__entity.getEntityType())
                    self.__entity.fini(ctx=leaveCtx)
            self.__entity = created
            if self.__prevEntity is not None and self.__prevEntity.isActive():
                self.__prevEntity.fini()
            self.__prevEntity = NotSupportedEntity()
            flag = self.__entity.init(ctx=ctx)
            self.notifyPrbEntitySwitched()
            ctx.clearFlags()
            ctx.addFlags(flag | created.getFunctionalFlags())
        LOG_DEBUG('Entity have been updated', ctx.getFlagsToStrings())
        ctx.clear()
        currentCtx = self.__requestCtx
        self.__requestCtx = PrbCtrlRequestCtx()
        currentCtx.stopProcessing(result=True)
        g_eventDispatcher.updateUI()
        return ctx.getFlags()

    @adisp_process
    def __onDoSelectAction(self, event):
        yield self.doSelectAction(event.action)

    @adisp_process
    def __onDoLeaveAction(self, event):
        yield self.doLeaveAction(event.action)


class _PrbPeripheriesHandler(object):
    lobbyContext = dependency.descriptor(ILobbyContext)

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
        if not self.lobbyContext.isAnotherPeriphery(peripheryID):
            LOG_ERROR('Player is in given periphery', peripheryID)
            return
        else:
            if postActions:
                if isinstance(postActions, types.ListType):
                    actionsList = postActions
                else:
                    LOG_ERROR('Argument "postActions" is invalid', postActions)
                    return
            else:
                actionsList = []
            actionsList.extend([actions.DisconnectFromPeriphery(loginViewPreselectedPeriphery=peripheryID), actions.ConnectToPeriphery(peripheryID), self.__enableAction])
            if finishActions:
                if isinstance(finishActions, types.ListType):
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

    @adisp_process
    def __doJoin(self, ctx):
        dispatcher = self.__loader.getDispatcher()
        if dispatcher:
            yield dispatcher.join(ctx)
        else:
            yield lambda callback: callback(None)


class _PrbControlLoader(IPrbControlLoader):
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

    def createBattleDispatcher(self):
        if self.__prbDispatcher is None:
            self.__prbDispatcher = _PreBattleDispatcher()
            g_playerEvents.onPrbDispatcherCreated()
        if self.__isEnabled:
            self.__doStart()
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
        self.createBattleDispatcher()

    def onAccountBecomeNonPlayer(self):
        self.__isEnabled = False
        self.__removeDispatcher()

    def onAvatarBecomePlayer(self):
        self.__isEnabled = False
        self.__removeDispatcher()
        self.__invitesManager.onAvatarBecomePlayer()
        self.__storage.onAvatarBecomePlayer()

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
