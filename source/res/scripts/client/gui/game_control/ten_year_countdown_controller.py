# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ten_year_countdown_controller.py
import calendar
import logging
import time
from collections import namedtuple
import typing
import Event
from adisp import process
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.game_control import ITenYearsCountdownController
from skeletons.gui.server_events import IEventsCache
from ten_year_countdown_config import EventBlockStates, FIRST_BLOCK_NUMBER, EVENT_BLOCKS_COUNT
from gui.game_control.links import URLMacros
_logger = logging.getLogger(__name__)
_EVENT_STATE_NAME = 'EventState'
_EVENT_BLOCK_NAME = 'EventBlock'
_EVENT_DATES_NAME = 'EventDates'
_EVENT_URL_NAME = 'EventBaseURL'
_EVENT_STATE_IN_PROGRESS = 'in_progress'
_EVENT_STATE_END = 'end'
_CurrentBlock = namedtuple('CurrentBlock', ('number', 'state'))
_CurrentBlock.__new__.__defaults__ = (FIRST_BLOCK_NUMBER, EventBlockStates.PASSIVE)
ActivePhaseDates = namedtuple('ActivePhaseDates', ('start', 'finish'))

class TenYearsCountdownController(ITenYearsCountdownController):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(TenYearsCountdownController, self).__init__()
        self.onEventStateChanged = Event.Event()
        self.onEventBlockChanged = Event.Event()
        self.onEventMonthsChanged = Event.Event()
        self.onActivePhasesDatesChanged = Event.Event()
        self.onEventFinishChanged = Event.Event()
        self.onEventDataUpdated = Event.Event()
        self.onBlocksDataValidityChanged = Event.Event()
        self.__isEventActive = False
        self.__currentBlock = _CurrentBlock()
        self.__months = {}
        self.__activePhaseDates = {}
        self.__eventFinish = 0
        self.__blocksCount = 0
        self.__eventBaseURL = ''
        self.__isBlocksDataValid = False
        self.__periodicNotifier = None
        return

    def fini(self):
        self.__clear()
        self.__currentBlock = None
        self.onEventStateChanged.clear()
        self.onEventBlockChanged.clear()
        self.onActivePhasesDatesChanged.clear()
        self.onEventMonthsChanged.clear()
        self.onEventFinishChanged.clear()
        self.onEventDataUpdated.clear()
        self.onBlocksDataValidityChanged.clear()
        return

    def onLobbyInited(self, event):
        self.__eventsCache.onSyncCompleted += self.__update
        self.__update()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def isEnabled(self):
        return self.__isEventActive

    def isCurrentBlockActive(self):
        return self.__isEventActive and self.__currentBlock.state == EventBlockStates.ACTIVE

    def getCurrentBlock(self):
        return self.__currentBlock

    def getCurrentBlockNumber(self):
        return self.__currentBlock.number if self.__currentBlock is not None else 0

    def getCurrentBlockState(self):
        return self.__currentBlock.state if self.__currentBlock is not None else None

    def getBlocksCount(self):
        return self.__blocksCount

    def getMonths(self):
        return self.__months

    def getMonth(self, blockNumber):
        return self.__months.get(blockNumber, 0)

    def getActivePhaseDates(self, blockNumber):
        return self.__activePhaseDates.get(blockNumber, ActivePhaseDates(0, 0))

    def getEventFinish(self):
        return self.__eventFinish

    def getEventBaseURL(self):
        return self.__eventBaseURL

    def isBlocksDataValid(self):
        return self.__isBlocksDataValid

    def isEventInProgress(self):
        return self.__isEventActive and self.__currentBlock.state != EventBlockStates.NOT_STARTED and self.__currentBlock.state != EventBlockStates.FINISHED

    def __clear(self):
        self.__isEventActive = False
        self.__currentBlock = _CurrentBlock()
        self.__months.clear()
        self.__activePhaseDates.clear()
        self.__eventFinish = 0
        self.__blocksCount = 0
        self.__eventBaseURL = ''
        self.__eventsCache.onSyncCompleted -= self.__update
        if self.__periodicNotifier is not None:
            self.__periodicNotifier.stopNotification()
            self.__periodicNotifier.clear()
            self.__periodicNotifier = None
        return

    def __update(self):
        actions = self.__eventsCache.getActions()
        eventState = self.__getEventState(actions, _EVENT_STATE_NAME)
        if eventState is None:
            return
        else:
            isBlocksDataValid = False
            if eventState not in (_EVENT_STATE_IN_PROGRESS, _EVENT_STATE_END):
                _logger.error('Event state should be: "%s" or "%s"', _EVENT_STATE_IN_PROGRESS, _EVENT_STATE_END)
                return
            self.__updateEvent(eventState)
            eventBaseURL = self.__getEventState(actions, _EVENT_URL_NAME)
            if not eventBaseURL:
                _logger.error('Event base url is not defined in step "EventBaseURL"')
            else:
                self.__updateBaseURL(eventBaseURL)
            datesState = self.__getEventState(actions, _EVENT_DATES_NAME)
            eventDates = self.__parseEventDates(datesState)
            if eventDates is not None:
                activePhaseDates, months, eventFinish = eventDates
                blocksCount = len(months)
                monthsByBlocks = {block:months[block - 1] for block in range(FIRST_BLOCK_NUMBER, blocksCount + 1)}
                activePhaseDatesByBlocks = {block:activePhaseDates[block - 1] for block in range(FIRST_BLOCK_NUMBER, blocksCount + 1)}
                block = self.__getCurrentBlock(activePhaseDatesByBlocks, eventFinish)
                if block is not None:
                    if block.state == EventBlockStates.FINISHED:
                        _logger.error('Event has finished.')
                    else:
                        self.__blocksCount = blocksCount
                        isBlocksDataValid = True
                        self.__updateMonths(monthsByBlocks)
                        self.__updateActivePhaseDates(activePhaseDatesByBlocks)
                        self.__updateEventFinish(eventFinish)
                        self.__updateCurrentBlock(block)
                        self.__startNotifier()
            self.__updateDataValidity(isBlocksDataValid)
            self.onEventDataUpdated()
            return

    def __updateEvent(self, eventState):
        isEventActive = eventState == _EVENT_STATE_IN_PROGRESS
        if self.__isEventActive != isEventActive:
            self.__isEventActive = isEventActive
            self.onEventStateChanged()

    def __updateCurrentBlock(self, block):
        if self.__currentBlock != block:
            self.__currentBlock = block
            self.onEventBlockChanged()

    def __updateMonths(self, months):
        if self.__months != months:
            self.__months = months
            self.onEventMonthsChanged()

    def __updateActivePhaseDates(self, dates):
        if self.__activePhaseDates != dates:
            self.__activePhaseDates = dates
            self.onActivePhasesDatesChanged()

    def __updateEventFinish(self, eventFinish):
        if self.__eventFinish != eventFinish:
            self.__eventFinish = eventFinish
            self.onEventFinishChanged()

    def __updateDataValidity(self, isBlocksDataValid):
        if self.__isBlocksDataValid != isBlocksDataValid:
            self.__isBlocksDataValid = isBlocksDataValid
            self.onBlocksDataValidityChanged()

    def __startNotifier(self):
        if self.__periodicNotifier is None and self.__currentBlock.state != EventBlockStates.FINISHED:
            self.__periodicNotifier = PeriodicNotifier(self.__getTimeLeft, self.__updateCurrentBlockOnTimeChanged, (time_utils.ONE_MINUTE,))
            self.__periodicNotifier.startNotification()
        return

    def __updateCurrentBlockOnTimeChanged(self):
        timeLeft = self.__getTimeLeft()
        if timeLeft == 0:
            block = self.__getCurrentBlock(self.__activePhaseDates, self.__eventFinish)
            self.__updateCurrentBlock(block)
            if block.state == EventBlockStates.FINISHED and self.__periodicNotifier is not None:
                self.__periodicNotifier.stopNotification()
        return

    def __getTimeLeft(self):
        if self.__currentBlock.state == EventBlockStates.NOT_STARTED:
            event = self.__activePhaseDates[FIRST_BLOCK_NUMBER].start
        elif self.__currentBlock.state == EventBlockStates.ACTIVE:
            event = self.__activePhaseDates[self.__currentBlock.number].finish
        elif self.__currentBlock.number < self.__blocksCount:
            event = self.__activePhaseDates[self.__currentBlock.number + 1].start
        elif self.__currentBlock.number == self.__blocksCount and self.__currentBlock.state == EventBlockStates.PASSIVE:
            event = self.__eventFinish
        else:
            return 0
        now = time_utils.getServerUTCTime()
        timeLeft = event - now
        return max(0, timeLeft)

    @process
    def __updateBaseURL(self, eventBaseURL):
        eventBaseURL = yield URLMacros().parse(eventBaseURL)
        if self.__eventBaseURL != eventBaseURL:
            self.__eventBaseURL = eventBaseURL

    @staticmethod
    def __getEventState(actions, eventName):
        for action in actions.itervalues():
            steps = action.getData()['steps']
            if steps is None:
                continue
            for step in steps:
                if step.get('name') != eventName:
                    continue
                return step.get('params').get('state')

        return

    @staticmethod
    def __getCurrentBlock(activePhases, eventFinish):
        if not activePhases:
            return
        else:
            now = time_utils.getServerUTCTime()
            if now < activePhases[FIRST_BLOCK_NUMBER].start:
                _logger.error("Event hasn't started yet.")
                return _CurrentBlock(FIRST_BLOCK_NUMBER, EventBlockStates.NOT_STARTED)
            if now >= eventFinish:
                return _CurrentBlock(5, EventBlockStates.FINISHED)
            nextBlockNumber = first((block for block, date in activePhases.iteritems() if date.start > now))
            if nextBlockNumber is None:
                blockNumber = activePhases.keys()[-1]
            else:
                blockNumber = nextBlockNumber - 1
            blockState = EventBlockStates.ACTIVE if now < activePhases[blockNumber].finish else EventBlockStates.PASSIVE
            currentBlock = _CurrentBlock(blockNumber, blockState)
            return currentBlock

    @staticmethod
    def __parseEventDates(eventDates):
        if eventDates is None:
            return
        else:
            activePhaseDates = []
            months = []
            try:
                active, finish = eventDates.split('||')
            except ValueError:
                _logger.error('Invalid format of event dates section: %s', eventDates)
                return

            try:
                dates = active.split('|')
            except ValueError:
                dates = []
                _logger.error('Invalid format of active phase dates section: %s', dates)
                return

            for date in dates:
                month, activePhaseDate = TenYearsCountdownController.__parseActivePhaseDate(date)
                if month is not None and activePhaseDate is not None:
                    if activePhaseDates and activePhaseDate.start < activePhaseDates[-1].start:
                        _logger.error('Start of active phase should be later than start of previous active phase.')
                        return
                    if activePhaseDates and activePhaseDate.start < activePhaseDates[-1].finish:
                        _logger.error('Start of active phase should be later than finish of previous active phase.')
                    else:
                        months.append(month)
                        activePhaseDates.append(activePhaseDate)

            if len(activePhaseDates) != EVENT_BLOCKS_COUNT:
                _logger.error('Number of dates should be equal to the number of event blocks: %s', EVENT_BLOCKS_COUNT)
                return
            if finish:
                eventFinish = TenYearsCountdownController.__parseEventFinishDate(finish)
                if activePhaseDates and eventFinish < activePhaseDates[-1].finish:
                    _logger.error('Finish of event should be later than finish of last active phase.')
                    return
            else:
                eventFinish = 0
            return (activePhaseDates, months, eventFinish)

    @staticmethod
    def __parseActivePhaseDate(date):
        try:
            start, finish = date.split()
            start = time.strptime(start, '%d.%m.%Y-%H:%M:%S')
            finish = time.strptime(finish, '%d.%m.%Y-%H:%M:%S')
            month = start.tm_mon
            start = calendar.timegm(start)
            finish = calendar.timegm(finish)
            if finish < start:
                _logger.error('Start of active phase should be earlier than its end.')
                month, activePhaseDate = (None, None)
            else:
                activePhaseDate = ActivePhaseDates(start, finish)
        except ValueError:
            _logger.error('Invalid format: %s, dates should be in format DD.MM.YYYY-HH:MM:SS', date)
            month, activePhaseDate = (None, None)

        return (month, activePhaseDate)

    @staticmethod
    def __parseEventFinishDate(finish):
        try:
            eventFinish = time.strptime(finish.strip(), '%d.%m.%Y-%H:%M:%S')
            eventFinish = calendar.timegm(eventFinish)
        except ValueError:
            eventFinish = 0
            _logger.error('Invalid format: %s, date should be in format DD.MM.YYYY-HH:MM:SS', eventFinish)

        return eventFinish
