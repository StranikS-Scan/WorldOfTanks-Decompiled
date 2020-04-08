# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/pre_launch_controller.py
import logging
import typing
import Event
from helpers import dependency
from skeletons.gui.game_control import IPreLaunchController
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
_PRELAUNCH_COUNT = 'PrelaunchCount'
_PREEVENT_STATE = 'PreEventState'
_STATE_EVENT_IN_PROGRESS = 'in_progress'

class PreLaunchController(IPreLaunchController):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(PreLaunchController, self).__init__()
        self._progressPercent = 0
        self._textID = 0
        self._preEventActive = False
        self.onPrelaunchCountChanged = Event.Event()
        self.onPrelaunchTextChanged = Event.Event()
        self.onPreEventStateChanged = Event.Event()
        self.onEventCurrencyAmountChanged = Event.Event()
        self.__needToShowTeaser = False

    def fini(self):
        self.__clear()
        self.onPrelaunchCountChanged.clear()
        self.onPrelaunchTextChanged.clear()
        self.onPreEventStateChanged.clear()
        self.onEventCurrencyAmountChanged.clear()

    def onLobbyInited(self, event):
        self._eventsCache.onSyncCompleted += self.__eventsDataUpdate
        self.__eventsDataUpdate()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onAccountBecomeNonPlayer(self):
        self.__needToShowTeaser = False

    def onConnected(self):
        self.__needToShowTeaser = True

    def onDisconnected(self):
        self.__clear()

    def getCount(self):
        return self._progressPercent

    def getTextID(self):
        return self._textID

    def isPreEventActive(self):
        return self._preEventActive

    def needToShowTeaser(self):
        return self.__needToShowTeaser

    def __clear(self):
        self._eventsCache.onSyncCompleted -= self.__eventsDataUpdate
        self.__needToShowTeaser = False

    @staticmethod
    def __getEventState(actions, nameEvent):
        for action in actions.itervalues():
            steps = action.getData()['steps']
            if steps is None:
                continue
            for step in steps:
                if step.get('name') != nameEvent:
                    continue
                return step.get('params').get('state')

        return

    def __eventsDataUpdate(self):
        actions = self._eventsCache.getActions()
        self.__updatePreEventCountText(actions)
        self.__updatePreEventState(actions)

    def __updatePreEventCountText(self, actions):
        curCountTextID = self.__getEventState(actions, _PRELAUNCH_COUNT)
        if curCountTextID is None:
            _logger.debug("No action file or section 'PrelaunchCount' in action")
            return
        else:
            try:
                curProgressPercentStr, curTextIDStr = curCountTextID.split(' ', 1)
            except ValueError:
                _logger.error("Can't split 'PrelaunchCount' string")
                return

            curCount = self.__tryConvertToInt(curProgressPercentStr, 'curProgressPercentStr')
            curTextID = self.__tryConvertToInt(curTextIDStr, 'curTextIDStr')
            self.__updateCount(curCount)
            self.__updateText(curTextID)
            return

    def __updateText(self, curTextID):
        if curTextID != self._textID:
            self._textID = curTextID
            self.__needToShowTeaser = True
            self.onPrelaunchTextChanged()

    def __updateCount(self, curProgressPercent):
        if curProgressPercent > 100:
            curProgressPercent = 100
        elif curProgressPercent < 0:
            curProgressPercent = 0
        if curProgressPercent != self._progressPercent:
            self._progressPercent = curProgressPercent
            self.onPrelaunchCountChanged()

    @staticmethod
    def __tryConvertToInt(curStr, nameVariable):
        try:
            number = int(curStr)
        except ValueError:
            _logger.error("Can't convert %s to int", nameVariable)
            number = 0

        return number

    def __updatePreEventState(self, actions):
        preEventState = self.__getEventState(actions, _PREEVENT_STATE) == _STATE_EVENT_IN_PROGRESS
        if preEventState != self._preEventActive:
            self._preEventActive = preEventState
            self.onPreEventStateChanged()
