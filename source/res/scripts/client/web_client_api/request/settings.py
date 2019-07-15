# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/request/settings.py
import helpers
from web_client_api import W2CSchema, w2c

class SettingsWebApiMixin(object):

    @w2c(W2CSchema, 'settings')
    def getSettings(self, _):
        return {'client_version': helpers.getClientVersion()}
