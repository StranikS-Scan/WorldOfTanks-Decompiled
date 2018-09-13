# Embedded file name: scripts/client/gui/prb_control/dispatcher.py
import types
import weakref
import BigWorld
from CurrentVehicle import g_currentVehicle
from adisp import async, process
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, DialogsInterface, GUI_SETTINGS, game_control
from gui.LobbyContext import g_lobbyContext
from gui.prb_control import functional, events_dispatcher, getClientPrebattle
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
from gui.prb_control.settings import PREBATTLE_RESTRICTION, FUNCTIONAL_EXIT, UNIT_MODE_FLAGS
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
        self._globalListeners = set()
        return

    def __del__(self):
        LOG_DEBUG('_PrebattleDispatcher deleted')

    def start(self, ctx):
        self.__requestCtx = PrbCtrlRequestCtx()
        result = self.__factories.start(self, CreateFunctionalCtx(create={'queueType': ctx.getQueueType(),
         'settings': ctx.preQueueStates}))
        self._startListening()
        functional.initDevFunctional()
        if result & FUNCTIONAL_INIT_RESULT.LOAD_PAGE == 0:
            BigWorld.callback(0.001, lambda : events_dispatcher.loadHangar())
        events_dispatcher.updateUI()
        events_dispatcher.addCompaniesToCarousel()
        if GUI_SETTINGS.specPrebatlesVisible and not areSpecBattlesHidden():
            events_dispatcher.addSpecBattlesToCarousel()

    def stop(self):
        self._stopListening()
        functional.finiDevFunctional()
        self._clear(woEvents=True)

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
        if ctx.getRequestType() is not REQUEST_TYPE.CREATE:
            LOG_ERROR('Invalid context to create prebattle/unit', ctx)
            if callback:
                callback(False)
        elif not self.__requestCtx.isProcessing():
            result = True
            for func, leaveCtx in self.__collection.getIteratorToLeave(self.__factories):
                if func.isConfirmToChange(exit=ctx.getFuncExit()):
                    result = yield DialogsInterface.showDialog(func.getConfirmDialogMeta(True))
                    if result:
                        result = yield self.leave(leaveCtx)
                        ctx.setForced(result)

            if result:
                entry = self.__factories.createEntry(ctx)
                if entry:
                    LOG_DEBUG('Request to create prebattle/unit', ctx)
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
        return

    @async
    @process
    def join(self, ctx, callback = None):
        if not self.__requestCtx.isProcessing():
            result = True
            for func in self.__collection.getIterator():
                if func.isPlayerJoined(ctx):
                    LOG_DEBUG('Player already joined', ctx)
                    func.showGUI()
                    result = False
                    break
                if func.hasLockedState():
                    SystemMessages.pushI18nMessage('#system_messages:prebattle/hasLockedState', type=SystemMessages.SM_TYPE.Warning)
                    result = False
                    break

            if result:
                for func, leaveCtx in self.__collection.getIteratorToLeave(self.__factories):
                    if func.isConfirmToChange(exit=ctx.getFuncExit()):
                        result = yield DialogsInterface.showDialog(func.getConfirmDialogMeta(True))
                        if result:
                            result = yield self.leave(leaveCtx)
                            ctx.setForced(result)

                if result:
                    entry = self.__factories.createEntry(ctx)
                    if entry:
                        LOG_DEBUG('Request to join prebattle/unit', ctx)
                        self.__requestCtx = ctx
                        entry.join(ctx, callback=callback)
                    else:
                        LOG_ERROR('Entry not found', ctx)
                        if callback:
                            callback(False)
                elif callback:
                    callback(False)
            elif callback:
                callback(False)
        else:
            LOG_ERROR('Request is processing', self.__requestCtx)
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
            formation = self.__collection.getItem(ctx.getEntityType())
            if formation is not None:
                if formation.hasLockedState():
                    LOG_ERROR('Player can not leave formation', ctx)
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
                elif g_currentVehicle.isDisabledInRoaming():
                    canDo = False
                    restriction = PREBATTLE_RESTRICTION.VEHICLE_ROAMING
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
        actionName = action.actionName
        result = False
        for factory in self.__factories.getIterator():
            ctx = factory.getLeaveCtxByAction(actionName)
            if ctx:
                self.doLeaveAction(ctx)
                result = True
                break
            ctx = factory.getOpenListCtxByAction(actionName)
            if ctx:
                entry = factory.createEntry(ctx)
                if entry:
                    entry.doAction(action, dispatcher=self)
                result = True
                break

        if not result:
            result = self.__collection.doAction(self, action, self.__factories)
        return result

    def doLeaveAction(self, ctx):
        formation = self.__collection.getItem(ctx.getEntityType())
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
        if gameSession.lastBanMsg is not None:
            self.gs_onTillBanNotification(*gameSession.lastBanMsg)
        gameSession.onTimeTillBan += self.gs_onTillBanNotification
        captchaCtrl.onCaptchaInputCanceled += self.captcha_onCaptchaInputCanceled
        unitMgr = getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft += self.unitMgr_onUnitLeft
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
        else:
            LOG_ERROR('Fort manager is not defined')
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
        unitMgr = getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.unitMgr_onUnitJoined
            unitMgr.onUnitLeft -= self.unitMgr_onUnitLeft
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        unitBrowser = getClientUnitBrowser()
        if unitBrowser:
            unitBrowser.onErrorReceived -= self.unitBrowser_onErrorReceived
        fortMgr = getClientFortMgr()
        if fortMgr:
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
        events_dispatcher.removeSpecBattlesFromCarousel()
        self._globalListeners.clear()
        return

    def pe_onArenaJoinFailure(self, errorCode, _):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def pe_onKickedFromArena(self, reasonCode):
        self.__collection.reset()

    def pe_onPrebattleAutoInvitesChanged(self):
        if GUI_SETTINGS.specPrebatlesVisible:
            isHidden = areSpecBattlesHidden()
            if isHidden:
                events_dispatcher.removeSpecBattlesFromCarousel()
            else:
                events_dispatcher.addSpecBattlesToCarousel()
        events_dispatcher.updateUI()

    def pe_onPrebattleJoined(self):
        clientPrb = getClientPrebattle()
        if clientPrb:
            self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREBATTLE))
        else:
            LOG_ERROR('ClientPrebattle is not defined')
            self.__requestCtx.stopProcessing(result=False)

    def pe_onPrebattleJoinFailure(self, errorCode):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)
        self.__requestCtx.stopProcessing(result=False)
        events_dispatcher.updateUI()

    def pe_onPrebattleLeft(self):
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREBATTLE))
        events_dispatcher.updateUI()

    def pe_onKickedFromPrebattle(self, _):
        self.pe_onPrebattleLeft()

    def gs_onTillBanNotification(self, isPlayTimeBan, timeTillBlock):
        if isParentControlActivated():
            self.__collection.reset()
            key = '#system_messages:gameSessionControl/korea/{0:>s}'
            if isPlayTimeBan:
                SystemMessages.g_instance.pushI18nMessage(key.format('playTimeNotification'), timeTillBlock, type=SystemMessages.SM_TYPE.Warning)
            else:
                SystemMessages.g_instance.pushI18nMessage(key.format('midnightNotification'), type=SystemMessages.SM_TYPE.Warning)

    def captcha_onCaptchaInputCanceled(self):
        self.__requestCtx.stopProcessing(False)

    def ctrl_onPrebattleInited(self):
        self.__requestCtx.stopProcessing(result=True)
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.PREBATTLE, init={'ctx': self.__requestCtx}))
        events_dispatcher.updateUI()

    def _changeUnitFunctional(self, exit = None, prbType = None, modeFlags = UNIT_MODE_FLAGS.UNDEFINED):
        if exit is not None:
            unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
            if unitFunctional:
                unitFunctional.setExit(exit)
            else:
                LOG_ERROR('Unit functional is not found')
        self.__factories.createFunctional(self, CreateFunctionalCtx(CTRL_ENTITY_TYPE.UNIT, create={'prbType': prbType,
         'modeFlags': modeFlags}))
        self.__requestCtx.stopProcessing(result=True)
        events_dispatcher.updateUI()
        return

    def ctrl_onUnitIntroModeJoined(self, prbType, modeFlags):
        self._changeUnitFunctional(exit=FUNCTIONAL_EXIT.INTRO_UNIT, prbType=prbType, modeFlags=modeFlags)

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
        events_dispatcher.updateUI()

    def ctrl_onPreQueueFunctionalDestroyed(self):
        self.ctrl_onPreQueueFunctionalCreated(None)
        return

    def unitMgr_onUnitJoined(self, unitMgrID, unitIdx):
        unitFunctional = self.getFunctional(CTRL_ENTITY_TYPE.UNIT)
        if unitFunctional and unitFunctional.getID() == unitMgrID and unitFunctional.getUnitIdx() == unitIdx:
            unitFunctional.rejoin()
        else:
            self._changeUnitFunctional(exit=FUNCTIONAL_EXIT.UNIT)

    def unitMgr_onUnitLeft(self, unitMgrID, unitIdx):
        self._changeUnitFunctional()

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
            events_dispatcher.updateUI()

    def unitBrowser_onErrorReceived(self, errorCode, errorString):
        if errorCode not in IGNORED_UNIT_BROWSER_ERRORS:
            msgType, msgBody = messages.getUnitBrowserMessage(errorCode, errorString)
            SystemMessages.pushMessage(msgBody, type=msgType)

    def forMgr_onFortStateChanged(self):
        events_dispatcher.updateUI()


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
    __slots__ = ('__prbDispatcher', '__invitesManager', '__autoNotifier', '__peripheriesHandler', '__isEnabled', '__preQueueStates')

    def __init__(self):
        super(_PrbControlLoader, self).__init__()
        self.__preQueueStates = ({}, None)
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
        self.__clearPreQueueStates()
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
                ctxUpdate, states = self.__preQueueStates
                self.__doStart(StartDispatcherCtx.fetch(preQueueStates=states, **ctxUpdate))
        return

    def onAccountShowGUI(self, ctx):
        if self.__prbDispatcher is None:
            self.__prbDispatcher = _PrebattleDispatcher()
        self.__invitesManager.onAccountShowGUI()
        if self.__isEnabled:
            ctxUpdate, states = self.__preQueueStates
            ctx.update(ctxUpdate)
            self.__doStart(StartDispatcherCtx(preQueueStates=states, **ctx))
        return

    def onAvatarBecomePlayer(self):
        self.__isEnabled = False
        self.__savePreQueueStates()
        self.__removeDispatcher()
        self.__invitesManager.onAvatarBecomePlayer()

    def onDisconnected(self):
        self.__isEnabled = False
        self.__removeDispatcher()
        self.__clearPreQueueStates()
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
        self.__clearPreQueueStates()

    def __removeDispatcher(self):
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.stop()
            self.__prbDispatcher = None
        return

    def __savePreQueueStates(self):
        if self.__prbDispatcher is not None:
            preQueue = self.__prbDispatcher.getPreQueueFunctional()
            if preQueue is not None:
                isPersistent, ctx, settings = preQueue.getStates()
                if isPersistent:
                    self.__preQueueStates = (ctx, settings)
        return

    def __clearPreQueueStates(self):
        self.__preQueueStates = ({}, None)
        return


g_prbLoader = _PrbControlLoader()
