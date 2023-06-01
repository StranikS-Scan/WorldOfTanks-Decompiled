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

    def onLoginNameUpdated(self):
        self._printOverrideError('onLoginNameUpdated')

    def isToken(self):
        self._printOverrideError('isToken')

    def resetToken(self):
        self._printOverrideError('resetToken')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def isCSISUpdateOnRequest(self):
        self._printOverrideError('isCSISUpdateOnRequest')

    def startListenCsisUpdate(self, startListenCsis):
        self._printOverrideError('startListenCsisUpdate')

    def showLegal(self):
        self._printOverrideError('showLegal')

    def changeAccount(self):
        self._printOverrideError('changeAccount')

    def as_setDefaultValuesS(self, data):
        return self.flashObject.as_setDefaultValues(data) if self._isDAAPIInited() else None

    def as_setErrorMessageS(self, msg, errorCode):
        return self.flashObject.as_setErrorMessage(msg, errorCode) if self._isDAAPIInited() else None

    def as_setVersionS(self, version):
        return self.flashObject.as_setVersion(version) if self._isDAAPIInited() else None

    def as_setCopyrightS(self, copyrightVal, legalInfo):
        return self.flashObject.as_setCopyright(copyrightVal, legalInfo) if self._isDAAPIInited() else None

    def as_setLoginWarningS(self, value):
        return self.flashObject.as_setLoginWarning(value) if self._isDAAPIInited() else None

    def as_setLoginWarningHideS(self):
        return self.flashObject.as_setLoginWarningHide() if self._isDAAPIInited() else None

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

    def as_showSimpleFormS(self, isShow, socialList, showRegisterLink):
        return self.flashObject.as_showSimpleForm(isShow, socialList, showRegisterLink) if self._isDAAPIInited() else None

    def as_showFilledLoginFormS(self, data):
        return self.flashObject.as_showFilledLoginForm(data) if self._isDAAPIInited() else None

    def as_showSteamLoginFormS(self, data):
        return self.flashObject.as_showSteamLoginForm(data) if self._isDAAPIInited() else None

    def as_resetPasswordS(self):
        return self.flashObject.as_resetPassword() if self._isDAAPIInited() else None

    def as_getServersDPS(self):
        return self.flashObject.as_getServersDP() if self._isDAAPIInited() else None

    def as_setSelectedServerIndexS(self, serverIndex):
        return self.flashObject.as_setSelectedServerIndex(serverIndex) if self._isDAAPIInited() else None

    def as_showHealthNoticeS(self, text):
        return self.flashObject.as_showHealthNotice(text) if self._isDAAPIInited() else None
