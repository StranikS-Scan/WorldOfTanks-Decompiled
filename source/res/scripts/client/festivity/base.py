# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/base.py
from collections import namedtuple
import logging
from pprint import pformat
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
_logger = logging.getLogger(__name__)

def _defaultLogger(*args):
    msg = pformat(args)
    _logger.debug('[SERVER CMD RESPONSE]:%s', msg)


def _getProxy(callback):
    return (lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)) if callback is not None else None


FestivityQuestsHangarFlag = namedtuple('FestivityQuestsHangarFlag', 'icon, iconDisabled, flagBackground')

class BaseFestivityRequester(AbstractSyncDataRequester):
    dataKey = None

    @async
    def _requestCache(self, callback):
        BigWorld.player().festivities.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        festivityData = data.get(self.dataKey, {})
        return dict(festivityData)


class BaseFestivityProcessor(object):

    def __init__(self):
        super(BaseFestivityProcessor, self).__init__()
        self.__commandProxy = None
        return

    def setCommandProxy(self, account):
        self.__commandProxy = account

    def _perform(self, command, argsList, callback=None):
        cmdArgs = argsList + (_getProxy(callback) if callback else _defaultLogger,)
        self.__commandProxy.perform(command, *cmdArgs)
