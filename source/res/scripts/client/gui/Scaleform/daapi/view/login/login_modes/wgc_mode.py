# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/wgc_mode.py
import BigWorld
from constants import IS_CHINA
from gui.Scaleform.locale.MENU import MENU
from gui.impl import backport
from gui.impl.gen import R
from helpers.i18n import makeString as _ms
from account_helpers.settings_core.settings_constants import GAME
from base_mode import BaseMode
from predefined_hosts import g_preDefinedHosts
_g_firstEntry = True

class WgcMode(BaseMode):

    def __init__(self, *args):
        super(WgcMode, self).__init__(*args)
        self.__wgcStoredUserSelected = True
        self._fallbackMode.setRememberPassword(False)
        self._fallbackMode.resetToken()

    @property
    def login(self):
        return BigWorld.WGC_getUserName() if self.__wgcStoredUserSelected else ''

    @property
    def showRememberServerWarning(self):
        return not self._loginManager.settingsCore.getSetting(GAME.LOGIN_SERVER_SELECTION) and self._loginManager.getPreference('server_select_was_set')

    def init(self):
        global _g_firstEntry
        self._loginManager.addOnWgcErrorListener(self.__onWgcError)
        if self.__wgcStoredUserSelected:
            autoLogin = _g_firstEntry and not self._loginManager.settingsCore.getSetting(GAME.LOGIN_SERVER_SELECTION) and not self._loginManager.getPreference('server_select_was_set')
            if autoLogin:
                self._loginManager.tryWgcLogin()
            _g_firstEntry = False
        else:
            self._fallbackMode.init()

    def destroy(self):
        self._loginManager.removeOnWgcErrorListener(self.__onWgcError)
        self._fallbackMode.destroy()
        super(WgcMode, self).destroy()

    def updateForm(self):
        if self.__wgcStoredUserSelected:
            if IS_CHINA:
                self._view.as_showHealthNoticeS(backport.text(R.strings.menu.login.healthNotice()))
            self._view.as_showFilledLoginFormS({'haveToken': True,
             'userName': BigWorld.WGC_getUserName(),
             'icoPath': '',
             'socialId': ''})
        else:
            self._fallbackMode.updateForm()

    def changeAccount(self):
        if self.__wgcStoredUserSelected:
            message = _ms('#menu:login/status/WGC_LOGOUT', userName=self.login)
            self.__stop()
            self._view.as_setLoginWarningS(message)
        else:
            self._fallbackMode.changeAccount()

    def doLogin(self, userName, password, serverName, isSocialToken2Login):
        if self.__wgcStoredUserSelected:
            self._loginManager.tryWgcLogin(serverName)
        else:
            self._fallbackMode.doLogin(userName, password, serverName, isSocialToken2Login)

    def doSocialLogin(self, *args):
        self._fallbackMode.doSocialLogin(*args)

    def skipRejectionError(self, loginStatus):
        return self._loginManager.checkWgcCouldRetry(loginStatus) if self.__wgcStoredUserSelected else self._fallbackMode.skipRejectionError(loginStatus)

    def __onWgcError(self):
        self.__stop()
        self._view.as_setLoginWarningS(_ms(MENU.LOGIN_SOCIAL_STATUS_WGC_ERROR))
        g_preDefinedHosts.requestPing()

    def __stop(self):
        self._loginManager.stopWgc()
        if self.__wgcStoredUserSelected:
            self.__wgcStoredUserSelected = False
            self._view.update()
            self._fallbackMode.init()
