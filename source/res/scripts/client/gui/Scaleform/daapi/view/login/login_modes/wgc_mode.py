# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/wgc_mode.py
import WGC
from constants import IS_CHINA
from gui.Scaleform.locale.MENU import MENU
from gui.impl import backport
from gui.impl.gen import R
from helpers.i18n import makeString as _ms
from base_wgc_mode import BaseWgcMode
from predefined_hosts import g_preDefinedHosts

class WgcMode(BaseWgcMode):

    def __init__(self, *args):
        super(WgcMode, self).__init__(*args)
        self.__wgcStoredUserSelected = True
        self._fallbackMode.setRememberPassword(False)
        self._fallbackMode.resetToken()

    @property
    def login(self):
        return super(WgcMode, self).login if self.__wgcStoredUserSelected else ''

    def onPopulate(self):
        if self.__wgcStoredUserSelected:
            super(WgcMode, self).onPopulate()
        else:
            self._fallbackMode.onPopulate()

    def destroy(self):
        self._fallbackMode.destroy()
        super(WgcMode, self).destroy()

    def updateForm(self):
        if self.__wgcStoredUserSelected:
            if IS_CHINA:
                self._view.as_showHealthNoticeS(backport.text(R.strings.menu.login.healthNotice()))
            self._view.as_showFilledLoginFormS({'haveToken': True,
             'userName': WGC.getUserName(),
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
            super(WgcMode, self).doLogin(userName, password, serverName, isSocialToken2Login)
        else:
            self._fallbackMode.doLogin(userName, password, serverName, isSocialToken2Login)

    def doSocialLogin(self, *args):
        self._fallbackMode.doSocialLogin(*args)

    def skipRejectionError(self, loginStatus):
        return super(WgcMode, self).skipRejectionError(loginStatus) if self.__wgcStoredUserSelected else self._fallbackMode.skipRejectionError(loginStatus)

    def _onWgcError(self):
        self.__stop()
        self._view.as_setLoginWarningS(_ms(MENU.LOGIN_SOCIAL_STATUS_WGC_ERROR))
        g_preDefinedHosts.requestPing()

    def __stop(self):
        self._loginManager.stopWgc()
        if self.__wgcStoredUserSelected:
            self.__wgcStoredUserSelected = False
            self._view.update()
            self._fallbackMode.init()
