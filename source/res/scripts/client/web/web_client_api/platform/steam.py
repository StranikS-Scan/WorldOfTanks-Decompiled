# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/platform/steam.py
from __future__ import absolute_import
import logging
import Steam
from constants import DISTRIBUTION_PLATFORM
from web.web_client_api.platform.base import IPlatformWebApi
_logger = logging.getLogger(__name__)

class SteamPlatformWebApi(IPlatformWebApi):

    def getType(self):
        return DISTRIBUTION_PLATFORM.STEAM.value

    def isInited(self):
        return Steam.isInited()

    def isConnected(self):
        return Steam.isInited()

    @staticmethod
    def isOverlayEnabled():
        return Steam.isOverlayEnabled()
