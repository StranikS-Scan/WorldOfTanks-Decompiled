# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/base_mode.py
import weakref
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
from view_background import ViewBackground

class INVALID_FIELDS(object):
    ALL_VALID = 0
    LOGIN_INVALID = 1
    PWD_INVALID = 2
    SERVER_INVALID = 4
    LOGIN_PWD_INVALID = LOGIN_INVALID | PWD_INVALID


class BaseMode(object):
    _loginManager = dependency.descriptor(ILoginManager)

    def __init__(self, view, fallbackMode=None):
        self._view = weakref.proxy(view)
        self._fallbackMode = fallbackMode
        self._viewBackground = None
        return

    def init(self):
        pass

    def destroy(self):
        if self._viewBackground is not None:
            self._viewBackground.hide()
            self._viewBackground = None
        self._view = None
        self._fallbackMode = None
        return

    @property
    def login(self):
        raise NotImplementedError

    def doLogin(self, *args):
        raise NotImplementedError

    def updateForm(self):
        raise NotImplementedError

    @property
    def rememberUser(self):
        return False

    @property
    def password(self):
        pass

    @property
    def rememberPassVisible(self):
        return False

    def setRememberPassword(self, *args):
        pass

    def isToken2(self):
        return False

    def resetToken(self):
        pass

    def doSocialLogin(self, *args):
        pass

    def changeAccount(self):
        pass

    def skipRejectionError(self, *args):
        return False

    def switchBgMode(self):
        if self._viewBackground is not None:
            self._viewBackground.switch()
        elif self._fallbackMode is not None:
            self._fallbackMode.switchBgMode()
        return

    def musicFadeOut(self):
        if self._viewBackground is not None:
            self._viewBackground.fadeSound()
        elif self._fallbackMode is not None:
            self._fallbackMode.musicFadeOut()
        return

    def videoLoadingFailed(self):
        if self._viewBackground is not None:
            self._viewBackground.showWallpaper(False)
        elif self._fallbackMode is not None:
            self._fallbackMode.videoLoadingFailed()
        return

    def setMute(self, value):
        if self._viewBackground is not None:
            self._viewBackground.toggleMute(value)
        elif self._fallbackMode is not None:
            self._fallbackMode.setMute(value)
        return

    def onVideoLoaded(self):
        if self._viewBackground is not None:
            self._viewBackground.startVideoSound()
        elif self._fallbackMode is not None:
            self._fallbackMode.onVideoLoaded()
        return

    def _initViewBackground(self):
        self._viewBackground = ViewBackground(self._view)
        self._viewBackground.show()
