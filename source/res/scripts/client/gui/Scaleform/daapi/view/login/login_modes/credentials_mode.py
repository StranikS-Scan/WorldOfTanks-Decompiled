# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/credentials_mode.py
from collections import namedtuple
import constants
from external_strings_utils import _LOGIN_NAME_MIN_LENGTH
from external_strings_utils import isAccountLoginValid, isPasswordValid, _PASSWORD_MIN_LENGTH, _PASSWORD_MAX_LENGTH
from gui import GUI_SETTINGS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.locale.MENU import MENU
from helpers.i18n import makeString as _ms
from base_mode import BaseMode, INVALID_FIELDS
_ValidateCredentialsResult = namedtuple('ValidateCredentialsResult', ('isValid', 'errorMessage', 'invalidFields'))

class CredentialsMode(BaseMode):

    def __init__(self, *args):
        super(CredentialsMode, self).__init__(*args)
        self._rememberUser = self._loginManager.getPreference('remember_user')

    @property
    def login(self):
        return '' if GUI_SETTINGS.clearLoginValue else self._loginManager.getPreference('login')

    @property
    def rememberUser(self):
        return self._rememberUser

    @property
    def password(self):
        return '*' * self._loginManager.getPreference('password_length') if self._rememberUser and not GUI_SETTINGS.clearLoginValue else ''

    @property
    def rememberPassVisible(self):
        return GUI_SETTINGS.rememberPassVisible

    def init(self):
        self._initViewBackground()

    def setRememberPassword(self, rememberUser):
        self._rememberUser = rememberUser

    def isToken2(self):
        return bool(self._loginManager.getPreference('token2'))

    def resetToken(self):
        self._loginManager.clearToken2Preference()

    def doLogin(self, userName, password, serverName, isSocialToken2Login):
        result = self.__validateCredentials(userName.lower().strip(), password.strip(), self.isToken2())
        if result.isValid:
            Waiting.show('login')
            self._loginManager.initiateLogin(userName, password, serverName, isSocialToken2Login, isSocialToken2Login or self._rememberUser)
        else:
            self._view.as_setErrorMessageS(result.errorMessage, result.invalidFields)
        return True

    def updateForm(self):
        self._view.as_showSimpleFormS(False, None)
        return

    @staticmethod
    def __validateCredentials(userName, password, isToken2Login):
        isValid = True
        errorMessage = None
        invalidFields = None
        if isToken2Login and GUI_SETTINGS.rememberPassVisible or constants.IS_DEVELOPMENT and userName:
            return _ValidateCredentialsResult(isValid, errorMessage, invalidFields)
        else:
            if len(userName) < _LOGIN_NAME_MIN_LENGTH:
                isValid = False
                errorMessage = _ms(MENU.LOGIN_STATUS_INVALID_LOGIN_LENGTH, count=_LOGIN_NAME_MIN_LENGTH)
                invalidFields = INVALID_FIELDS.LOGIN_INVALID
            elif not isAccountLoginValid(userName):
                isValid = False
                errorMessage = _ms(MENU.LOGIN_STATUS_INVALID_LOGIN)
                invalidFields = INVALID_FIELDS.LOGIN_INVALID
            elif not isPasswordValid(password):
                isValid = False
                errorMessage = _ms(MENU.LOGIN_STATUS_INVALID_PASSWORD, minLength=_PASSWORD_MIN_LENGTH, maxLength=_PASSWORD_MAX_LENGTH)
                invalidFields = INVALID_FIELDS.PWD_INVALID
            return _ValidateCredentialsResult(isValid, errorMessage, invalidFields)
