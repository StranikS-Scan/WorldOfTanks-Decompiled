# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/controller.py
import typing
import async
from BWUtil import AsyncReturn
from gui.platform.base import logger
from gui.platform.base.requester import PlatformRequester
from gui.platform.base.settings import REQUEST_TIMEOUT
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.platform.controller import IPlatformRequestController
if typing.TYPE_CHECKING:
    from gui.platform.base.request import Params

class PlatformRequestController(IPlatformRequestController):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(PlatformRequestController, self).__init__()
        self._requester = None
        self._logger = logger.getWithContext(instance=self)
        return

    def init(self):
        self.connectionMgr.onConnected += self._start
        self.connectionMgr.onDisconnected += self._stop
        self._logger.debug('Initialized.')

    def fini(self):
        self.connectionMgr.onConnected -= self._start
        self.connectionMgr.onDisconnected -= self._stop
        self._logger.debug('Destroyed.')

    @async.async
    def _request(self, params, timeout=REQUEST_TIMEOUT, waitingID=None):
        if self._requester is None:
            self._logger.debug('Not started.')
            response = params.response.createServiceNotStarted()
        else:
            response = yield self._requester.request(params, timeout=timeout, waitingID=waitingID)
        raise AsyncReturn(response)
        return

    def _start(self):
        self._requester = PlatformRequester()
        self._logger.debug('Started.')

    def _stop(self):
        if self._requester:
            self._requester.clear()
        self._requester = None
        self._logger.debug('Stopped.')
        return
