# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/platform/steam.py
from __future__ import absolute_import
import typing
import logging
import Steam
from web.client_web_api.api import C2WHandler, c2w
_logger = logging.getLogger(__name__)

class SteamPlatformEventHandler(C2WHandler):

    def init(self):
        super(SteamPlatformEventHandler, self).init()
        if Steam.isInited():
            Steam.microTxnAuthorizationResponse(self.__onMicroTxnAuthorizationResponse)
            Steam.gameOverlayActivated(self.__onGameOverlayActivated)
        else:
            _logger.error('Steam is not inited')

    def fini(self):
        Steam.microTxnAuthorizationResponse(None)
        Steam.gameOverlayActivated(None)
        super(SteamPlatformEventHandler, self).fini()
        return

    @c2w(name='on_platform_payment')
    def __onMicroTxnAuthorizationResponse(self, appID, orderID, authorized):
        return {'orderID': orderID,
         'authorized': bool(authorized)}

    @c2w(name='on_overlay_activated')
    def __onGameOverlayActivated(self, active):
        return {'isActive': bool(active)}
