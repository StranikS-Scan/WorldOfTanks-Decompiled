# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginPageMeta.py
from gui.Scaleform.framework.entities.View import View

class LoginPageMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

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

    def switchBgMode(self):
        self._printOverrideError('switchBgMode')

    def setMute(self, value):
        self._printOverrideError('setMute')

    def onVideoLoaded(self):
        self._printOverrideError('onVideoLoaded')

    def musicFadeOut(self):
        self._printOverrideError('musicFadeOut')

    def as_setDefaultValuesS(self, loginName, pwd, rememberPwd, rememberPwdVisible, isIgrCredentialsReset, showRecoveryLink):
        return self.flashObject.as_setDefaultValues(loginName, pwd, rememberPwd, rememberPwdVisible, isIgrCredentialsReset, showRecoveryLink) if self._isDAAPIInited() else None

    def as_setErrorMessageS(self, msg, errorCode):
        return self.flashObject.as_setErrorMessage(msg, errorCode) if self._isDAAPIInited() else None

    def as_setVersionS(self, version):
        return self.flashObject.as_setVersion(version) if self._isDAAPIInited() else None

    def as_setCopyrightS(self, copyrightVal, legalInfo):
        return self.flashObject.as_setCopyright(copyrightVal, legalInfo) if self._isDAAPIInited() else None

    def as_showWallpaperS(self, isShow, path, showSwitcher, isMuted):
        return self.flashObject.as_showWallpaper(isShow, path, showSwitcher, isMuted) if self._isDAAPIInited() else None

    def as_showLoginVideoS(self, path, bufferTime, isMuted):
        return self.flashObject.as_showLoginVideo(path, bufferTime, isMuted) if self._isDAAPIInited() else None

    def as_setCapsLockStateS(self, isActive):
        return self.flashObject.as_setCapsLockState(isActive) if self._isDAAPIInited() else None

    def as_pausePlaybackS(self):
        return self.flashObject.as_pausePlayback() if self._isDAAPIInited() else None

    def as_resumePlaybackS(self):
        return self.flashObject.as_resumePlayback() if self._isDAAPIInited() else None

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

    def as_getServersDPS(self):
        return self.flashObject.as_getServersDP() if self._isDAAPIInited() else None

    def as_setSelectedServerIndexS(self, serverIndex):
        return self.flashObject.as_setSelectedServerIndex(serverIndex) if self._isDAAPIInited() else None
