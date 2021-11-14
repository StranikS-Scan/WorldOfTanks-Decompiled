# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/base/controller.py
import typing
import async
from BWUtil import AsyncReturn
from gui.platform.base.controller import PlatformRequestController
from gui.platform.base.settings import REQUEST_TIMEOUT
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controllers import IWGNPRequestController
if typing.TYPE_CHECKING:
    from gui.platform.base.request import Params
    from helpers.server_settings import _Wgnp

class WGNPRequestController(PlatformRequestController, IWGNPRequestController):
    lobbyContext = dependency.descriptor(ILobbyContext)

    @property
    def settings(self):
        return self.lobbyContext.getServerSettings().wgnp

    @async.async
    def _request(self, params, timeout=REQUEST_TIMEOUT, waitingID=None):
        if not self.settings.isEnabled():
            self._logger.debug('WGNP disabled.')
            response = params.response.createServiceDisabled()
        else:
            response = yield super(WGNPRequestController, self)._request(params, timeout=timeout, waitingID=waitingID)
        raise AsyncReturn(response)
