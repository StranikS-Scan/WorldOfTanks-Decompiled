# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/base_mode.py
import weakref
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager

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

    def onPopulate(self):
        pass

    def destroy(self):
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

    @property
    def showRememberServerWarning(self):
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
