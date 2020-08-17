# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/low_tier_rewards_controller.py
import logging
import typing
import Event
from gui.game_control.links import URLMacros
from helpers import dependency
from adisp import process
from skeletons.gui.game_control import ILowTierRewardsController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_EVENT_STATE_NAME = 'LowTierRewardsState'
_EVENT_STATE_IN_PROGRESS = 'in_progress'
_EVENT_STATE_END = 'end'
_TOKEN_STATE_END = 'giveaway10yearsreward'

class LowTierRewardsController(ILowTierRewardsController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(LowTierRewardsController, self).__init__()
        self.onEventStateChanged = Event.Event()
        self.__eventBaseURL = ''
        self.__isEventActive = False

    def fini(self):
        self.__clear()
        self.onEventStateChanged.clear()

    def isEnabled(self):
        return self.__isEventActive

    def isRewardReady(self):
        _, tokenState = self.__itemsCache.items.tokens.getTokens().get(_TOKEN_STATE_END, (0, 0))
        return not tokenState > 0

    def getEventBaseURL(self):
        return self.__eventBaseURL

    def onLobbyInited(self, event):
        self.__eventsCache.onSyncCompleted += self.__update
        self.__update()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def __clear(self):
        self.__eventBaseURL = ''
        self.__isEventActive = False
        self.__eventsCache.onSyncCompleted -= self.__update

    def __update(self):
        actions = self.__eventsCache.getActions()
        eventState, eventBaseURL = self.__getEventParams(actions, _EVENT_STATE_NAME)
        if eventState is None:
            self.__updateEvent(_EVENT_STATE_END)
            return
        elif eventState not in (_EVENT_STATE_IN_PROGRESS, _EVENT_STATE_END):
            _logger.error('Event state should be: "%s" or "%s"', _EVENT_STATE_IN_PROGRESS, _EVENT_STATE_END)
            self.__updateEvent(_EVENT_STATE_END)
            return
        else:
            self.__updateEvent(eventState)
            if not eventBaseURL:
                _logger.error('Event base url is not defined in step "EventBaseURL"')
            else:
                self.__updateBaseURL(eventBaseURL)
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
                return (step.get('params').get('state'), step.get('params').get('url'))

        return (None, None)

    def __updateEvent(self, eventState):
        isEventActive = eventState == _EVENT_STATE_IN_PROGRESS
        if self.__isEventActive != isEventActive:
            self.__isEventActive = isEventActive
            self.onEventStateChanged()

    @process
    def __updateBaseURL(self, eventBaseURL):
        self.__eventBaseURL = yield URLMacros().parse(eventBaseURL)
