# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/base_lgc_mode.py
import LGC
from account_helpers.settings_core.settings_constants import GAME
from base_mode import BaseMode
_g_firstEntry = True

class BaseLgcMode(BaseMode):

    @property
    def login(self):
        return LGC.getUserName()

    @property
    def showRememberServerWarning(self):
        return not self._loginManager.settingsCore.getSetting(GAME.LOGIN_SERVER_SELECTION) and self._loginManager.getPreference('server_select_was_set')

    def onPopulate(self):
        global _g_firstEntry
        if self._loginManager.lgcAvailable:
            self._loginManager.addOnLgcErrorListener(self._onLgcError)
        autoLogin = _g_firstEntry and not self._loginManager.settingsCore.getSetting(GAME.LOGIN_SERVER_SELECTION) and not self._loginManager.getPreference('server_select_was_set')
        if autoLogin:
            self._loginManager.tryLgcLogin()
        _g_firstEntry = False

    def doLogin(self, userName, password, serverName, isSocialToken2Login):
        self._loginManager.tryLgcLogin(serverName)

    def skipRejectionError(self, loginStatus):
        return self._loginManager.checkLgcCouldRetry(loginStatus)

    def updateForm(self):
        pass

    def destroy(self):
        if self._loginManager.lgcAvailable:
            self._loginManager.removeOnLgcErrorListener(self._onLgcError)
        super(BaseLgcMode, self).destroy()

    def _onLgcError(self):
        pass
