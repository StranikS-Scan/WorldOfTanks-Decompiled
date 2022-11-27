# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/shop_sales_event_controller.py
import logging
import sys
from datetime import datetime
from functools import partial
import typing
from Event import Event, EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SHOP_SALES_EVENT_STATE
from adisp import adisp_process, adisp_async
from constants import EventPhase, SHOP_SALES_CONFIG
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar, showShop
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.shop_sales import ShopSalesEventGetCurrentBundleProcessor, ShopSalesEventReRollProcessor
from gui.shared.money import Money
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.shop import Origin
from gui.wgcg.shop_sales_event.contexts import ShopSalesEventFetchFavoritesCtx
from helpers import dependency, server_settings
from helpers.time_utils import getServerUTCTime
from messenger.proto.events import g_messengerEvents
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IShopSalesEventController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.shop_sales.main_view import ShopSalesMainView
_logger = logging.getLogger(__name__)
_SECONDS_BEFORE_UPDATE = 2

class _EventStatusSystemChanelNotifier(object):
    __ctrl = dependency.descriptor(IShopSalesEventController)

    def __init__(self):
        self.__msgRes = R.strings.messenger.serviceChannelMessages.shopSalesEvent
        self.__prevEnabled = self.__ctrl.isEnabled

    def init(self):
        self.__ctrl.onStateChanged += self.__onStateChanged
        self.__ctrl.onPhaseChanged += self.__onPhaseChanged
        self.__ctrl.onPhaseChanged += self.__onStateEnabledReset

    def fini(self):
        self.__ctrl.onPhaseChanged -= self.__onStateEnabledReset
        self.__ctrl.onPhaseChanged -= self.__onPhaseChanged
        self.__ctrl.onStateChanged -= self.__onStateChanged

    def __onStateEnabledReset(self):
        self.__prevEnabled = True

    def __onStateChanged(self):
        if self.__prevEnabled != self.__ctrl.isEnabled:
            if not self.__ctrl.isEnabled and self.__ctrl.isInEvent:
                self.__ctrl.closeMainView()
            pushDisabledWarning = self.__ctrl.currentEventPhase != EventPhase.NOT_STARTED and self.__ctrl.isInEvent
            if pushDisabledWarning:
                self.__pushStateMessage()
            self.__prevEnabled = self.__ctrl.isEnabled

    def __onPhaseChanged(self):
        self.__pushPhaseMessage()

    def __pushStateMessage(self):
        msgRes, msgType = self.__getStateMessageData()
        SystemMessages.pushMessage(self.__formatMessage(msgRes()), msgType)

    def __pushPhaseMessage(self):
        msgRes, msgType = self.__getPhaseMessageData()
        if msgRes.exists() and msgType is not None:
            SystemMessages.pushMessage(self.__formatMessage(msgRes()), msgType)
        return

    def __getStateMessageData(self):
        return (self.__msgRes.enabledBySwitch, SM_TYPE.EventWarningWithButton) if self.__ctrl.isEnabled else (self.__msgRes.disabledBySwitch, SM_TYPE.EventError)

    def __getPhaseMessageData(self):
        if self.__ctrl.currentEventPhase == EventPhase.IN_PROGRESS:
            return (self.__msgRes.activePhaseStarted, SM_TYPE.EventInfoWithButton)
        elif self.__ctrl.currentEventPhase == EventPhase.FINISHED:
            return (self.__msgRes.activePhaseFinished, SM_TYPE.EventInfoWithButton)
        else:
            return (self.__msgRes.eventFinished, SM_TYPE.EventInfo) if not self.__ctrl.isInEvent else (R.invalid, None)

    def __formatMessage(self, messageId):
        if messageId == self.__msgRes.activePhaseFinished():
            _, phaseEndTs = self.__ctrl.currentEventPhaseTimeRange
            phaseEndDate = datetime.fromtimestamp(phaseEndTs)
            datetimeRes = R.strings.menu.dateTime
            phaseEndDateStr = text_styles.stats(backport.text(datetimeRes.orderWithoutYear(), day=phaseEndDate.day, month=backport.text(datetimeRes.months.num(phaseEndDate.month)()), time=phaseEndDate.strftime(backport.text(datetimeRes.timeFormat()))))
        else:
            phaseEndDateStr = ''
        return backport.text(messageId, date=phaseEndDateStr)


class _Notifiable(Notifiable):

    def updateNotifiers(self, *notifiers):
        self.clearNotification()
        self.addNotificators(*notifiers)
        self.startNotification()


class ShopSalesEventController(IShopSalesEventController, _Notifiable):
    __appLoader = dependency.descriptor(IAppLoader)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __webController = dependency.descriptor(IWebController)

    def __init__(self):
        super(ShopSalesEventController, self).__init__()
        self.__em = EventManager()
        self.onStateChanged = Event(self.__em)
        self.onPhaseChanged = Event(self.__em)
        self.onBundlePurchased = Event(self.__em)
        self.onCurrentBundleChanged = Event(self.__em)
        self.onFavoritesChanged = Event(self.__em)
        self.__state = {}
        self.__phase = None
        self.__currentBundleInfo = (True,
         '',
         0,
         None)
        self.__favoritesCount = 0
        self.__sysChanelNotifier = None
        return

    @property
    def isEnabled(self):
        return self.__state.get('enabled', False)

    @property
    def isForbidden(self):
        return not self.__currentBundleInfo[0]

    @property
    def isInEvent(self):
        return getServerUTCTime() < self.eventFinishTime

    @property
    def currentEventPhase(self):
        return self.__phase

    @property
    def currentEventPhaseTimeRange(self):
        return self.getEventPhaseTimeRange(self.__phase)

    @property
    def reRollPrice(self):
        return Money(**self.__state.get('rerollPrice', {}))

    @property
    def periodicRenewalPeriod(self):
        return self.__state.get('periodicRenewalPeriod', 86400)

    @property
    def periodicRenewalStartTime(self):
        return self.__state.get('periodicRenewalStartTime', 0.0)

    @property
    def activePhaseStartTime(self):
        return self.__state.get('activePhaseStartTime', 0.0)

    @property
    def activePhaseFinishTime(self):
        return self.__state.get('activePhaseFinishTime', 0.0)

    @property
    def eventFinishTime(self):
        return self.__state.get('eventFinishTime', 0.0)

    @property
    def currentBundleID(self):
        return self.__currentBundleInfo[1]

    @property
    def currentBundleReRolls(self):
        return self.__currentBundleInfo[2]

    @property
    def favoritesCount(self):
        return self.__favoritesCount

    @adisp_async
    @adisp_process
    def reRollBundle(self, callback=None):
        asyncResult = yield ShopSalesEventReRollProcessor().request()
        newBundleInfo = asyncResult.auxData
        self.__updateBundleInfo(newBundleInfo)
        callback(newBundleInfo)

    def getEventPhase(self, timestamp):
        if timestamp < self.activePhaseStartTime:
            return EventPhase.NOT_STARTED
        elif timestamp < self.activePhaseFinishTime:
            return EventPhase.IN_PROGRESS
        else:
            return EventPhase.FINISHED if timestamp < self.eventFinishTime else None

    def getEventPhaseTimeRange(self, phase):
        if phase == EventPhase.NOT_STARTED:
            return (0, self.activePhaseStartTime)
        if phase == EventPhase.IN_PROGRESS:
            return (self.activePhaseStartTime, self.activePhaseFinishTime)
        return (self.activePhaseFinishTime, self.eventFinishTime) if phase == EventPhase.FINISHED else (self.eventFinishTime, sys.maxint)

    def setFavoritesCount(self, value):
        if self.__favoritesCount != value:
            self.__favoritesCount = value
            self.onFavoritesChanged()

    def openMainView(self, url=None, origin=None):
        (showShop if origin == Origin.SHOP else showHangar)()
        showBrowserOverlayView(url or self.__state.get('url', ''), alias=VIEW_ALIAS.SHOP_SALES_MAIN_VIEW, params={'origin': origin or Origin.WITHOUT_NAME})

    def closeMainView(self):
        app = self.__appLoader.getApp()
        if app is None or app.containerManager is None:
            return
        else:
            view = app.containerManager.getView(WindowLayer.FULLSCREEN_WINDOW, {POP_UP_CRITERIA.UNIQUE_NAME: VIEW_ALIAS.SHOP_SALES_MAIN_VIEW})
            if view is None:
                return
            view.onCloseBtnClick()
            return

    def init(self):
        self.__loadState()

    def fini(self):
        self.__stop()
        self.__clear()
        self.__saveState()

    def onLobbyInited(self, event):
        self.__sysChanelNotifier = _EventStatusSystemChanelNotifier()
        self.__sysChanelNotifier.init()
        self.__update(self.__lobbyContext.getServerSettings().shopSalesEventConfig.asDict())
        self.__subscribe()

    def onAccountBecomeNonPlayer(self):
        self.__stop()
        self.__clear()
        self.__saveState()

    def __stop(self):
        self.stopNotification()
        if self.__sysChanelNotifier is not None:
            self.__sysChanelNotifier.fini()
        return

    def __clear(self):
        self.__em.clear()
        self.__unsubscribe()

    def __subscribe(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__onChatMessageReceived
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def __unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onChatMessageReceived

    def __loadState(self):
        self.__updateState(AccountSettings.getSettings(SHOP_SALES_EVENT_STATE))

    def __saveState(self):
        AccountSettings.setSettings(SHOP_SALES_EVENT_STATE, self.__state)

    def __onChatMessageReceived(self, clientID, message):
        if message is not None and _isShopSalesEventBundlePurchasedMessage(message.data):
            self.onBundlePurchased(message.data)
            self.__updateCurrentBundle()
            if self.__phase == EventPhase.FINISHED:
                self.__updateFavoritesCount()
        return

    def __onTokensUpdate(self, diff):
        if any((key.startswith('cn_11_11_forbidden') for key in diff.keys())):
            self.__updateCurrentBundle()

    @server_settings.serverSettingsChangeListener(SHOP_SALES_CONFIG)
    def __onServerSettingsChanged(self, diff):
        self.__update(diff[SHOP_SALES_CONFIG])

    def __update(self, data):
        self.__updateState(data)
        self.__updateCurrentBundle()
        self.__updateFavoritesCount()

    def __updateState(self, data):
        newState = dict(self.__state)
        newState.update(data)
        self.__state = newState
        self.__updatePhase()
        self.onStateChanged()

    def __updatePhase(self, updateBundle=False):
        newPhase = self.getEventPhase(getServerUTCTime())
        if newPhase != self.__phase:
            self.__phase = newPhase
            if updateBundle and newPhase == EventPhase.IN_PROGRESS:
                self.__updateCurrentBundle()
            self.onPhaseChanged()
        self.updateNotifiers(SimpleNotifier(self.__getToNextNotifyDelta, partial(self.__updatePhase, updateBundle=True)))

    def __getToNextNotifyDelta(self):
        _, endTimestamp = self.currentEventPhaseTimeRange
        return endTimestamp - getServerUTCTime() + _SECONDS_BEFORE_UPDATE

    @adisp_process
    def __updateCurrentBundle(self):
        if self.isEnabled:
            asyncResult = yield ShopSalesEventGetCurrentBundleProcessor().request()
            newBundleInfo = asyncResult.auxData
        else:
            newBundleInfo = (True,
             '',
             0,
             None)
        self.__updateBundleInfo(newBundleInfo)
        return

    def __updateBundleInfo(self, newBundleInfo):
        if newBundleInfo == self.__currentBundleInfo:
            return
        self.__currentBundleInfo = newBundleInfo
        self.onCurrentBundleChanged()

    @adisp_process
    def __updateFavoritesCount(self):
        if not self.isEnabled:
            _logger.debug('Unable to fetch favorites. Reason: Disabled by server.')
        elif self.isInEvent and self.currentEventPhase != EventPhase.NOT_STARTED:
            response = yield self.__webController.sendRequest(ctx=ShopSalesEventFetchFavoritesCtx())
            if response.isSuccess():
                favoritesList = response.getData() or []
                self.setFavoritesCount(len(favoritesList))
            else:
                _logger.warning('Unable to fetch favorites. Code: %s.', response.getCode())
        else:
            _logger.debug('Unable to fetch favorites. Reason: Invalid event phase.')


def _isShopSalesEventBundlePurchasedMessage(messageData):
    return isinstance(messageData, dict) and 'wgds' in messageData.get('tags', [])
