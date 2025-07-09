# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/lgc_mode.py
import LGC
from constants import IS_CHINA
from gui.Scaleform.locale.MENU import MENU
from gui.impl import backport
from gui.impl.gen import R
from helpers.i18n import makeString as _ms
from base_lgc_mode import BaseLgcMode
from predefined_hosts import g_preDefinedHosts

class LgcMode(BaseLgcMode):

    def __init__(self, *args):
        super(LgcMode, self).__init__(*args)
        self.__lgcStoredUserSelected = True
        self._fallbackMode.setRememberPassword(False)
        self._fallbackMode.resetToken()

    @property
    def login(self):
        return super(LgcMode, self).login if self.__lgcStoredUserSelected else ''

    def onPopulate(self):
        if self.__lgcStoredUserSelected:
            super(LgcMode, self).onPopulate()
        else:
            self._fallbackMode.onPopulate()

    def destroy(self):
        self._fallbackMode.destroy()
        super(LgcMode, self).destroy()

    def updateForm(self):
        if self.__lgcStoredUserSelected:
            if IS_CHINA:
                self._view.as_showHealthNoticeS(backport.text(R.strings.menu.login.healthNotice()))
            self._view.as_showFilledLoginFormS({'haveToken': True,
             'userName': LGC.getUserName(),
             'icoPath': '',
             'socialId': ''})
        else:
            self._fallbackMode.updateForm()

    def changeAccount(self):
        if self.__lgcStoredUserSelected:
            message = _ms('#menu:login/status/LGC_LOGOUT', userName=self.login)
            self.__stop()
            self._view.as_setLoginWarningS(message)
        else:
            self._fallbackMode.changeAccount()

    def doLogin(self, userName, password, serverName, isSocialToken2Login):
        if self.__lgcStoredUserSelected:
            super(LgcMode, self).doLogin(userName, password, serverName, isSocialToken2Login)
        else:
            self._fallbackMode.doLogin(userName, password, serverName, isSocialToken2Login)

    def doSocialLogin(self, *args):
        self._fallbackMode.doSocialLogin(*args)

    def skipRejectionError(self, loginStatus):
        return super(LgcMode, self).skipRejectionError(loginStatus) if self.__lgcStoredUserSelected else self._fallbackMode.skipRejectionError(loginStatus)

    def _onLgcError(self):
        self.__stop()
        self._view.as_setLoginWarningS(_ms(MENU.LOGIN_SOCIAL_STATUS_LGC_ERROR))
        g_preDefinedHosts.requestPing()

    def __stop(self):
        self._loginManager.stopLgc()
        if self.__lgcStoredUserSelected:
            self.__lgcStoredUserSelected = False
            self._view.update()
            self._fallbackMode.onPopulate()
