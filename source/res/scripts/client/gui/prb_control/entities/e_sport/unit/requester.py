# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/requester.py
import time
import BigWorld
from PlayerEvents import g_playerEvents
from UnitBase import UNIT_ERROR
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages
from gui.prb_control import prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from helpers import time_utils

class UnitAutoSearchHandler(object):
    """
    Unit auto search requester: it handles player's request to:
    - start
    - accept
    - decline
    - stop
    """

    def __init__(self, entity):
        super(UnitAutoSearchHandler, self).__init__()
        self.__entity = entity
        self.__vTypeDescrs = []
        self.__isInSearch = False
        self.__hasResult = False
        self.__startSearchTime = -1
        self.__lastErrorCode = UNIT_ERROR.OK

    def init(self):
        """
        Initialization of requester. Subscription to browser events.
        """
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            browser.onSearchSuccessReceived += self.unitBrowser_onSearchSuccessReceived
            browser.onErrorReceived += self.unitBrowser_onErrorReceived
        else:
            LOG_ERROR('Unit browser is not defined')
        g_playerEvents.onDequeuedUnitAssembler += self.pe_onDequeuedUnitAssembler
        g_playerEvents.onKickedFromUnitAssembler += self.pe_onKickedFromUnitAssembler
        g_playerEvents.onEnqueuedUnitAssembler += self.pe_onEnqueuedUnitAssembler

    def fini(self):
        """
        Finalization of requester. Unsubscription from browser events.
        """
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            browser.onSearchSuccessReceived -= self.unitBrowser_onSearchSuccessReceived
            browser.onErrorReceived -= self.unitBrowser_onErrorReceived
        g_playerEvents.onDequeuedUnitAssembler -= self.pe_onDequeuedUnitAssembler
        g_playerEvents.onKickedFromUnitAssembler -= self.pe_onKickedFromUnitAssembler
        g_playerEvents.onEnqueuedUnitAssembler -= self.pe_onEnqueuedUnitAssembler
        if self.__isInSearch:
            self.stop()
        self.__entity = None
        return

    def initEvents(self, listener):
        """
        Initializes event listeners
        """
        if self.__hasResult:
            browser = prb_getters.getClientUnitBrowser()
            if browser:
                acceptDelta = self.getAcceptDelta(browser._acceptDeadlineUTC)
                if acceptDelta > 0:
                    LOG_DEBUG('onUnitAutoSearchSuccess', acceptDelta)
                    listener.onUnitAutoSearchSuccess(acceptDelta)
        elif self.__isInSearch:
            g_eventDispatcher.setUnitProgressInCarousel(self.__entity.getEntityType(), True)
            listener.onUnitAutoSearchStarted(self.getTimeLeftInSearch())

    def isInSearch(self):
        """
        Are we in search now
        """
        return self.__isInSearch

    def getTimeLeftInSearch(self):
        """
        Get time that left in search
        """
        if self.__startSearchTime > -1:
            timeLeft = int(BigWorld.time() - self.__startSearchTime)
        else:
            timeLeft = -1
        return timeLeft

    def getAcceptDelta(self, acceptDeadlineUTC):
        """
        Get acceptance time delta
        Args:
            acceptDeadlineUTC: time when approval expires
        """
        return max(0, int(time_utils.makeLocalServerTime(acceptDeadlineUTC) - time.time())) if acceptDeadlineUTC else 0

    def start(self, vTypeDescrs=None):
        """
        Start auto search with vehicles selected:
        Args:
            vTypeDescrs: list of selected vehicles intCDs
        """
        if self.__isInSearch:
            LOG_ERROR('Auto search already started.')
            return False
        else:
            browser = prb_getters.getClientUnitBrowser()
            if browser:
                if vTypeDescrs is not None:
                    self.__vTypeDescrs = vTypeDescrs
                self.__lastErrorCode = UNIT_ERROR.OK
                browser.startSearch(vehTypes=self.__vTypeDescrs)
                return True
            LOG_ERROR('Unit browser is not defined')
            return False
            return

    def stop(self):
        """
        Stops the auto search
        """
        if not self.__isInSearch:
            LOG_DEBUG('Auto search did not start. Exits form search forced.')
            self.__exitFromQueue()
            return True
        browser = prb_getters.getClientUnitBrowser()
        if browser:
            self.__lastErrorCode = UNIT_ERROR.OK
            browser.stopSearch()
        else:
            LOG_ERROR('Unit browser is not defined')
            return False

    def accept(self):
        """
        Accepts the auto search result
        """
        if not self.__hasResult:
            LOG_ERROR('First, sends request for search.')
            return False
        else:
            browser = prb_getters.getClientUnitBrowser()
            if browser:
                self.__lastErrorCode = UNIT_ERROR.OK
                browser.acceptSearch()
                return True
            LOG_ERROR('Unit browser is not defined')
            return False

    def decline(self):
        """
        Declines the auto search result
        """
        if not self.__hasResult:
            LOG_ERROR('First, sends request for search.')
            return False
        else:
            browser = prb_getters.getClientUnitBrowser()
            if browser:
                self.__lastErrorCode = UNIT_ERROR.OK
                browser.declineSearch()
                return True
            LOG_ERROR('Unit browser is not defined')
            return False

    def pe_onDequeuedUnitAssembler(self):
        """
        Listener for unit assembler dequeue event
        """
        self.__exitFromQueue()
        g_eventDispatcher.updateUI()

    def pe_onKickedFromUnitAssembler(self):
        """
        Listener for unit assembler kick event
        """
        self.__exitFromQueue()
        g_eventDispatcher.updateUI()
        SystemMessages.pushMessage(messages.getUnitKickedReasonMessage('KICKED_FROM_UNIT_ASSEMBLER'), type=SystemMessages.SM_TYPE.Warning)

    def pe_onEnqueuedUnitAssembler(self):
        """
        Listener for unit assembler enqueue event
        """
        self.__isInSearch = True
        self.__startSearchTime = BigWorld.time()
        g_eventDispatcher.setUnitProgressInCarousel(self.__entity.getEntityType(), True)
        for listener in self.__entity.getListenersIterator():
            listener.onUnitAutoSearchStarted(0)
        else:
            g_eventDispatcher.showUnitWindow(self.__entity.getEntityType())

        g_eventDispatcher.updateUI()

    def unitBrowser_onSearchSuccessReceived(self, unitMgrID, acceptDeadlineUTC):
        """
        Listener for auto search succeed event
        Args:
            unitMgrID: unit manager ID
            acceptDeadlineUTC: time when approval will expire
        """
        self.__hasResult = True
        acceptDelta = self.getAcceptDelta(acceptDeadlineUTC)
        LOG_DEBUG('onUnitAutoSearchSuccess', acceptDelta, acceptDeadlineUTC)
        g_eventDispatcher.setUnitProgressInCarousel(self.__entity.getEntityType(), False)
        for listener in self.__entity.getListenersIterator():
            listener.onUnitAutoSearchSuccess(acceptDelta)
        else:
            g_eventDispatcher.showUnitWindow(self.__entity.getEntityType())

        g_eventDispatcher.updateUI()

    def unitBrowser_onErrorReceived(self, errorCode, errorStr):
        """
        Listener for auto search error event
        Args:
            errorCode: error code
            errorStr: error message
        """
        self.__isInSearch = False
        self.__lastErrorCode = errorCode
        if errorCode != UNIT_ERROR.OK:
            for listener in self.__entity.getListenersIterator():
                listener.onUnitBrowserErrorReceived(errorCode)

        g_eventDispatcher.updateUI()

    def __exitFromQueue(self):
        """
        Routine clears all information that is related to in search state
        """
        self.__isInSearch = False
        self.__lastErrorCode = UNIT_ERROR.OK
        self.__hasResult = False
        self.__startSearchTime = 0
        prbType = self.__entity.getEntityType()
        g_eventDispatcher.setUnitProgressInCarousel(prbType, False)
        for listener in self.__entity.getListenersIterator():
            listener.onUnitAutoSearchFinished()
        else:
            g_eventDispatcher.showUnitWindow(prbType)
