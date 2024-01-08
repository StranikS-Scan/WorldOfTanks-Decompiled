# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/web_season_provider.py
from collections import namedtuple
import logging
import time
import BigWorld
import Event
import constants
from adisp import adisp_process
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.web import IWebController
from gui.wgcg.rank.contexts import RankedPositionCtx
_logger = logging.getLogger(__name__)
_WEB_AVAILABLE_SYNC_TIME = 2
_LEAGUE_SYNC_TIME = 2 * ONE_MINUTE
WebSeasonInfo = namedtuple('WebSeasonInfo', 'league, position, isSprinter, isTop')
UNDEFINED_LEAGUE_ID = 0
UNDEFINED_WEB_INFO = WebSeasonInfo(UNDEFINED_LEAGUE_ID, None, False, False)
TOP_LEAGUE_ID = 1

class RankedWebSeasonProvider(object):
    __webController = dependency.descriptor(IWebController)
    __slots__ = ('onInfoUpdated', '__isStarted', '__callbackID', '__lastUpdateTime', '__webSeasonInfo', '__fakeInfo')

    def __init__(self):
        super(RankedWebSeasonProvider, self).__init__()
        self.onInfoUpdated = Event.Event()
        self.__isStarted = False
        self.__callbackID = None
        self.__lastUpdateTime = None
        self.__webSeasonInfo = UNDEFINED_WEB_INFO
        self.__fakeInfo = None
        return

    @property
    def isStarted(self):
        return self.__isStarted

    @property
    def lastUpdateTime(self):
        return self.__lastUpdateTime

    @property
    def seasonInfo(self):
        return self.__webSeasonInfo

    def clear(self):
        self.__fakeInfo = None
        self.__webSeasonInfo = UNDEFINED_WEB_INFO
        self.__lastUpdateTime = None
        return

    def start(self):
        if self.__isStarted:
            return
        self.__isStarted = True
        self.__invoke()

    def stop(self):
        if self.__isStarted:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__isStarted = False
        return

    def _setFakeSeasonInfo(self, league=0, position=None, isSprinter=False, isTop=False):
        if constants.IS_DEVELOPMENT:
            self.__fakeInfo = WebSeasonInfo(league, position, isSprinter, isTop)

    @adisp_process
    def __invoke(self):
        self.__callbackID = None
        if not self.__fakeInfo or not constants.IS_DEVELOPMENT:
            if self.__webController.isAvailable():
                ctx = RankedPositionCtx()
                result = yield self.__webController.sendRequest(ctx)
                if result.isSuccess():
                    results = ctx.getDataObj(result.data).get('results')
                    if results is not None and isinstance(results, dict):
                        self.__webSeasonInfo = WebSeasonInfo(results.get('league', UNDEFINED_LEAGUE_ID), results.get('position'), results.get('isSprinter', False), results.get('isTop', False))
                        self.__lastUpdateTime = time.time()
                        self.onInfoUpdated()
                else:
                    _logger.debug('RankedWebSeasonProvider: response is not success with code %s', result.getCode())
        else:
            self.__webSeasonInfo = self.__fakeInfo
            self.__lastUpdateTime = time.time()
            self.onInfoUpdated()
        if self.isStarted:
            self.__callbackID = BigWorld.callback(self.__getInvokeDelay(), self.__invoke)
        return

    def __getInvokeDelay(self):
        return _LEAGUE_SYNC_TIME if self.__webController.isAvailable() else _WEB_AVAILABLE_SYNC_TIME
