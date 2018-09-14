# Embedded file name: scripts/client/gui/prb_control/dispatcher.py
from functools import partial
import types
import weakref
import BigWorld
from CurrentVehicle import g_currentVehicle
from adisp import async, process
from constants import IGR_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from FortifiedRegionBase import FORT_ERROR
from gui import SystemMessages, DialogsInterface, GUI_SETTINGS, game_control
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import functional, getClientPrebattle
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control import getClientUnitMgr
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.factories import ControlFactoryDecorator
from gui.prb_control.functional.battle_session import AutoInvitesNotifier
from gui.prb_control.functional.FunctionalCollection import FunctionalCollection
from gui.prb_control.invites import InvitesManager
from gui.prb_control.formatters import messages
from gui.prb_control.functional.interfaces import IGlobalListener
from gui.prb_control import areSpecBattlesHidden
from gui.prb_control.context import PrbCtrlRequestCtx, StartDispatcherCtx
from gui.prb_control.context import CreateFunctionalCtx
from gui.prb_control import isParentControlActivated, getClientUnitBrowser
from gui.prb_control.settings import PREBATTLE_RESTRICTION, FUNCTIONAL_EXIT, UNIT_MODE_FLAGS, PREBATTLE_ACTION_NAME
from gui.prb_control.settings import FUNCTIONAL_INIT_RESULT
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.prb_control.settings import IGNORED_UNIT_MGR_ERRORS
from gui.prb_control.settings import IGNORED_UNIT_BROWSER_ERRORS
from gui.prb_control.settings import RETURN_INTRO_UNIT_MGR_ERRORS
from PlayerEvents import g_playerEvents
from gui.shared import actions
from gui.shared.fortifications import getClientFortMgr

class _PrebattleDispatcher(object):

    def __init__(self):
        super(_PrebattleDispatcher, self).__init__()
        self.__requestCtx = None
        self.__collection = FunctionalCollection()
        self.__factories = ControlFactoryDecorator()
        self.__nextPrbFunctional = None
        self._globalListeners = set()
        return

    def __del__(self):
        LOG_DEBUG('_PrebattleDispatcher deleted')

    def start(self, ctx):
        g_eventDispatcher.init(self)
        self.__requestCtx = PrbCtrlRequestCtx()
        result = self.__factories.start(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.UNKNOWN, create={'queueType': ctx.getQueueType(),
         'settings': ctx.prbSettings}))
        self._startListening()
        functional.initDevFunctional()
        if result & FUNCTIONAL_INIT_RESULT.LOAD_PAGE == 0:
            BigWorld.callback(0.001, lambda : g_eventDispatcher.loadHangar())
        g_eventDispatcher.updateUI()
        if GUI_SETTINGS.specPrebatlesVisible and not areSpecBattlesHidden():
            g_eventDispatcher.addSpecBattlesToCarousel()

    def stop(self):
        self.__nextPrbFunctional = None
        self._stopListening()
        functional.finiDevFunctional()
        self._clear(woEvents=True)
        g_eventDispatcher.fini()
        return

    def getPrbFunctional(self):
        return self.__collection.getItem(CTRL_ENTITY_TYPE.PREBATTLE)

    def getUnitFunctional(self):
        return self.__collection.getItem(CTRL_ENTITY_TYPE.UNIT)

    def getPreQueueFunctional(self):
        return self.__collection.getItem(CTRL_ENTITY_TYPE.PREQUEUE)

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
    def create(self, ctx, callback = None):
        if ctx.getRequestType() == REQUEST_TYPE.CREATE:
            if not self.__requestCtx.isProcessing():
                result = yield self.unlock(ctx.getFuncExit(), True)
                if result:
                    entry = self.__factories.createEntry(ctx)
                    if entry:
                        LOG_DEBUG('Request to create', ctx)
                        self.__requestCtx = ctx
                        entry.create(ctx, callback=callback)
                    else:
                        LOG_ERROR('Entry not found', ctx)
                        if callback:
                            callback(False)
                elif callback:
                    callback(False)
            else:
                LOG_ERROR('Request is processing', self.__requestCtx)
                if callback:
                    callback(False)
                yield lambda callback = None: callback
        else:
            LOG_ERROR('Invalid context to create', ctx)
            if callback:
                callback(False)
            yield lambda callback = None: callback
        return

    @async
    @process
    def join(self, ctx, callback = None):
        if self._validateJoinOp(ctx):
            result = yield self.unlock(ctx.getFuncExit(), ctx.isForced())
            ctx.setForced(result)
            if result:
                entry = self.__factories.createEntry(ctx)
                if entry:
                    LOG_DEBUG('Request to join', ctx)
                    self.__requestCtx = ctx
                    entry.join(ctx, callback=callback)
                else:
                    LOG_ERROR('Entry not found', ctx)
                    if callback:
                        callback(False)
        else:
            if callback:
                callback(False)
            yield lambda callback = None: callback
        return

    @async
    def leave(self, ctx, callback = None):
        if ctx.getRequestType() is not REQUEST_TYPE.LEAVE:
            LOG_ERROR('Invalid context to leave prebattle/unit', ctx)
            if callback:
                callback(False)
            return
        elif self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            if callback:
                callback(False)
            return
        else:
            ctrlType = ctx.getCtrlType()
            formation = self.__collection.getItem(ctx.getCtrlType())
            if formation is not None:
                if formation.hasLockedState():
                    if ctrlType == CTRL_ENTITY_TYPE.PREQUEUE:
                        entityType = formation.getQueueType()
                    else:
                        entityType = formation.getPrbType()
                    SystemMessages.pushI18nMessage('#system_messages:{0}'.format(rally_dialog_meta.makeI18nKey(ctrlType, entityType, 'leaveDisabled')), type=SystemMessages.SM_TYPE.Warning)
                    if callback:
                        callback(False)
                    return
                LOG_DEBUG('Request to leave formation', ctx)
                self.__requestCtx = ctx
                formation.leave(ctx, callback=callback)
            else:
                LOG_ERROR('Functional not found', ctx)
                if callback:
                    callback(False)
            return

    @async
    @process
    def unlock(self, funcExit, forced, callback = None):
        state = self.getFunctionalState()
        result = True
        if state.hasModalEntity and (not state.isIntroMode or forced):
            factory = self.__factories.get(state.ctrlTypeID)
            result = False
            if factory:
                ctx = factory.createLeaveCtx(funcExit)
                if ctx:
                    meta = self.__collection.getItem(state.ctrlTypeID).getConfirmDialogMeta(funcExit)
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
        if callback:
            callback(result)
        yield lambda callback = None: callback
        return

    @async
    @process
    def select(self, entry, callback = None):
        ctx = entry.makeDefCtx()
        if ctx and self._validateJoinOp(ctx):
            result = yield self.unlock(ctx.getFuncExit(), True)
            ctx.setForced(result)
            if result:
                LOG_DEBUG('Request to select', ctx)
                self.__requestCtx = ctx
                entry.select(ctx, callback=callback)
            elif callback:
                callback(False)
        else:
            if callback:
                callback(False)
            yield lambda callback = None: callback
        return

    @async
    def sendPrbRequest(self, ctx, callback = None):
        prbFunctional = self.getFunctional(CTRL_ENTITY_TYPE.PREBATTLE)
        if prbFunctional:
            prbFunctional.request(ctx, callback=callback)
        else:
            LOG_ERROR('prbFunctional is not found', ctx)
            if callback:
                callback(False)

    @async
    def sendUnitRequest(self, ctx, callback = None):
        unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
        if unitFunctional:
            unitFunctional.request(ctx, callback=callback)
        else:
            LOG_ERROR('unitFunctional is not found', ctx)
            if callback:
                callback(False)

    def exitFromQueue(self):
        self.__collection.exitFromQueue()

    def canPlayerDoAction(self):
        canDo, restriction = self.__collection.canPlayerDoAction(False)
        if canDo:
            if not g_currentVehicle.isReadyToFight():
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
                elif not g_currentVehicle.isGroupReady():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_GROUP_IS_NOT_READY
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

    def doAction(self, action):
        if not g_currentVehicle.isPresent():
            SystemMessages.pushMessage(messages.getInvalidVehicleMessage(PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT), type=SystemMessages.SM_TYPE.Error)
            return False
        LOG_DEBUG('Do GUI action', action)
        return self.__collection.doAction(self, action, self.__factories)

    def doSelectAction(self, action):
        result = self.__collection.doSelectAction(action)
        if result:
            return True
        if action.actionName == PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE:
            self._doUnlock()
            return True
        entry = self.__factories.createEntryByAction(action.actionName)
        if entry:
            self._doSelect(entry)
            result = True
        return result

    def doLeaveAction(self, ctx):
        formation = self.__collection.getItem(ctx.getCtrlType())
        if formation:
            LOG_DEBUG('Request to leave', ctx)
            formation.doLeaveAction(self, ctx=ctx)
        else:
            LOG_ERROR('Functional is not found.', ctx)

    def addGlobalListener(self, listener):
        if isinstance(listener, IGlobalListener):
            listenerRef = weakref.ref(listener)
            if listenerRef not in self._globalListeners:
                self._globalListeners.add(listenerRef)
                self.__collection.addListener(listener)
            else:
                LOG_ERROR('Listener already added', listener)
        else:
            LOG_ERROR('Object is not extend IPrbListener', listener)

    def removeGlobalListener(self, listener):
        listenerRef = weakref.ref(listener)
        if listenerRef in self._globalListeners:
            self._globalListeners.remove(listenerRef)
        else:
            LOG_ERROR('Listener not found', listener)
        self.__collection.removeListener(listener)

    def getGUIPermissions(self):
        return self.__collection.getGUIPermissions()

    def _startListening(self):
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
        captchaCtrl = game_control.g_instance.captcha
        rentCtr = game_control.g_instance.rentals
        igrCtr = game_control.g_instance.igr
        if gameSession.lastBanMsg is not None:
            self.gs_onTillBanNotification(*gameSession.lastBanMsg)
        gameSession.onTimeTillBan += self.gs_onTillBanNotification
        rentCtr.onRentChangeNotify += self.rc_onRentChange
        captchaCtrl.onCaptchaInputCanceled += self.captcha_onCaptchaInputCanceled
        igrCtr.onIgrTypeChanged += self.igr_onRoomChange
        unitMgr = getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft += self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored += self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived += self.unitMgr_onUnitErrorReceived
        else:
            LOG_ERROR('Unit manager is not defined')
        unitBrowser = getClientUnitBrowser()
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
        return

    def _stopListening(self):
        """
        Unsubscribe from player events.
        """
        g_playerEvents.onPrebattleJoined -= self.pe_onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure -= self.pe_onPrebattleJoinFailure
        g_playerEvents.onPrebattleLeft -= self.pe_onPrebattleLeft
        g_playerEvents.onKickedFromPrebattle -= self.pe_onKickedFromPrebattle
        g_playerEvents.onArenaJoinFailure -= self.pe_onArenaJoinFailure
        g_playerEvents.onKickedFromArena -= self.pe_onKickedFromArena
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.pe_onPrebattleAutoInvitesChanged
        game_control.g_instance.captcha.onCaptchaInputCanceled -= self.captcha_onCaptchaInputCanceled
        game_control.g_instance.gameSession.onTimeTillBan -= self.gs_onTillBanNotification
        game_control.g_instance.rentals.onRentChangeNotify -= self.rc_onRentChange
        game_control.g_instance.igr.onIgrTypeChanged -= self.igr_onRoomChange
        unitMgr = getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft -= self.unitMgr_onUnitLeft
            unitMgr.onUnitRestored -= self.unitMgr_onUnitRestored
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        unitBrowser = getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived -= self.unitBrowser_onErrorReceived
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortResponseReceived -= self.fortMgr_onFortResponseReceived
            fortMgr.onFortStateChanged -= self.forMgr_onFortStateChanged
        g_prbCtrlEvents.clear()

    def _setRequestCtx(self, ctx):
        result = True
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            result = False
        else:
            self.__requestCtx = ctx
        return result

    def _clear(self, woEvents = False):
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
        self._globalListeners.clear()
        return

    def pe_onArenaJoinFailure(self, errorCode, _):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onKickedFromArena(self, reasonCode):
        self.__collection.reset()
        SystemMessages.pushMessage(messages.getKickReasonMessage(reasonCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onPrebattleAutoInvitesChanged(self):
        if GUI_SETTINGS.specPrebatlesVisible:
            isHidden = areSpecBattlesHidden()
            if isHidden:
                g_eventDispatcher.removeSpecBattlesFromCarousel()
            else:
                g_eventDispatcher.addSpecBattlesToCarousel()
        g_eventDispatcher.updateUI()

    def pe_onPrebattleJoined(self):
        clientPrb = getClientPrebattle()
        if clientPrb:
            prbFunctional = self.getFunctional(CTRL_ENTITY_TYPE.PREBATTLE)
            if prbFunctional:
                if self.__requestCtx and self.__requestCtx.getPrbType() == prbFunctional.getPrbType():
                    exit = FUNCTIONAL_EXIT.PREBATTLE
                else:
                    exit = FUNCTIONAL_EXIT.NO_FUNC
                prbFunctional.setExit(exit)
            else:
                LOG_ERROR('Prebattle functional is not found')
            self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREBATTLE))
        else:
            LOG_ERROR('ClientPrebattle is not defined')
            self.__requestCtx.stopProcessing(result=False)

    def pe_onPrebattleJoinFailure(self, errorCode):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)
        self.__requestCtx.stopProcessing(result=False)
        g_eventDispatcher.updateUI()

    def pe_onPrebattleLeft(self):
        if self.__nextPrbFunctional:
            self.__nextPrbFunctional()
            self.__nextPrbFunctional = None
            return
        else:
            prbFunctional = self.getFunctional(CTRL_ENTITY_TYPE.PREBATTLE)
            prbType = 0
            if prbFunctional and prbFunctional.getExit() not in [FUNCTIONAL_EXIT.NO_FUNC,
             FUNCTIONAL_EXIT.BATTLE_TUTORIAL,
             FUNCTIONAL_EXIT.RANDOM,
             FUNCTIONAL_EXIT.SWITCH,
             FUNCTIONAL_EXIT.SQUAD]:
                prbType = prbFunctional.getPrbType()
            self._changePrbFunctional(prbType=prbType, stop=False)
            return

    def pe_onKickedFromPrebattle(self, _):
        self._changePrbFunctional(funcExit=FUNCTIONAL_EXIT.NO_FUNC, stop=False)

    def gs_onTillBanNotification(self, isPlayTimeBan, timeTillBlock):
        if isParentControlActivated():
            self.__collection.reset()
            key = '#system_messages:gameSessionControl/korea/{0:>s}'
            if isPlayTimeBan:
                SystemMessages.g_instance.pushI18nMessage(key.format('playTimeNotification'), timeTillBlock, type=SystemMessages.SM_TYPE.Warning)
            else:
                SystemMessages.g_instance.pushI18nMessage(key.format('midnightNotification'), type=SystemMessages.SM_TYPE.Warning)

    def rc_onRentChange(self, vehicles):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.intCD in vehicles and g_currentVehicle.isDisabledInRent() and g_currentVehicle.isInPrebattle():
            self.__collection.reset()

    def igr_onRoomChange(self, roomType, _):
        if roomType != IGR_TYPE.PREMIUM:
            if g_currentVehicle.isPremiumIGR() and g_currentVehicle.isInPrebattle():
                self.__collection.reset()

    def captcha_onCaptchaInputCanceled(self):
        self.__requestCtx.stopProcessing(False)

    def ctrl_onPrebattleIntroModeJoined(self, prbType, isLeaving):
        if not isLeaving:
            self._changePrbFunctional(funcExit=FUNCTIONAL_EXIT.INTRO_PREBATTLE, prbType=prbType)
        else:
            self.__nextPrbFunctional = partial(self._changePrbFunctional, prbType=prbType)

    def ctrl_onPrebattleIntroModeLeft(self):
        self._changePrbFunctional()

    def ctrl_onPrebattleInited(self):
        self.__requestCtx.stopProcessing(result=True)
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREBATTLE, init={'ctx': self.__requestCtx}))
        g_eventDispatcher.updateUI()

    def ctrl_onUnitIntroModeJoined(self, prbType, modeFlags):
        self._changeUnitFunctional(funcExit=FUNCTIONAL_EXIT.INTRO_UNIT, prbType=prbType, modeFlags=modeFlags)

    def ctrl_onUnitIntroModeLeft(self):
        self._changeUnitFunctional()

    def ctrl_onPreQueueFunctionalCreated(self, queueType, doAction = False, action = None):
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREQUEUE, create={'queueType': queueType}))
        g_prbCtrlEvents.onPreQueueFunctionalChanged()
        if action and doAction:
            preQueueFunctional = self.getFunctional(CTRL_ENTITY_TYPE.PREQUEUE)
            if preQueueFunctional:
                preQueueFunctional.doAction(action, dispatcher=self)
            else:
                LOG_ERROR('PreQueue functional is not found')
        g_eventDispatcher.updateUI()

    def ctrl_onPreQueueFunctionalDestroyed(self):
        self.ctrl_onPreQueueFunctionalCreated(None)
        return

    def unitMgr_onUnitJoined(self, unitMgrID, unitIdx):
        unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
        if unitFunctional and unitFunctional.getID() == unitMgrID and unitFunctional.getUnitIdx() == unitIdx:
            unitFunctional.rejoin()
        else:
            self._changeUnitFunctional(funcExit=FUNCTIONAL_EXIT.UNIT)

    def unitMgr_onUnitLeft(self, unitMgrID, unitIdx):
        unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
        prbType = 0
        update = True
        if unitFunctional and unitFunctional.getExit() == FUNCTIONAL_EXIT.INTRO_UNIT:
            prbType = unitFunctional.getPrbType()
            update = False
        self._changeUnitFunctional(prbType=prbType)
        if update:
            g_eventDispatcher.updateUI()

    def unitMgr_onUnitRestored(self, unitMgrID, unitIdx):
        unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
        flags = unitFunctional.getFlags()
        pInfo = unitFunctional.getPlayerInfo()
        if flags.isInPreArena() and pInfo.isInSlot:
            g_eventDispatcher.loadHangar()

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, unitIdx, errorCode, errorString):
        unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
        if unitFunctional:
            unitFunctional.setLastError(errorCode)
        else:
            LOG_ERROR('Unit functional is not found')
        if errorCode not in IGNORED_UNIT_MGR_ERRORS:
            msgType, msgBody = messages.getUnitMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)
            if errorCode in RETURN_INTRO_UNIT_MGR_ERRORS and unitFunctional:
                unitFunctional.setExit(FUNCTIONAL_EXIT.INTRO_UNIT)
            self.__requestCtx.stopProcessing(result=False)
            g_eventDispatcher.updateUI()

    def unitBrowser_onErrorReceived(self, errorCode, errorString):
        if errorCode not in IGNORED_UNIT_BROWSER_ERRORS:
            msgType, msgBody = messages.getUnitBrowserMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)

    def forMgr_onFortStateChanged(self):
        g_eventDispatcher.updateUI()

    def fortMgr_onFortResponseReceived(self, requestID, resultCode, _):
        self.__requestCtx.stopProcessing(result=resultCode in (FORT_ERROR.OK,))
        g_eventDispatcher.updateUI()

    def _changePrbFunctional(self, funcExit = None, prbType = 0, stop = True):
        if funcExit is not None:
            prbFunctional = self.getFunctional(CTRL_ENTITY_TYPE.PREBATTLE)
            if prbFunctional:
                prbFunctional.setExit(funcExit)
            else:
                LOG_ERROR('Prebattle functional is not found')
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREBATTLE, prbType))
        if stop:
            self.__requestCtx.stopProcessing(result=True)
        return

    def _changeUnitFunctional(self, funcExit = None, prbType = 0, modeFlags = UNIT_MODE_FLAGS.UNDEFINED):
        if funcExit is not None:
            unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
            if unitFunctional:
                unitFunctional.setExit(funcExit)
            else:
                LOG_ERROR('Unit functional is not found')
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.UNIT, prbType, create={'modeFlags': modeFlags}, init={'ctx': self.__requestCtx}))
        self.__requestCtx.stopProcessing(result=True)
        return

    def _validateJoinOp(self, ctx):
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            return False
        for func in self.__collection.getIterator():
            if func.isPlayerJoined(ctx):
                LOG_DEBUG('Player already joined', ctx)
                func.showGUI()
                return False
            if func.hasLockedState():
                SystemMessages.pushI18nMessage('#system_messages:prebattle/hasLockedState', type=SystemMessages.SM_TYPE.Warning)
                return False

        return True

    @process
    def _doUnlock(self):
        yield self.unlock(FUNCTIONAL_EXIT.RANDOM, True)

    @process
    def _doSelect(self, entry):
        yield self.select(entry)


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

    def join(self, peripheryID, ctx, postActions = None, finishActions = None):
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
    __slots__ = ('__prbDispatcher', '__invitesManager', '__autoNotifier', '__peripheriesHandler', '__isEnabled', '__prbSettings')

    def __init__(self):
        super(_PrbControlLoader, self).__init__()
        self.__prbSettings = ({}, {})
        self.__prbDispatcher = None
        self.__invitesManager = None
        self.__autoNotifier = None
        self.__peripheriesHandler = None
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
        return

    def fini(self):
        self.__removeDispatcher()
        self.__clearPrbSettings()
        if self.__invitesManager is not None:
            self.__invitesManager.fini()
            self.__invitesManager = None
        if self.__autoNotifier is not None:
            self.__autoNotifier.fini()
            self.__autoNotifier = None
        if self.__peripheriesHandler is not None:
            self.__peripheriesHandler.fini()
            self.__peripheriesHandler = None
        return

    def getDispatcher(self):
        return self.__prbDispatcher

    def getInvitesManager(self):
        return self.__invitesManager

    def getAutoInvitesNotifier(self):
        return self.__autoNotifier

    def getPeripheriesHandler(self):
        return self.__peripheriesHandler

    def isEnabled(self):
        return self.__isEnabled

    def setEnabled(self, enabled):
        if self.__isEnabled ^ enabled:
            self.__isEnabled = enabled
            if self.__isEnabled and self.__prbDispatcher is not None:
                ctxUpdate, settings = self.__prbSettings
                self.__doStart(StartDispatcherCtx.fetch(prbSettings=settings, **ctxUpdate))
        return

    def onAccountShowGUI(self, ctx):
        if self.__prbDispatcher is None:
            self.__prbDispatcher = _PrebattleDispatcher()
        if self.__isEnabled:
            ctxUpdate, settings = self.__prbSettings
            ctx.update(ctxUpdate)
            self.__doStart(StartDispatcherCtx(prbSettings=settings, **ctx))
        return

    def onAvatarBecomePlayer(self):
        self.__isEnabled = False
        self.__savePrbSettings()
        self.__removeDispatcher()
        self.__invitesManager.onAvatarBecomePlayer()

    def onDisconnected(self):
        self.__isEnabled = False
        self.__removeDispatcher()
        self.__clearPrbSettings()
        self.__autoNotifier.stop()
        if self.__invitesManager is not None:
            self.__invitesManager.clear()
        if self.__autoNotifier is not None:
            self.__autoNotifier.stop()
        return

    def __doStart(self, ctx):
        self.__prbDispatcher.start(ctx)
        self.__invitesManager.start()
        self.__autoNotifier.start()
        self.__peripheriesHandler.activate()
        self.__clearPrbSettings()

    def __removeDispatcher(self):
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.stop()
            self.__prbDispatcher = None
        return

    def __savePrbSettings(self):
        if self.__prbDispatcher is not None:
            ctx, settings = self.__prbSettings
            for func in self.__prbDispatcher.getFunctionalCollection().getIterator():
                if functional.isStatefulFunctional(func):
                    funcCtx, funcStates = func.getStates()
                    ctx.update(funcCtx)
                    settings[func.getEntityType()] = funcStates

        return

    def __clearPrbSettings(self):
        self.__prbSettings = ({}, {})


g_prbLoader = _PrbControlLoader()
