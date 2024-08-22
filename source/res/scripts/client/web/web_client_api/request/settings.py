# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/request/settings.py
import helpers
from gui.limited_ui.lui_rules_storage import LUI_RULES
from helpers import dependency
from skeletons.gui.game_control import ILimitedUIController
from web.web_client_api import W2CSchema, w2c

class SettingsWebApiMixin(object):
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    _MODE_HIDE_COUNTERS = 'hide_counters'

    @w2c(W2CSchema, 'settings')
    def getSettings(self, _):
        return {'client_version': helpers.getClientVersion(),
         'ui_spam_mode': '' if self.__limitedUIController.isRuleCompleted(LUI_RULES.store) else self._MODE_HIDE_COUNTERS}
