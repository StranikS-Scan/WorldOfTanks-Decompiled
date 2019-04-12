# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/league_provider.py
from collections import namedtuple
import logging
import time
import BigWorld
import Event
import constants
from adisp import process
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)
_LEAGUE_SYNC_TIME = 2 * ONE_MINUTE
WebLeague = namedtuple('WebLeague', 'league, position')
UNDEFINED_LEAGUE_ID = 0
UNDEFINED_WEB_LEAGUE = WebLeague(UNDEFINED_LEAGUE_ID, None)

class RankedBattlesLeagueProvider(object):
    clansController = dependency.descriptor(IWebController)
    __slots__ = ('onLeagueUpdated', '__em', '__callbackID', '__fakeWebLeague', '__mutexOpen', '__lastUpdateTime', '__webLeague', '__isStarted')

    def __init__(self):
        super(RankedBattlesLeagueProvider, self).__init__()
        self.__em = Event.EventManager()
        self.onLeagueUpdated = Event.Event(self.__em)
        self.__callbackID = None
        self.__fakeWebLeague = None
        self.__mutexOpen = True
        self.__lastUpdateTime = None
        self.__webLeague = UNDEFINED_WEB_LEAGUE
        self.__isStarted = False
        return

    @property
    def isStarted(self):
        return self.__isStarted

    @property
    def lastUpdateTime(self):
        return self.__lastUpdateTime

    @property
    def webLeague(self):
        return self.__webLeague

    @staticmethod
    def getUpdateFrequency():
        return _LEAGUE_SYNC_TIME

    def clear(self):
        self.__lastUpdateTime = None
        self.__webLeague = UNDEFINED_WEB_LEAGUE
        return

    def forceUpdateLeague(self):
        if self.__mutexOpen:
            self.__mutexOpen = False
            _logger.debug('LeagueProvider update starts')
            self.__updateLeague()
            self.__mutexOpen = True
            self.onLeagueUpdated()
            _logger.debug('LeagueProvider update finishes')

    def setWebLeague(self, league=0, position=0):
        if constants.IS_DEVELOPMENT:
            self.__fakeWebLeague = WebLeague(league, position)

    def start(self):
        self.forceUpdateLeague()
        if self.isStarted:
            return
        self.__isStarted = True
        self.__callbackID = BigWorld.callback(_LEAGUE_SYNC_TIME, self.__invoke)

    def stop(self):
        if self.__isStarted:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__isStarted = False
        return

    def __invoke(self):
        self.__callbackID = None
        self.forceUpdateLeague()
        if self.isStarted:
            self.__callbackID = BigWorld.callback(_LEAGUE_SYNC_TIME, self.__invoke)
        return

    @process
    def __updateLeague(self):
        if not self.__fakeWebLeague or not constants.IS_DEVELOPMENT:
            if self.clansController.getAccountProfile():
                result = yield self.clansController.getClanDossier().requestRankedPosition()
                if result is not None and isinstance(result, dict):
                    results = result.get('results')
                    if results is not None and isinstance(results, dict):
                        self.__webLeague = WebLeague(results.get('league'), results.get('position'))
                        self.__lastUpdateTime = time.time()
        else:
            self.__webLeague = self.__fakeWebLeague
            self.__lastUpdateTime = time.time()
        return
