# Embedded file name: scripts/client/gui/shared/fortifications/fort_provider.py
import weakref
from FortifiedRegionBase import FORT_ERROR, FORT_ERROR_NAMES
from PlayerEvents import g_playerEvents
from adisp import async, process
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SM
from gui.shared.fortifications import controls, states, getClientFortMgr, getClanFortState
from gui.shared.fortifications.fort_ext import FortSubscriptionKeeper
from gui.shared.fortifications.interfaces import IFortListener
from gui.shared.fortifications.settings import FORT_PROVIDER_INITIAL_FLAGS, CLIENT_FORT_STATE
from gui.shared.utils.ListenersCollection import ListenersCollection
from helpers import i18n

class _ClientFortListeners(ListenersCollection):

    def __init__(self):
        super(_ClientFortListeners, self).__init__()
        self._setListenerClass(IFortListener)

    def isEmpty(self):
        return not len(self._listeners)

    def notify(self, eventType, *args):
        self._invokeListeners(eventType, *args)

    def clear(self):
        while len(self._listeners):
            self._listeners.pop()


def getFortErrorMessage(errorCode, errorString):
    if errorCode in FORT_ERROR_NAMES:
        errorName = FORT_ERROR_NAMES[errorCode]
        i18nKey = I18N_SM.fortification_errors(FORT_ERROR_NAMES[errorCode])
    else:
        errorName = str(errorCode)
        i18nKey = I18N_SM.FORTIFICATION_ERRORS_UNKNOWN
    if i18nKey is not None:
        msg = i18n.makeString(i18nKey)
    else:
        msg = errorName + '\n' + errorString
    return msg


class ClientFortProvider(object):

    def __init__(self):
        super(ClientFortProvider, self).__init__()
        self.__clan = None
        self.__state = None
        self.__controller = None
        self.__listeners = None
        self.__keeper = None
        self.__initial = 0
        self.__lock = False
        return

    def __del__(self):
        LOG_DEBUG('Fort provider deleted:', self)

    def getClanCache(self):
        return self.__clan

    def getState(self):
        return self.__state

    def getController(self):
        return self.__controller

    def isStarted(self):
        return self.__initial & FORT_PROVIDER_INITIAL_FLAGS.STARTED > 0

    def isSubscribed(self):
        return self.__initial & FORT_PROVIDER_INITIAL_FLAGS.SUBSCRIBED > 0

    def clear(self):
        self.__clan = None
        self.__state = None
        self.__lock = False
        if self.__keeper:
            self.__keeper.onAutoUnsubscribed -= self.__onAutoUnsubscribed
            self.__keeper.stop()
            self.__keeper = None
        if self.__controller:
            self.__controller.fini()
            self.__controller = None
        if self.__listeners:
            self.__listeners.clear()
            self.__listeners = None
        return

    def start(self, clanCache):
        if self.isStarted():
            LOG_WARNING('Fort provider already is ready')
            return
        self.__initial |= FORT_PROVIDER_INITIAL_FLAGS.STARTED
        self.__clan = weakref.proxy(clanCache)
        self.__listeners = _ClientFortListeners()
        self.__keeper = FortSubscriptionKeeper()
        self.__keeper.onAutoUnsubscribed += self.__onAutoUnsubscribed
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortResponseReceived += self.__onFortResponseReceived
            fortMgr.onFortUpdateReceived += self.__onFortUpdateReceived
            fortMgr.onFortStateChanged += self.__onFortStateChanged
        else:
            LOG_ERROR('Fort manager is not found')
        g_playerEvents.onCenterIsLongDisconnected += self.__onCenterIsLongDisconnected
        self.__controller = controls.createInitial()
        self.__controller.init(self.__clan, self.__listeners)
        states.create(self)

    def stop(self):
        if not self.isStarted():
            LOG_DEBUG('Fort provider already is stopped')
            return
        self.__initial = 0
        self.clear()
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortResponseReceived -= self.__onFortResponseReceived
            fortMgr.onFortUpdateReceived -= self.__onFortUpdateReceived
            fortMgr.onFortStateChanged -= self.__onFortStateChanged
        g_playerEvents.onCenterIsLongDisconnected -= self.__onCenterIsLongDisconnected

    @async
    def sendRequest(self, ctx, callback = None):
        isSubscribed = self.isSubscribed()
        if isSubscribed or not self.__keeper.isEnabled():
            if not isSubscribed:
                ctx._setUpdateExpected(False)
            self.__controller.request(ctx, callback=callback)
        else:
            LOG_WARNING('Fort provider is not subscribed', ctx)
            if callback:
                callback(False)

    def addListener(self, listener):
        self.__listeners.addListener(listener)
        self.__resolveSubscription()

    def removeListener(self, listener):
        if self.__listeners:
            self.__listeners.removeListener(listener)
        self.__resolveSubscription()

    def notify(self, eventType, *args):
        if self.__listeners:
            self.__listeners.notify(eventType, *args)
        else:
            LOG_WARNING('Listeners collection is deleted', eventType)

    def updateState(self):
        if self.isStarted():
            self.__state.update(self)
        else:
            LOG_WARNING('Fort provider is not started')

    def resetState(self):
        if self.isStarted():
            states.create(self)
        else:
            LOG_WARNING('Fort provider is not started')

    def changeState(self, state):
        stateID = state.getStateID()
        if not self.isStarted():
            LOG_WARNING('Fort provider is not started')
            return
        if self.__state and stateID == self.__state.getStateID():
            LOG_DEBUG('Fort state is already set. It is ignored', state)
            return
        self.__state = state
        LOG_DEBUG('Fort state has been changed', state)
        controller = controls.createByState(state, self.__controller.getPermissions().canCreate(), self.__controller.__class__)
        if controller:
            controller.init(self.__clan, self.__listeners, self.__controller)
            self.__controller.fini(self.__state.getStateID() != CLIENT_FORT_STATE.CENTER_UNAVAILABLE)
            self.__controller = controller
            LOG_DEBUG('Fort controller has been changed', controller)
        self.__listeners.notify('onClientStateChanged', state)
        self.__resolveSubscription()

    @process
    def __resolveSubscription(self):
        if not self.isStarted() or self.__lock:
            return
        else:
            isSubscribed = self.isSubscribed()
            if self.__listeners.isEmpty():
                if isSubscribed:
                    if self.__state is not None and self.__state.getStateID() != CLIENT_FORT_STATE.NO_CLAN:
                        self.__lock = True
                        unsubscribed = yield self.__requestUnsubscribe()
                        self.__lock = False
                    else:
                        unsubscribed = True
                        yield lambda callback: callback(True)
                    if unsubscribed:
                        self.__initial ^= FORT_PROVIDER_INITIAL_FLAGS.SUBSCRIBED
                        if self.__keeper:
                            self.__keeper.stop()
                        self.resetState()
            else:
                if self.__state:
                    stateID = self.__state.getStateID()
                else:
                    stateID = CLIENT_FORT_STATE.UNKNOWN
                if not isSubscribed and stateID in CLIENT_FORT_STATE.NEED_SUBSCRIPTION:
                    self.__lock = True
                    result = yield self.__requestSubscribe()
                    self.__lock = False
                    if result:
                        self.__keeper.start(stateID)
                        self.__initial |= FORT_PROVIDER_INITIAL_FLAGS.SUBSCRIBED
                else:
                    self.__keeper.update(stateID)
            return

    @async
    def __requestSubscribe(self, callback = None):
        self.__controller.subscribe(callback)

    @async
    def __requestUnsubscribe(self, callback = None):
        self.__controller.unsubscribe(callback)

    def __onFortResponseReceived(self, _, resultCode, resultString):
        if resultCode != FORT_ERROR.OK:
            SystemMessages.pushMessage(getFortErrorMessage(resultCode, resultString), type=SystemMessages.SM_TYPE.Error)

    def __onFortUpdateReceived(self, isFullUpdate = False):
        self.updateState()
        self.__listeners.notify('onUpdated', isFullUpdate)

    def __onFortStateChanged(self):
        if getClanFortState() is None:
            self.resetState()
        else:
            self.updateState()
        return

    def __onAutoUnsubscribed(self):
        if self.isSubscribed() and not self.__lock:
            self.__initial ^= FORT_PROVIDER_INITIAL_FLAGS.SUBSCRIBED

    def __onCenterIsLongDisconnected(self, _):
        self.__controller.stopProcessing()
        self.resetState()
