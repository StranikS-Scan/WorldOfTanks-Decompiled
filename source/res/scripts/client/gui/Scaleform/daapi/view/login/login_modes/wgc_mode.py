# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/wgc_mode.py
import BigWorld
from gui.Scaleform.locale.MENU import MENU
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GAME
from base_mode import BaseMode
from predefined_hosts import g_preDefinedHosts
_g_firstEntry = True

class WgcMode(BaseMode):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, wgcStoredUserSelected, *args):
        super(WgcMode, self).__init__(*args)
        self.__wgcStoredUserSelected = wgcStoredUserSelected
        self._fallbackMode.setRememberPassword(False)

    @property
    def login(self):
        return BigWorld.WGC_getUserName() if self.__wgcStoredUserSelected else ''

    def init(self):
        global _g_firstEntry
        self._loginManager.addOnWgcErrorListener(self.__onWgcError)
        if self.__wgcStoredUserSelected:
            if _g_firstEntry and not self._settingsCore.getSetting(GAME.LOGIN_SERVER_SELECTION):
                self._loginManager.tryWgcLogin()
                g_preDefinedHosts.resetPingResult()
            _g_firstEntry = False
        else:
            self._fallbackMode.init()

    def destroy(self):
        self._loginManager.removeOnWgcErrorListener(self.__onWgcError)
        self._fallbackMode.destroy()
        super(WgcMode, self).destroy()

    def updateForm(self):
        if self.__wgcStoredUserSelected:
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

    def doLogin(self, *args):
        if self.__wgcStoredUserSelected:
            self._loginManager.tryWgcLogin()
        elif self._fallbackMode is not None:
            self._fallbackMode.doLogin(*args)
        return

    def doSocialLogin(self, *args):
        self._fallbackMode.doSocialLogin(*args)

    def __onWgcError(self):
        self.__stop()
        self._view.as_setLoginWarningS(_ms(MENU.LOGIN_SOCIAL_STATUS_WGC_ERROR))
        g_preDefinedHosts.requestPing()

    def __stop(self):
        if self.__wgcStoredUserSelected:
            self.__wgcStoredUserSelected = False
            self._view.update()
            self._fallbackMode.init()
