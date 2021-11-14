# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/common/field_presenters.py
import re
from abc import ABCMeta, abstractmethod
import typing
from Event import Event
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_email_model import FieldEmailModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_password_model import FieldPasswordModel
from gui.impl.lobby.account_completion.common import errors
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_completion.common.base_field_model import BaseFieldModel
_EMAIL_PATTERN = re.compile('^[a-z0-9_-]+(\\.[a-z0-9_-]+)*@([a-z0-9]([a-z0-9-]*[a-z0-9])?\\.)+[a-z]{2,4}$', re.I)
_PASSWORD_PATTERN = re.compile('^[a-z0-9_]+$', re.I)

class BaseFieldPresenter(object):
    __metaclass__ = ABCMeta
    __slots__ = ('_value', '_viewModel', 'onValueChanged', 'onFocusLost')

    def __init__(self, viewModel):
        super(BaseFieldPresenter, self).__init__()
        viewModel.onChange += self.__valueChangeHandler
        viewModel.onLostFocus += self.__lostFocusChangeHandler
        self._value = ''
        self._viewModel = viewModel
        self.onValueChanged = Event()
        self.onFocusLost = Event()

    @property
    def viewModel(self):
        return self._viewModel

    @property
    def value(self):
        return self._value

    @property
    def isValid(self):
        return not self._viewModel.getErrorMessage()

    def clear(self):
        self.setValue('')
        self.viewModel.setErrorMessage('')

    def setValue(self, value):
        self._value = value
        self.viewModel.setValue(value)

    def dispose(self):
        self._viewModel.onChange -= self.__valueChangeHandler
        self._viewModel.onLostFocus -= self.__lostFocusChangeHandler
        self._viewModel = None
        return

    def validate(self):
        self._validateChangedValue()
        if self.isValid:
            self._validateValueWhenFocusChanged()
        return self.isValid

    @abstractmethod
    def _validateChangedValue(self):
        raise NotImplementedError

    @abstractmethod
    def _validateValueWhenFocusChanged(self):
        raise NotImplementedError

    def __valueChangeHandler(self, args):
        self._value = args.get('value', '')
        self._validateChangedValue()
        self.onValueChanged()

    def __lostFocusChangeHandler(self):
        if self.isValid and self._value:
            self._validateValueWhenFocusChanged()
        self.onFocusLost()


class EmailPresenter(BaseFieldPresenter):
    __slots__ = ()

    def __init__(self, viewModel):
        super(EmailPresenter, self).__init__(viewModel)
        self.viewModel.setName(R.strings.dialogs.accountCompletion.email.fieldName())
        self.viewModel.setPlaceholder(backport.text(R.strings.dialogs.accountCompletion.email.fieldPlaceholder()))

    @property
    def viewModel(self):
        return self._viewModel

    def _validateChangedValue(self):
        with self.viewModel.transaction() as vm:
            vm.setErrorTime(0)
            if len(self._value) > FieldEmailModel.EMAIL_LEN_MAX:
                vm.setErrorMessage(errors.emailIsTooLong())
            else:
                vm.setErrorMessage('')

    def _validateValueWhenFocusChanged(self):
        if len(self._value) < FieldEmailModel.EMAIL_LEN_MIN:
            self.viewModel.setErrorMessage(errors.emailIsTooShort())
        elif not _EMAIL_PATTERN.match(self._value):
            self.viewModel.setErrorMessage(errors.emailIsInvalid())


class PasswordPresenter(BaseFieldPresenter):
    __slots__ = ('onPasswordVisibilityChanged', '_isPasswordVisible', '_wasPasswordVisibilityChanged')

    def __init__(self, viewModel):
        super(PasswordPresenter, self).__init__(viewModel)
        self.onPasswordVisibilityChanged = Event()
        self._isPasswordVisible = False
        self._wasPasswordVisibilityChanged = False
        viewModel.setName(R.strings.dialogs.accountCompletion.password.fieldName())
        viewModel.setIsPasswordVisible(self._isPasswordVisible)
        viewModel.onEyeClicked += self._eyeClickHandler

    def dispose(self):
        self.viewModel.onEyeClicked -= self._eyeClickHandler
        super(PasswordPresenter, self).dispose()

    @property
    def viewModel(self):
        return self._viewModel

    @property
    def isPasswordVisible(self):
        return self._isPasswordVisible

    @property
    def wasPasswordVisibilityChanged(self):
        return self._wasPasswordVisibilityChanged

    def clear(self):
        self._isPasswordVisible = False
        self._wasPasswordVisibilityChanged = False
        super(PasswordPresenter, self).clear()

    def _validateChangedValue(self):
        if self.value and not _PASSWORD_PATTERN.match(self.value):
            self.viewModel.setErrorMessage(errors.passwordIsInvalid())
        elif len(self.value) > FieldPasswordModel.PASSWORD_LEN_MAX:
            self.viewModel.setErrorMessage(errors.passwordIsTooLong())
        else:
            self.viewModel.setErrorMessage('')

    def _validateValueWhenFocusChanged(self):
        if len(self._value) < FieldPasswordModel.PASSWORD_LEN_MIN:
            self.viewModel.setErrorMessage(errors.passwordIsTooShort())

    def _eyeClickHandler(self):
        self._wasPasswordVisibilityChanged = True
        self._isPasswordVisible = not self._isPasswordVisible
        self.viewModel.setIsPasswordVisible(self._isPasswordVisible)
        self.onPasswordVisibilityChanged()


class CodePresenter(BaseFieldPresenter):
    __slots__ = ()

    def _validateChangedValue(self):
        self.viewModel.setErrorMessage('')

    def _validateValueWhenFocusChanged(self):
        pass
