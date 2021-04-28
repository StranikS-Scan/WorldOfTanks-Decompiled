# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/platform/china360.py
from constants import DISTRIBUTION_PLATFORM
from web.web_client_api.platform.base import IPlatformWebApi

class China360PlatformWebApi(IPlatformWebApi):

    def getType(self):
        return DISTRIBUTION_PLATFORM.CHINA_360.value

    def isInited(self):
        return True

    def isConnected(self):
        return True
