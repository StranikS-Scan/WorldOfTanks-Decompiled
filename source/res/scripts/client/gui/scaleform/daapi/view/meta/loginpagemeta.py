# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginPageMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoginPageMeta(DAAPIModule):

    def onLogin(self, user, password, host):
        self._printOverrideError('onLogin')

    def onRegister(self):
        self._printOverrideError('onRegister')

    def onRecovery(self):
        self._printOverrideError('onRecovery')

    def onSetRememberPassword(self, remember):
        self._printOverrideError('onSetRememberPassword')

    def onExitFromAutoLogin(self):
        self._printOverrideError('onExitFromAutoLogin')

    def doUpdate(self):
        self._printOverrideError('doUpdate')

    def isToken(self):
        self._printOverrideError('isToken')

    def resetToken(self):
        self._printOverrideError('resetToken')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def isPwdInvalid(self, password):
        self._printOverrideError('isPwdInvalid')

    def isLoginInvalid(self, login):
        self._printOverrideError('isLoginInvalid')

    def showLegal(self):
        self._printOverrideError('showLegal')

    def as_setDefaultValuesS(self, loginName, pwd, rememberPwd, rememberPwdVisible, isIgrCredentialsReset, showRecoveryLink):
        if self._isDAAPIInited():
            return self.flashObject.as_setDefaultValues(loginName, pwd, rememberPwd, rememberPwdVisible, isIgrCredentialsReset, showRecoveryLink)

    def as_setErrorMessageS(self, msg, errorCode):
        if self._isDAAPIInited():
            return self.flashObject.as_setErrorMessage(msg, errorCode)

    def as_setServersListS(self, servers, selectedIdx):
        if self._isDAAPIInited():
            return self.flashObject.as_setServersList(servers, selectedIdx)

    def as_setVersionS(self, version):
        if self._isDAAPIInited():
            return self.flashObject.as_setVersion(version)

    def as_setCopyrightS(self, copyrightVal, legalInfo):
        if self._isDAAPIInited():
            return self.flashObject.as_setCopyright(copyrightVal, legalInfo)

    def as_showWallpaperS(self, isShow, path):
        if self._isDAAPIInited():
            return self.flashObject.as_showWallpaper(isShow, path)

    def as_setCapsLockStateS(self, isActive):
        if self._isDAAPIInited():
            return self.flashObject.as_setCapsLockState(isActive)

    def as_setKeyboardLangS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setKeyboardLang(value)

    def as_cancelLoginQueueS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_cancelLoginQueue()

    def as_doAutoLoginS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_doAutoLogin()

    def as_enableS(self, enabled):
        if self._isDAAPIInited():
            return self.flashObject.as_enable(enabled)
