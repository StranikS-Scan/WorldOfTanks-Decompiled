# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/shop_sales_event_controller.py
import logging
import sys
import json
from Event import Event, EventManager
from constants import EventPhase
from gui.impl.lobby.shop_sales.shop_sales_main_view import ShopSalesMainWindow
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers.time_utils import getServerUTCTime, getTimestampByStrDate
from helpers.events_handler import EventsHandler
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IShopSalesEventController, IEventsNotificationsController
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)
_HANGAR_ENTRY_POINTS = 'hangarEntryPoints'
_SHOP_SALES_ENTRY_POINT = 'ShopSalesEntryPoint'

class _Notifiable(Notifiable):

    def updateNotifiers(self, *notifiers):
        self.clearNotification()
        self.addNotificators(*notifiers)
        self.startNotification()


class ShopSalesEventController(IShopSalesEventController, _Notifiable, EventsHandler):
    __appLoader = dependency.descriptor(IAppLoader)
    __webController = dependency.descriptor(IWebController)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)

    def __init__(self):
        super(ShopSalesEventController, self).__init__()
        self.__phase = None
        self.__em = EventManager()
        self.onSettingsChanged = Event(self.__em)
        self.onPhaseChanged = Event(self.__em)
        self.__reset()
        self.__phaseNotifier = PeriodicNotifier(self.__getToNextNotifyDelta, self.__updatePhase)
        self.updateNotifiers(self.__phaseNotifier)
        return

    def __reset(self):
        self.__url = ''
        self.__enabled = False
        self.__eventStartTime = 0
        self.__eventFinishTime = 0
        self.__activePhaseStartTime = 0
        self.__activePhaseFinishTime = 0

    @property
    def isEnabled(self):
        return self.__enabled

    def isShopSalesEntryPointAvailable(self):
        return self.isEnabled and getServerUTCTime() < self.eventFinishTime

    @property
    def currentEventPhase(self):
        return self.__phase

    @property
    def currentEventPhaseTimeRange(self):
        return self.getEventPhaseTimeRange(self.__phase)

    @property
    def activePhaseStartTime(self):
        return self.__activePhaseStartTime

    @property
    def activePhaseFinishTime(self):
        return self.__activePhaseFinishTime

    @property
    def eventFinishTime(self):
        return self.__eventFinishTime

    @property
    def url(self):
        return self.__url

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

    def openMainView(self, url=None, origin=None):
        url = url or self.__url
        _logger.info('I will open shop sales with url %s', url)
        window = ShopSalesMainWindow(url)
        window.load()

    def start(self):
        self.__scanNotifications()

    def fini(self):
        self.__stop()
        self.__clear()

    def onLobbyInited(self, event):
        self.start()
        self._subscribe()

    def onAccountBecomeNonPlayer(self):
        self.__stop()
        self.__clear()

    def _getEvents(self):
        return ((self.__notificationsCtrl.onEventNotificationsChanged, self.__onEventNotification),)

    def __stop(self):
        self.stopNotification()

    def __clear(self):
        self.__em.clear()
        self._unsubscribe()

    def __scanNotifications(self):
        for item in self.__notificationsCtrl.getEventsNotifications():
            if item.eventType == _HANGAR_ENTRY_POINTS:
                self.__parseNotificationData(item)

    def __onEventNotification(self, added, removed):
        for item in removed:
            if item.eventType == _HANGAR_ENTRY_POINTS:
                notificationEntries = json.loads(item.data)
                for entryData in notificationEntries:
                    if str(entryData.get('id')) == _SHOP_SALES_ENTRY_POINT:
                        self.__reset()
                        self.__updatePhase()
                        self.onSettingsChanged()

        for item in added:
            if item.eventType == _HANGAR_ENTRY_POINTS:
                self.__parseNotificationData(item)

    def __parseNotificationData(self, item):
        if item is None:
            return
        else:
            notificationEntries = json.loads(item.data)
            for entryData in notificationEntries:
                if str(entryData.get('id')) == _SHOP_SALES_ENTRY_POINT:
                    self.__enabled = True
                    self.__url = entryData.get('shopSalesUrl', '')
                    try:
                        self.__eventStartTime = getTimestampByStrDate(entryData.get('startDate', ''))
                        self.__eventFinishTime = getTimestampByStrDate(entryData.get('endDate', ''))
                        self.__activePhaseStartTime = getTimestampByStrDate(entryData.get('activePhaseStartTime', ''))
                        self.__activePhaseFinishTime = getTimestampByStrDate(entryData.get('activePhaseFinishTime', ''))
                    except ValueError as exc:
                        _logger.error('Invalid event config: %s', exc)
                        self.__reset()

                    self.__updatePhase()
                    self.onSettingsChanged()

            return

    def __updatePhase(self):
        newPhase = self.getEventPhase(getServerUTCTime())
        if newPhase == self.__phase:
            return
        self.__phase = newPhase
        self.__phaseNotifier.startNotification()
        self.onPhaseChanged()

    def __getToNextNotifyDelta(self):
        _, endTimestamp = self.currentEventPhaseTimeRange
        return 0 if endTimestamp == sys.maxint else endTimestamp - getServerUTCTime() + 1


@dependency.replace_none_kwargs(shopSalesEventController=IShopSalesEventController)
def getShopSalesEntryPointIsActive(shopSalesEventController=None):
    _logger.debug('isShopSalesEntryPointAvailable: %s', shopSalesEventController.isShopSalesEntryPointAvailable())
    return shopSalesEventController.isShopSalesEntryPointAvailable()
