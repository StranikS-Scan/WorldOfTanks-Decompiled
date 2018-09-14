# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/dispatcher.py
import time
import types
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from adisp import async, process
from constants import IGR_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, DialogsInterface, GUI_SETTINGS
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities import initDevFunctional, finiDevFunctional
from gui.prb_control.entities.base.unit.ctx import JoinUnitCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.factories import ControlFactoryComposite
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.ctx import CreatePrbEntityCtx, PrbCtrlRequestCtx
from gui.prb_control.entities.base.entity import NotSupportedEntity
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.invites import InvitesManager, AutoInvitesNotifier
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import CTRL_ENTITY_TYPE as _CTRL_TYPE, ENTER_UNIT_MGR_ERRORS
from gui.prb_control.settings import IGNORED_UNIT_BROWSER_ERRORS
from gui.prb_control.settings import IGNORED_UNIT_MGR_ERRORS
from gui.prb_control.settings import PREBATTLE_RESTRICTION, FUNCTIONAL_FLAG
from gui.prb_control.settings import REQUEST_TYPE as _RQ_TYPE
from gui.prb_control.storages import PrbStorageDecorator
from gui.shared import actions
from gui.shared.utils.listeners_collection import ListenersCollection
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController, IRentalsController
from skeletons.gui.game_control import IIGRController, IFalloutController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class _PreBattleDispatcher(ListenersCollection):
    """
    Dispatcher is a class that handles all actions from player related to
    prebattles: select, join, create, etc. Also dispatcher itself is a listeners
    collection that is used for global listening of prebattle events.
    """
    gameSession = dependency.descriptor(IGameSessionController)
    rentals = dependency.descriptor(IRentalsController)
    igrCtrl = dependency.descriptor(IIGRController)
    falloutCtrl = dependency.descriptor(IFalloutController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        """
        In init we're setting default request context, factories composite
        default entity and supported listeners class.
        """
        super(_PreBattleDispatcher, self).__init__()
        self.__requestCtx = PrbCtrlRequestCtx()
        self.__factories = ControlFactoryComposite()
        self.__entity = NotSupportedEntity()
        self.__prevEntity = NotSupportedEntity()
        self._setListenerClass(IGlobalListener)

    def __del__(self):
        """
        Just a mark for logs that shows us when dispatcher was deleted.
        """
        LOG_DEBUG('_PreBattleDispatcher deleted')

    def start(self):
        """
        Start is called when dispatcher should start its job and process events.
        """
        g_eventDispatcher.init(self)
        result = self.__setDefault()
        self.__startListening()
        initDevFunctional()
        if result & FUNCTIONAL_FLAG.LOAD_PAGE == 0:
            g_eventDispatcher.loadHangar()
        if GUI_SETTINGS.specPrebatlesVisible and not prb_getters.areSpecBattlesHidden():
            g_eventDispatcher.addSpecBattlesToCarousel()

    def stop(self):
        """
        Is called when its time to stop dispatchers work.
        """
        self.__stopListening()
        finiDevFunctional()
        self.__clear(woEvents=True)
        g_eventDispatcher.fini()

    def getEntity(self):
        """
        Getter for current entity.
        Returns:
            current prebattle entity
        """
        return self.__entity

    def getControlFactories(self):
        """
        Getter for factories composite.
        Returns:
            control factories
        """
        return self.__factories

    def getFunctionalState(self):
        """
        Gets current functional state.
        Returns:
            current functional state
        """
        factory = self.__factories.get(self.__entity.getCtrlType())
        return factory.createStateEntity(self.__entity) if factory is not None else FunctionalState()

    @async
    @process
    def create(self, ctx, callback=None):
        """
        Asynchronous method for prebattle creation. Using given context its
        creates entry point via factories and uses it to create new prebattle.
        Current entity will be destroyed.
        Args:
            ctx: creation context
            callback: request callback
        """
        if ctx.getRequestType() != _RQ_TYPE.CREATE:
            LOG_ERROR('Invalid context to create prebattle/unit', ctx)
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
            if not entry.canCreate():
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

    @async
    @process
    def join(self, ctx, callback=None):
        """
        Asynchronous method for prebattle joining. Using given context its
        creates entry point via factories and uses it to join another prebattle.
        Current entity will be destroyed.
        Args:
            ctx: join context
            callback: request callback
        """
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

    @async
    @process
    def leave(self, ctx, callback=None):
        """
        Asynchronous method for prebattle leaving. Using given context its
        leaves current entity.
        Args:
            ctx: leave context
            callback: request callback
        """
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
            meta = entity.getConfirmDialogMeta(ctx)
            if meta:
                result = yield DialogsInterface.showDialog(meta)
                if not result:
                    if callback is not None:
                        callback(False)
                    return
            if not entity.isActive():
                if callback is not None:
                    callback(False)
                return
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

    @async
    @process
    def unlock(self, unlockCtx, callback=None):
        """
        Asynchronous method to leave from prebattle if player is in formation
        and shows confirmation dialog.
        Args:
            unlockCtx: unlock context
            callback: request callback
        """
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

    @async
    @process
    def select(self, entry, callback=None):
        """
        Asynchronous method to select prebattle mode and leave current mode if given entry
        is not just visual.
        Args:
            entry: newly selected entry point
            callback: request callback
        """
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

    @async
    def sendPrbRequest(self, ctx, callback=None):
        """
        Asynchronous method for send request to prebattle.
        Args:
            ctx: request context
            callback: request callback
        """
        self.__entity.request(ctx, callback=callback)

    def getPlayerInfo(self):
        """
        Gets information of player (is creator, is ready, etc.) in current active entity.
        Returns:
            current player info
        """
        factory = self.__factories.get(self.__entity.getCtrlType())
        return factory.createPlayerInfo(self.__entity) if factory is not None else PlayerDecorator()

    def doAction(self, action=None):
        """
        Processes action that comes from GUI by current entity.
        Args:
            action: given player's action
        Returns:
            was this action successful
        """
        if not g_currentVehicle.isPresent():
            SystemMessages.pushMessage(messages.getInvalidVehicleMessage(PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT), type=SystemMessages.SM_TYPE.Error)
            return False
        LOG_DEBUG('Do GUI action', action)
        return self.__entity.doAction(action)

    @async
    @process
    def doSelectAction(self, action, callback=None):
        """
        Processes action that comes from GUI to change to another mode.
        Args:
            action: given player's select action
            callback: request callback
        """
        selectResult = self.__entity.doSelectAction(action)
        if selectResult.isProcessed:
            result = True
            if selectResult.newEntry is not None:
                result = yield self.select(selectResult.newEntry)
            if callback is not None:
                callback(result)
            return
        else:
            entry = self.__factories.createEntryByAction(action)
            if entry is not None:
                result = yield self.select(entry)
                if callback is not None:
                    callback(result)
                return
            if callback is not None:
                callback(False)
            return

    @async
    @process
    def doLeaveAction(self, action, callback=None):
        """
        Processes action that comes from GUI to leave current mode.
        Args:
            action: given player's leave action
            callback: callback function or None
        """
        factory = self.__factories.get(self.__entity.getCtrlType())
        if factory is None:
            LOG_ERROR('Factory is not found', self.__entity)
            if callback is not None:
                callback(True)
            return
        else:
            flags = FUNCTIONAL_FLAG.UNDEFINED
            if action.isExit:
                flags = FUNCTIONAL_FLAG.EXIT
            elif self.__entity.canKeepMode():
                flags = self.__entity.getModeFlags()
            ctx = factory.createLeaveCtx(flags, entityType=self.__entity.getEntityType())
            result = yield self.leave(ctx)
            if callback is not None:
                callback(result)
            return

    def getGUIPermissions(self):
        """
        Gets available action in GUI for current player.
        Returns:
            current GUI permissions
        """
        return self.__entity.getPermissions()

    def isRequestInProcess(self):
        """
        Is current request in process.
        Returns:
            is request in process now
        """
        return self.__requestCtx.isProcessing()

    def restorePrevious(self):
        """
        Trying to set current entity to previous.
        Returns:
            initialization result as flags
        """
        return self.__setEntity(CreatePrbEntityCtx(self.__prevEntity.getCtrlType(), self.__prevEntity.getEntityType(), flags=self.__prevEntity.getFunctionalFlags()))

    def pe_onArenaCreated(self):
        """
        Player event listener for arena creation. Updates UI.
        """
        if self.__entity.hasLockedState():
            g_eventDispatcher.updateUI()

    def pe_onArenaJoinFailure(self, errorCode, errorStr):
        """
        Player event listener for arena join failure. Pushes system message.
        Args:
            errorCode: join error code
            errorStr: join error message
        """
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onKickedFromArena(self, reasonCode):
        """
        Player event listener for arena kick. Resets state and pushes system message.
        Args:
            reasonCode: kick reason code
        """
        self.__entity.resetPlayerState()
        SystemMessages.pushMessage(messages.getKickReasonMessage(reasonCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onPrebattleAutoInvitesChanged(self):
        """
        Player event listener for autoinvites state. Controls chat tab visibility of spec battles
        and updates UI.
        """
        if GUI_SETTINGS.specPrebatlesVisible:
            isHidden = prb_getters.areSpecBattlesHidden()
            if isHidden:
                g_eventDispatcher.removeSpecBattlesFromCarousel()
            else:
                g_eventDispatcher.addSpecBattlesToCarousel()
        g_eventDispatcher.updateUI()

    def pe_onPrebattleInviteError(self, inviteID, errorCode, errorStr):
        """
        Player event listener for prebattle invitation failed. Resets current entity to default.
        """
        self.__unsetEntity()
        self.__setDefault()

    def pe_onPrebattleJoined(self):
        """
        Player event listener for prebattle join. Sets entity to proper legacy or
        resets to default.
        """
        if prb_getters.getClientPrebattle() is not None:
            self.__setLegacy(self.__requestCtx.getFlags())
        else:
            LOG_ERROR('ClientPrebattle is not defined')
            self.__setDefault()
            g_eventDispatcher.loadHangar()
        return

    def pe_onPrebattleJoinFailure(self, errorCode):
        """
        Player event listener for prebattle join filure. Pushes system message and
        resets current entity to default.
        Args:
            errorCode: join error code
        """
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)
        self.__setDefault()
        g_eventDispatcher.loadHangar()

    def pe_onPrebattleLeft(self):
        """
        Player event listener for prebattle left. Tries to keep current mode or
        just unsets current entity.
        """
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
        """
        Player event listener for prebattle kick. Resets current entity to default.
        """
        self.__unsetEntity()
        self.__setDefault()

    def ctrl_onLegacyIntroModeJoined(self, prbType):
        """
        Prebattle control events listener for legacy intro join. Sets new legacy entity.
        Args:
            prbType: joined prebattle type
        """
        self.__setLegacy(flags=self.__requestCtx.getFlags(), prbType=prbType)

    def ctrl_onLegacyIntroModeLeft(self):
        """
        Prebattle control events listener for legacy intro leave. Unsets current legacy entity
        and inits default state if it is not switch.
        """
        flags = self.__requestCtx.getFlags()
        self.__unsetEntity(self.__requestCtx)
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            self.__setDefault()

    def ctrl_onLegacyInited(self):
        """
        Prebattle control events listener for legacy init. Sets new legacy entity.
        """
        self.__setLegacy(flags=self.__requestCtx.getFlags())

    def ctrl_onUnitIntroModeJoined(self, prbType, flags):
        """
        Prebattle control events listener for unit intro mode join. Sets new unit entity.
        Args:
            prbType: intro prebattle type
            flags: functional flags
        """
        self.__setUnit(flags=flags, prbType=prbType)

    def ctrl_onUnitBrowserModeLeft(self, prbType):
        """
        Prebattle control events listener for unit browser mode leave. Unsets current unit entity
        and tries to init intro mode if it is not switch.
        Args:
            prbType: intro prebattle type
        """
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
        """
        Prebattle control events listener for unit intro leave. Unsets current unit entity
        and inits default state if it is not switch.
        """
        flags = self.__requestCtx.getFlags()
        self.__unsetEntity(self.__requestCtx)
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            self.__setDefault()

    def unitMgr_onUnitJoined(self, unitMgrID, prbType):
        """
        Unit manager event listener for unit join. Sets unit entity if we're not already
        joined to it.
        Args:
            unitMgrID: unit manager identifier
            prbType: unit prebattle type
        """
        entity = self.__entity
        ctx = JoinUnitCtx(unitMgrID, prbType)
        if entity.isPlayerJoined(ctx):
            entity.rejoin()
        else:
            self.__setUnit(flags=self.__requestCtx.getFlags(), prbType=self.__requestCtx.getEntityType())

    def unitMgr_onUnitLeft(self, unitMgrID):
        """
        Unit manager listener for unit left. Tries to keep current mode or
        just unsets current entity.
        Args:
            unitMgrID: unit manager identifier
        """
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
        """
        Unit manager event listener for unit restoration.
        Args:
            unitMgrID: unit manager identifier
        """
        self.__entity.restore()

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, errorCode, errorString):
        """
        Unit manager event listener for unit request error. Pushes system message.
        Args:
            requestID: request identifier
            unitMgrID: unit manager identifier
            errorCode: request error code
            errorString: request error message
        """
        if errorCode not in IGNORED_UNIT_MGR_ERRORS:
            msgType, msgBody = messages.getUnitMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            self.__requestCtx.stopProcessing()
        if errorCode in ENTER_UNIT_MGR_ERRORS:
            self.restorePrevious()

    def unitBrowser_onErrorReceived(self, errorCode, errorString):
        """
        Unit browser event listener for request error. Pushes system message and resets current
        entity to default.
        Args:
            errorCode: request error code
            errorString: request error message
        """
        if errorCode not in IGNORED_UNIT_BROWSER_ERRORS:
            msgType, msgBody = messages.getUnitBrowserMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            self.__unsetEntity()
            self.__setDefault()

    def ctrl_onPreQueueJoined(self, queueType):
        """
        Prebattle control events for pre queue join. Sets pre queue entity.
        Args:
            queueType: queue type
        """
        self.__setPreQueue(flags=self.__requestCtx.getFlags(), queueType=queueType)

    def ctrl_onPreQueueJoinFailure(self, errorCode):
        """
        Player event listener for prequeue join filure. Resets current entity to default.
        Args:
            errorCode: join error code
        """
        self.__setDefault()

    def ctrl_onPreQueueLeft(self):
        """
        Prebattle control events for pre queue leave. Unsets current unit entity
        and inits default state if it is not switch.
        """
        flags = self.__requestCtx.getFlags()
        self.__unsetEntity(self.__requestCtx)
        if flags & FUNCTIONAL_FLAG.SWITCH == 0:
            self.__setDefault()

    def gs_onTillBanNotification(self, isPlayTimeBan, timeTillBlock):
        """
        Game session listener for ban notification. Resets current entity to default.
        Args:
            isPlayTimeBan: is ban for play time
            timeTillBlock: time when block will be activated
        """
        if prb_getters.isParentControlActivated():
            self.__entity.resetPlayerState()
            key = '#system_messages:gameSessionControl/korea/{0:>s}'
            if isPlayTimeBan:
                SystemMessages.pushI18nMessage(key.format('playTimeNotification'), timeTillBlock, type=SystemMessages.SM_TYPE.Warning)
            else:
                notifyStartTime, blockTime = self.gameSession.getCurfewBlockTime()
                formatter = lambda t: time.strftime('%H:%M', time.localtime(t))
                SystemMessages.pushI18nMessage(key.format('midnightNotification'), type=SystemMessages.SM_TYPE.Warning, preBlockTime=formatter(notifyStartTime), blockTime=formatter(blockTime))

    def rc_onRentChange(self, vehicles):
        """
        Rental listener for vehicles state update. Resets current player's state.
        Args:
            vehicles: list of affected vehicle intCDs
        """
        if g_currentVehicle.isPresent() and g_currentVehicle.item.intCD in vehicles and g_currentVehicle.isDisabledInRent() and g_currentVehicle.isInPrebattle():
            self.__entity.resetPlayerState()

    def igr_onRoomChange(self, roomType, xpFactor):
        """
        IGR listener for room state. Resets current player's state when he is in premium IGR,
        joined some prebattle and this room is no more premium.
        Args:
            roomType: new IGR room type
            xpFactor: xp boost factor
        """
        if roomType != IGR_TYPE.PREMIUM:
            if g_currentVehicle.isPremiumIGR() and g_currentVehicle.isInPrebattle():
                self.__entity.resetPlayerState()

    def __startListening(self):
        """
        Subscribes to player and system events.
        """
        g_playerEvents.onPrebattleJoined += self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure += self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft += self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle += self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaCreated += self.pe_onArenaCreated
        g_playerEvents.onArenaJoinFailure += self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena += self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged += self.pe_onPrebattleAutoInvitesChanged
        g_playerEvents.onPrebattleInvitationsError += self.pe_onPrebattleInviteError
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
        g_prbCtrlEvents.onPreQueueJoined += self.ctrl_onPreQueueJoined
        g_prbCtrlEvents.onPreQueueJoinFailure += self.ctrl_onPreQueueJoinFailure
        g_prbCtrlEvents.onPreQueueLeft += self.ctrl_onPreQueueLeft
        return

    def __stopListening(self):
        """
        Unsubscribe from player and system events.
        """
        g_playerEvents.onPrebattleJoined -= self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure -= self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft -= self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle -= self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaCreated -= self.pe_onArenaCreated
        g_playerEvents.onArenaJoinFailure -= self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena -= self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.pe_onPrebattleAutoInvitesChanged
        g_playerEvents.onPrebattleInvitationsError -= self.pe_onPrebattleInviteError
        self.gameSession.onTimeTillBan -= self.gs_onTillBanNotification
        self.rentals.onRentChangeNotify -= self.rc_onRentChange
        self.igrCtrl.onIgrTypeChanged -= self.igr_onRoomChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft -= self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored -= self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        unitBrowser = prb_getters.getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived -= self.unitBrowser_onErrorReceived
        g_prbCtrlEvents.clear()

    def __clear(self, woEvents=False):
        """
        Clears dispatchers current state and attributes.
        Args:
            woEvents: flag that we should not raise any events
        """
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
        """
        Sets current entity to legacy and stops request processing.
        Args:
            flags: functional flags
            prbType: prebattle type
        
        Returns:
            initialization result as flags
        """
        return self.__setEntity(CreatePrbEntityCtx(_CTRL_TYPE.LEGACY, prbType, flags=flags, initCtx=self.__requestCtx))

    def __setUnit(self, flags=FUNCTIONAL_FLAG.UNDEFINED, prbType=0):
        """
        Sets current entity to unit and stops request processing.
        Args:
            flags: functional flags
            prbType: prebattle type
        
        Returns:
            initialization result as flags
        """
        return self.__setEntity(CreatePrbEntityCtx(_CTRL_TYPE.UNIT, prbType, flags=flags, initCtx=self.__requestCtx))

    def __setPreQueue(self, flags=FUNCTIONAL_FLAG.UNDEFINED, queueType=0):
        """
        Sets current entity to queue and stops request processing.
        Args:
            flags: functional flags
            queueType: queue type
        
        Returns:
            initialization result as flags
        """
        return self.__setEntity(CreatePrbEntityCtx(_CTRL_TYPE.PREQUEUE, queueType, flags=flags, initCtx=self.__requestCtx))

    def __setDefault(self):
        """
        Sets current entity to default (allowing the system to initialize
        by itself) and stops request processing.
        Returns:
            initialization result as flags
        """
        return self.__setEntity(CreatePrbEntityCtx(flags=FUNCTIONAL_FLAG.DEFAULT))

    def __validateJoinOp(self, ctx):
        """
        Validates join operation: is request in process, is player already joined,
        or current entity has locked state.
        Args:
            ctx: join request context
        
        Returns:
            was validation passed
        """
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
        """
        Unset current entity.
        Args:
            ctx: leave, join or create request context
        """
        if not isinstance(self.__entity, NotSupportedEntity):
            self._invokeListeners('onPrbEntitySwitching')
            self.__entity.fini(ctx=ctx)
            self.__prevEntity = self.__entity
            self.__entity = NotSupportedEntity()
            self.__requestCtx.stopProcessing(result=True)

    def __setEntity(self, ctx):
        """
        Set current entity and clear request context.
        Args:
            ctx: set entity context
        
        Returns:
            integer containing initialization result as flags
        """
        created = self.__factories.createEntity(ctx)
        if created is not None:
            if created.getEntityFlags() & FUNCTIONAL_FLAG.SET_GLOBAL_LISTENERS > 0:
                created.addMutualListeners(self)
            self.__entity = created
            self.__prevEntity = NotSupportedEntity()
            flag = self.__entity.init(ctx=ctx)
            self._invokeListeners('onPrbEntitySwitched')
            ctx.clearFlags()
            ctx.addFlags(flag | created.getFunctionalFlags())
        LOG_DEBUG('Entity have been updated', ctx.getFlagsToStrings())
        ctx.clear()
        self.__requestCtx.stopProcessing(result=True)
        self.__requestCtx = PrbCtrlRequestCtx()
        g_eventDispatcher.updateUI()
        return ctx.getFlags()


class _PrbPeripheriesHandler(object):
    """
    Class of handler for join to prebattle/unit that is on another periphery.
    """
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, loader):
        """
        Constructor for default attrs initialization.
        Args:
            loader: prebattle control loader
        """
        super(_PrbPeripheriesHandler, self).__init__()
        self.__joinChain = None
        self.__joinCtx = None
        self.__enableAction = actions.WaitFlagActivation()
        self.__loader = loader
        return

    def __del__(self):
        """
        Delete method for debug purposes logging.
        """
        LOG_DEBUG('_PrbPeripheriesHandler deleted')

    def fini(self):
        """
        Finalization.
        """
        if self.__joinChain is not None:
            self.__joinChain.onStopped -= self.__onJoinChainStopped
            self.__joinChain.stop()
            self.__joinChain = None
        self.__joinCtx = None
        self.__loader = None
        self.__enableAction = None
        return

    def join(self, peripheryID, ctx, postActions=None, finishActions=None):
        """
        Join to prebattle/unit that is on another periphery.
        Args:
            peripheryID: periphery identifier
            ctx: join request context
            postActions: post actions chain
            finishActions: finish actions chain
        """
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
            actionsList.extend([actions.DisconnectFromPeriphery(), actions.ConnectToPeriphery(peripheryID), self.__enableAction])
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
        """
        Activate handler when player login to server and prbLoader is enabled.
        """
        self.__enableAction.activate()

    def hasJoinAction(self):
        """
        Check if it has join action.
        Returns:
            has it join action
        """
        return self.__joinCtx is not None

    def __onJoinChainStopped(self, isCompleted):
        """
        Callback listener for join action
        Args:
            isCompleted: was it completed
        """
        if isCompleted and self.__joinCtx:
            ctx, self.__joinCtx = self.__joinCtx, None
            self.__doJoin(ctx)
        else:
            self.__joinCtx = None
        return

    @process
    def __doJoin(self, ctx):
        """
        Calls dispatcher join method with context given.
        Args:
            ctx: join request context
        """
        dispatcher = self.__loader.getDispatcher()
        if dispatcher:
            yield dispatcher.join(ctx)
        else:
            yield lambda callback: callback(None)


class _PrbControlLoader(object):
    """
    Loader for for next entities:
    - prebattle dispatcher. When player login to server, it creates
    prebattle dispatcher. And when GUI says isEnabled, it starts prebattle
    dispatcher. When player come to battle or login page, it removes
    prebattle dispatcher;
    - invites manager for invitation to prebattle;
    - notifier of auto invites.
    """
    __slots__ = ('__prbDispatcher', '__invitesManager', '__autoNotifier', '__peripheriesHandler', '__storage', '__isEnabled')

    def __init__(self):
        """
        Constructor for default initialization.
        """
        super(_PrbControlLoader, self).__init__()
        self.__prbDispatcher = None
        self.__invitesManager = None
        self.__autoNotifier = None
        self.__peripheriesHandler = None
        self.__storage = None
        self.__isEnabled = False
        return

    def init(self):
        """
        Loader initializations work: subscribe to required events.
        Routine must invoke in BWPersonality module.
        """
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
        g_playerEvents.onBootcampShowGUI += self.pe_onBootcampShowGUI
        return

    def fini(self):
        """
        Loader finalizes work: unsubscribe from events, removes prebattle dispatcher.
        Routine must invoke in BWPersonality module.
        """
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
        g_playerEvents.onBootcampShowGUI -= self.pe_onBootcampShowGUI
        return

    def getDispatcher(self):
        """
        Gets prebattle dispatcher.
        Returns:
            prebattle dispatcher or None. Returns None when
            player come to battle or login page.
        """
        return self.__prbDispatcher

    def getInvitesManager(self):
        """
        Gets manager for prebattle invites.
        Returns:
            invites manager
        """
        return self.__invitesManager

    def getAutoInvitesNotifier(self):
        """
        Gets notifier for auto invites.
        Returns:
            auto notifier
        """
        return self.__autoNotifier

    def getPeripheriesHandler(self):
        """
        Gets notifier for auto invites.
        Returns:
            peripheries handler
        """
        return self.__peripheriesHandler

    def getStorage(self):
        """
        Gets storage decorator to hold local client settings.
        Returns:
            storage
        """
        return self.__storage

    def isEnabled(self):
        """
        Is dispatcher enabled.
        Returns:
            obvious one - is dispatcher enabled.
        """
        return self.__isEnabled

    def setEnabled(self, enabled):
        """
        Sets dispatcher enabled.
        Args:
            enabled: new state
        """
        if self.__isEnabled ^ enabled:
            self.__isEnabled = enabled
            if self.__isEnabled and self.__prbDispatcher is not None:
                self.__doStart()
        return

    def onAccountShowGUI(self, ctx):
        """
        Listener for player event - show gui. Initializes dispatcher if needed.
        Args:
            ctx: gui init context
        """
        if self.__prbDispatcher is None:
            self.__prbDispatcher = _PreBattleDispatcher()
        if self.__isEnabled:
            self.__doStart()
        return

    def onAccountBecomeNonPlayer(self):
        """
        Listener for player event - on become non player. Deletes dispatcher.
        """
        self.__isEnabled = False
        self.__removeDispatcher()

    def onAvatarBecomePlayer(self):
        """
        Listener for player event - on become avatar. Deletes dispatcher.
        """
        self.__isEnabled = False
        self.__removeDispatcher()
        self.__invitesManager.onAvatarBecomePlayer()
        self.__storage.onAvatarBecomePlayer()

    def onDisconnected(self):
        """
        Listener for connection manager event - on disconnected. Deletes dispatcher
        and clears all related data.
        """
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
        """
        Do all the job related to loader statr.
        """
        self.__storage.swap()
        self.__prbDispatcher.start()
        self.__invitesManager.start()
        self.__autoNotifier.start()
        self.__peripheriesHandler.activate()

    def __removeDispatcher(self):
        """
        Removes prebattle dispatcher.
        """
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.stop()
            self.__prbDispatcher = None
        return

    def pe_onBootcampShowGUI(self, prbEnable):
        self.onAccountShowGUI({})
        if prbEnable:
            self.setEnabled(True)


g_prbLoader = _PrbControlLoader()
