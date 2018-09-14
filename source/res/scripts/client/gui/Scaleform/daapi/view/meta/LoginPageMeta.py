# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginPageMeta.py
from gui.Scaleform.framework.entities.View import View

class LoginPageMeta(View):

    def onLogin(self, user, password, host, isSocial):
        self._printOverrideError('onLogin')

    def onRegister(self, host):
        self._printOverrideError('onRegister')

    def onRecovery(self):
        self._printOverrideError('onRecovery')

    def onTextLinkClick(self, linkId):
        self._printOverrideError('onTextLinkClick')

    def onLoginBySocial(self, socialId, host):
        self._printOverrideError('onLoginBySocial')

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

    def isCSISUpdateOnRequest(self):
        self._printOverrideError('isCSISUpdateOnRequest')

    def isPwdInvalid(self, password):
        self._printOverrideError('isPwdInvalid')

    def isLoginInvalid(self, login):
        self._printOverrideError('isLoginInvalid')

    def showLegal(self):
        self._printOverrideError('showLegal')

    def startListenCsisUpdate(self, startListenCsis):
        self._printOverrideError('startListenCsisUpdate')

    def saveLastSelectedServer(self, server):
        self._printOverrideError('saveLastSelectedServer')

    def changeAccount(self):
        self._printOverrideError('changeAccount')

    def as_setDefaultValuesS(self, loginName, pwd, rememberPwd, rememberPwdVisible, isIgrCredentialsReset, showRecoveryLink):
        return self.flashObject.as_setDefaultValues(loginName, pwd, rememberPwd, rememberPwdVisible, isIgrCredentialsReset, showRecoveryLink) if self._isDAAPIInited() else None

    def as_setErrorMessageS(self, msg, errorCode):
        return self.flashObject.as_setErrorMessage(msg, errorCode) if self._isDAAPIInited() else None

    def as_setServersListS(self, servers, selectedIdx):
        return self.flashObject.as_setServersList(servers, selectedIdx) if self._isDAAPIInited() else None

    def as_setVersionS(self, version):
        return self.flashObject.as_setVersion(version) if self._isDAAPIInited() else None

    def as_setCopyrightS(self, copyrightVal, legalInfo):
        return self.flashObject.as_setCopyright(copyrightVal, legalInfo) if self._isDAAPIInited() else None

    def as_showWallpaperS(self, isShow, path):
        return self.flashObject.as_showWallpaper(isShow, path) if self._isDAAPIInited() else None

    def as_setCapsLockStateS(self, isActive):
        return self.flashObject.as_setCapsLockState(isActive) if self._isDAAPIInited() else None

    def as_setKeyboardLangS(self, value):
        return self.flashObject.as_setKeyboardLang(value) if self._isDAAPIInited() else None

    def as_doAutoLoginS(self):
        return self.flashObject.as_doAutoLogin() if self._isDAAPIInited() else None

    def as_enableS(self, enabled):
        return self.flashObject.as_enable(enabled) if self._isDAAPIInited() else None

    def as_switchToAutoAndSubmitS(self, key):
        return self.flashObject.as_switchToAutoAndSubmit(key) if self._isDAAPIInited() else None

    def as_showSimpleFormS(self, isShow, socialList):
        return self.flashObject.as_showSimpleForm(isShow, socialList) if self._isDAAPIInited() else None

    def as_showSocialFormS(self, haveToken, userName, icoPath, socialId):
        return self.flashObject.as_showSocialForm(haveToken, userName, icoPath, socialId) if self._isDAAPIInited() else None

    def as_resetPasswordS(self):
        return self.flashObject.as_resetPassword() if self._isDAAPIInited() else None
