# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/year_position_provider.py
import logging
import BigWorld
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_YEAR_POSITION
from adisp import adisp_process
import constants
from gui.wgcg.rank.contexts import RankedYearPositionCtx
from gui.ranked_battles.constants import YEAR_STRIPE_CLIENT_TOKEN, YEAR_STRIPE_SERVER_TOKEN
from helpers import dependency, isPlayerAccount
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.web import IWebController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_WEB_AVAILABLE_SYNC_TIME = 2
_POSITION_SYNC_TIME = 2 * ONE_MINUTE

class RankedYearPositionProvider(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __webController = dependency.descriptor(IWebController)

    def __init__(self):
        super(RankedYearPositionProvider, self).__init__()
        self.__isStarted = False
        self.__callbackID = None
        self.__yearPosition = None
        self.__fakePosition = None
        return

    @property
    def isStarted(self):
        return self.__isStarted

    @property
    def yearPosition(self):
        return self.__yearPosition

    def start(self):
        if self.__isStarted or not self.__hasServerFinalToken():
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

    def _setFakePosition(self, position):
        if constants.IS_DEVELOPMENT:
            self.__fakePosition = position

    @adisp_process
    def __invoke(self):
        self.__callbackID = None
        if self.__fakePosition is None or not constants.IS_DEVELOPMENT:
            if self.__webController.isAvailable():
                ctx = RankedYearPositionCtx()
                result = yield self.__webController.sendRequest(ctx)
                if result.isSuccess():
                    results = ctx.getDataObj(result.data).get('results')
                    if results is not None and isinstance(results, dict):
                        self.__yearPosition = results.get('position')
                else:
                    _logger.debug('RankedYearPositionProvider: response is not success with code %s', result.getCode())
        else:
            self.__yearPosition = self.__fakePosition
        if self.__isStarted and isPlayerAccount():
            if self.__yearPosition is not None and self.__yearPosition > 0 and self.__hasServerFinalToken():
                AccountSettings.setSettings(RANKED_YEAR_POSITION, self.__yearPosition)
                BigWorld.player().requestSingleToken(YEAR_STRIPE_CLIENT_TOKEN)
            self.__callbackID = BigWorld.callback(self.__getInvokeDelay(), self.__invoke)
        return

    def __getInvokeDelay(self):
        return _POSITION_SYNC_TIME if self.__webController.isAvailable() else _WEB_AVAILABLE_SYNC_TIME

    def __hasServerFinalToken(self):
        token = self.__itemsCache.items.tokens.getTokens().get(YEAR_STRIPE_SERVER_TOKEN)
        return True if token is not None and token[1] > 0 else False
