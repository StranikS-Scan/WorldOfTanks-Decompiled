# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/promo/promo_logger.py
import logging
from functools import partial
import BigWorld
from adisp import adisp_process
from gui.macroses import getLanguageCode
from gui.wgcg.promo_screens.contexts import PromoSendActionLogCtx
from helpers import dependency, isPlayerAccount, time_utils
from ids_generators import Int32IDGenerator
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.promo import IPromoLogger
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class PromoLogActions(CONST_CONTAINER):
    RECEIVED_WGNC = 'ReceivedWGNC'
    GET_MOST_IMPORTANT = 'GetMostImportant'
    OPEN_FROM_TEASER = 'OpenFromTeaser'
    CLOSED_BY_USER = 'ClosedByUser'
    KILLED_BY_SYSTEM = 'KilledBySystem'
    OPEN_FROM_MENU = 'OpenFromMenu'
    OPEN_IN_OLD = 'OpenInOld'


class PromoLogSubjectType(CONST_CONTAINER):
    TEASER = 'Teaser'
    PROMO_SCREEN = 'Promoscreen'
    INDEX = 'Index'
    PROMO_SCREEN_OR_INDEX = 'PromoscreenOrIndex'


class PromoLogSourceType(CONST_CONTAINER):
    WGNC = 'WGNC'
    FIRST_LOGIN = 'Firstlogin'
    AFTER_BATTLE = '10stBattle'
    PRMP = 'PRMP'
    SSE = 'SSE'


def _getPlayerDatabaseID():
    return BigWorld.player().databaseID if isPlayerAccount() else None


class PromoLogger(IPromoLogger):
    __PARAMS_MAP = {'action': {'set': PromoLogActions.ALL()},
     'type': {'set': PromoLogSubjectType.ALL(),
              'default': PromoLogSubjectType.TEASER},
     'teaserid': {},
     'slug': {},
     'spaid': {'default': _getPlayerDatabaseID},
     'time': {'default': time_utils.getCurrentTimestamp},
     'success': {},
     'lang': {'default': getLanguageCode},
     'source': {'set': PromoLogSourceType.ALL()},
     'url': {}}
    __TEASER_PARAMS_MAP = {'promoID': 'teaserid',
     'url': 'url',
     'slug': 'slug'}
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __webController = dependency.descriptor(IWebController)
    __ANSWER_WAITING_TIME = 30
    __IDGenerator = Int32IDGenerator()

    def __init__(self):
        self.__requestIDs = {}

    @adisp_process
    def logAction(self, **kwargs):
        if self.__isEnabled():
            ctx = PromoSendActionLogCtx(self.__packData(kwargs))
            yield self.__webController.sendRequest(ctx=ctx)

    def logTeaserAction(self, teaserData, **kwargs):
        dataToSend = kwargs.copy()
        if teaserData:
            for sourceName, targetName in self.__TEASER_PARAMS_MAP.iteritems():
                dataToSend[targetName] = teaserData.get(sourceName)

        self.logAction(**dataToSend)

    def getLoggingFuture(self, teaserData=None, **kwargs):
        if not self.__isEnabled():
            return None
        else:
            requestID = self.__IDGenerator.next()
            callbackID = BigWorld.callback(self.__ANSWER_WAITING_TIME, partial(self.__sendDelayed, teaserData, requestID, **kwargs))
            self.__requestIDs[requestID] = callbackID
            return partial(self.__sendDelayed, teaserData, requestID, callbackID, **kwargs)

    def fini(self):
        for requestID, callbackID in self.__requestIDs.items():
            BigWorld.cancelCallback(callbackID)
            del self.__requestIDs[requestID]

    def __isEnabled(self):
        return self.__lobbyContext.getServerSettings().isPromoLoggingEnabled()

    def __sendDelayed(self, teaserData, requestID, callbackID=None, **kwargs):
        if requestID in self.__requestIDs:
            del self.__requestIDs[requestID]
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)
            success = kwargs.pop('success', None)
            if teaserData is not None:
                self.logTeaserAction(teaserData, success=success, **kwargs)
            else:
                self.logAction(success=success, **kwargs)
        return

    def __packData(self, data):
        result = {}
        for paramName, settings in self.__PARAMS_MAP.iteritems():
            if paramName in data:
                value = data[paramName]
                possibleValues = settings.get('set')
                if possibleValues and value not in possibleValues:
                    _logger.error('Wrong value for enumerable %s', paramName)
                    continue
                result[paramName] = value
            if 'default' in settings:
                default = settings['default']
                result[paramName] = default() if callable(default) else default

        return result
