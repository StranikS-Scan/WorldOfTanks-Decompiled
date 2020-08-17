# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/low_tier_mm_controller.py
import calendar
from datetime import datetime
import typing
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LOW_TIER_REWARDS_LAST_STATE
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import ILowTierMMController
from skeletons.gui.server_events import IEventsCache
_EVENT_STATE_NAME = 'MatchMakerState'
FORMAT_DATE = '%d-%m-%Y_%H-%M'

def isEnabledMMEvent():
    return AccountSettings.getSettings(LOW_TIER_REWARDS_LAST_STATE)


def setEnabledMMEvent(state):
    AccountSettings.setSettings(LOW_TIER_REWARDS_LAST_STATE, state)


class LowTierMMController(ILowTierMMController):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(LowTierMMController, self).__init__()
        self.onEventStateChanged = Event.Event()
        self.__isEventActive = False
        self.__dateFinish = None
        self.__notifier = None
        return

    def fini(self):
        self.__clear()
        self.onEventStateChanged.clear()
        self.__clearNotifier()

    def isEnabled(self):
        return self.__isEventActive

    def getDateFinish(self):
        return self.__dateFinish

    def onLobbyInited(self, event):
        self.__eventsCache.onSyncCompleted += self.__update
        self.__update()

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.__clearNotifier()

    def onDisconnected(self):
        self.__clear()
        self.__clearNotifier()

    def __getTimeDelta(self):
        return self.__dateFinish - time_utils.getServerUTCTime()

    def __clear(self):
        self.__isEventActive = False
        self.__dateFinish = None
        self.__eventsCache.onSyncCompleted -= self.__update
        return

    def __clearNotifier(self):
        if self.__notifier:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        return

    def __update(self):
        actions = self.__eventsCache.getActions()
        eventState = self.__getEventParams(actions, _EVENT_STATE_NAME)
        try:
            dateFinishDT = datetime.strptime(eventState.strip(), FORMAT_DATE)
            self.__dateFinish = calendar.timegm(dateFinishDT.timetuple())
        except (AttributeError, TypeError):
            self.__updateEvent(False)
            self.__dateFinish = None
            return

        currtime = time_utils.getServerUTCTime()
        eventState = self.__dateFinish > currtime
        self.__updateEvent(eventState)
        self.__clearNotifier()
        if eventState:
            self.__notifier = SimpleNotifier(self.__getTimeDelta, self.__update)
            self.__notifier.startNotification()
        else:
            self.__dateFinish = None
        return

    @staticmethod
    def __getEventParams(actions, eventName):
        for action in actions.itervalues():
            steps = action.getData()['steps']
            if steps is None:
                continue
            for step in steps:
                if step.get('name') != eventName:
                    continue
                return step.get('params').get('date')

        return

    def __updateEvent(self, eventState):
        if self.__isEventActive != eventState:
            self.__isEventActive = eventState
            setEnabledMMEvent(self.__isEventActive)
            self.onEventStateChanged()
