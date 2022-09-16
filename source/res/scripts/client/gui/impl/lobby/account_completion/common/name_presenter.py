# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/common/name_presenter.py
import logging
import re
import typing
import BigWorld
from Event import Event
from wg_async import wg_async, wg_await, AsyncScope, AsyncEvent, BrokenPromiseError
from gui.impl.backport import text as loc
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_name_model import FieldNameModel, NameStateEnum
from gui.impl.lobby.account_completion.common import errors
from gui.impl.lobby.account_completion.common.field_presenters import BaseFieldPresenter
from helpers import dependency
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController
if typing.TYPE_CHECKING:
    from typing import Callable, List
    from gui.platform.wgnp.demo_account.request import ValidateNicknameParams
_NAME_PATTERN = re.compile('^[a-z0-9_]+$', re.I)
_VALIDATION_DELAY = 3.0
_VALIDATE_NOW_DELAY = 0.1
_res = R.strings.dialogs.accountCompletion.renamingOverlay
_logger = logging.getLogger(__name__)

class ValidationRequestWrapper(object):
    __slots__ = ('_isDisposed',)
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    _instances = list()

    def __init__(self):
        super(ValidationRequestWrapper, self).__init__()
        self._isDisposed = False

    @wg_async
    def process(self, name, callback):
        self._isDisposed = False
        response = yield wg_await(self._wgnpDemoAccCtrl.validateNickname(name))
        if not self._isDisposed:
            callback(response)
        ValidationRequestWrapper.utilize(self)

    def dispose(self):
        self._isDisposed = True

    @staticmethod
    def create():
        return ValidationRequestWrapper._instances.pop() if ValidationRequestWrapper._instances else ValidationRequestWrapper()

    @staticmethod
    def utilize(wrapper):
        if wrapper not in ValidationRequestWrapper._instances:
            ValidationRequestWrapper._instances.append(wrapper)


class RemoteNameValidator(object):
    __slots__ = ('onStatusChanged', '_localValidator', '_remoteValidationCB', '_status', '_name', '_currentFuture', '_error', '_suggestions', '_requestWrapper')
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)

    def __init__(self, localValidator):
        super(RemoteNameValidator, self).__init__()
        self.onStatusChanged = Event()
        self._localValidator = localValidator
        self._remoteValidationCB = None
        self._status = NameStateEnum.UNDEFINED
        self._name = ''
        self._error = ''
        self._suggestions = []
        self._requestWrapper = None
        return

    @property
    def status(self):
        return self._status

    @property
    def isChecking(self):
        return self._status == NameStateEnum.CHECKING

    @property
    def error(self):
        return self._error

    @property
    def suggestions(self):
        return self._suggestions

    def dispose(self):
        self._status = NameStateEnum.UNDEFINED
        self._clearTimer()
        self._localValidator = None
        if self._requestWrapper is not None:
            self._requestWrapper.dispose()
            self._requestWrapper = None
        return

    def clear(self):
        self._status = NameStateEnum.UNDEFINED
        self._clearTimer()
        self._clearCurrentRequest()
        self._suggestions = []
        self._error = ''
        self.onStatusChanged()

    def invalidate(self, name):
        self._name = name
        self._startTimer()

    def validateNow(self, name):
        self._name = name
        self._clearTimer()
        self._remoteValidationCB = BigWorld.callback(_VALIDATE_NOW_DELAY, self._doValidate)

    def _startTimer(self):
        self._clearTimer()
        self._remoteValidationCB = BigWorld.callback(_VALIDATION_DELAY, self._doValidate)
        self._status = NameStateEnum.UNDEFINED
        self.onStatusChanged()

    def _clearTimer(self):
        if self._remoteValidationCB is not None:
            BigWorld.cancelCallback(self._remoteValidationCB)
            self._remoteValidationCB = None
        return

    def _doValidate(self):
        self._suggestions = []
        self._error = ''
        self._remoteValidationCB = None
        if not self._name or not self._localValidator():
            return
        else:
            self._status = NameStateEnum.CHECKING
            self.onStatusChanged()
            self._request()
            return

    @wg_async
    def _request(self):
        self._clearCurrentRequest()
        self._requestWrapper = ValidationRequestWrapper.create()
        yield wg_await(self._requestWrapper.process(self._name, self._requestCompleted))

    def _clearCurrentRequest(self):
        if self._requestWrapper is not None:
            self._requestWrapper.dispose()
            self._requestWrapper = None
        return

    def _requestCompleted(self, response):
        self._status = NameStateEnum.ERROR
        if response.isBanned:
            self._error = loc(_res.nameForbidden())
        elif response.isOccupied:
            if response.suggestions:
                self._suggestions = response.suggestions[:]
                self._error = loc(_res.nameTakenPickVariant())
            else:
                self._error = loc(_res.nameTaken())
        elif response.isInvalid:
            self._error = errors.nameInvalid()
        elif response.isMinLength:
            self._error = errors.nameIsTooShort()
        elif response.isMaxLength:
            self._error = errors.nameIsTooLong()
        else:
            self._error = ''
            self._status = NameStateEnum.OK
        self.onStatusChanged()


class NamePresenter(BaseFieldPresenter):
    __slots__ = ('onChanged', '_remoteValidator', '_isLocked', '_asyncScope')

    def __init__(self, viewModel):
        super(NamePresenter, self).__init__(viewModel)
        self.onChanged = Event()
        self._remoteValidator = RemoteNameValidator(self.validate)
        self._remoteValidator.onStatusChanged += self._statusChangeHandler
        self._isLocked = False
        self._asyncScope = AsyncScope()
        self.onValueChanged += self._valueChangeHandler
        self.onFocusLost += self._focusLostHandler
        with self.viewModel.transaction() as model:
            model.setName(R.strings.dialogs.accountCompletion.renamingOverlay.fieldName())
            model.setPlaceholder(BigWorld.player().name)
            model.setState(self._remoteValidator.status)
        viewModel.onSuggestionSelected += self._suggestionSelectHandler

    @property
    def viewModel(self):
        return self._viewModel

    @property
    def isValid(self):
        return super(NamePresenter, self).isValid and not self._remoteValidator.isChecking

    @property
    def isAlreadyRemotelyValidated(self):
        return self._remoteValidator.status in (NameStateEnum.OK, NameStateEnum.ERROR)

    def lock(self):
        if not self._isLocked:
            self._isLocked = True
            self._remoteValidator.clear()

    def unlock(self):
        if self._isLocked:
            self._isLocked = False
            self._remoteValidator.validateNow(self.value)

    def validate(self):
        isValid = super(NamePresenter, self).validate() and not self._remoteValidator.isChecking
        self.onChanged()
        return isValid

    @wg_async
    def remotelyValidate(self):
        event = AsyncEvent(scope=self._asyncScope)

        def statusChangeHandler():
            if self._remoteValidator.status in (NameStateEnum.OK, NameStateEnum.ERROR):
                event.set()

        self._remoteValidator.onStatusChanged += statusChangeHandler
        self._remoteValidator.validateNow(self.value)
        try:
            yield wg_await(event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed before got a response to remote nickname validation request', self)

        self._remoteValidator.onStatusChanged -= statusChangeHandler

    def clear(self):
        self._remoteValidator.clear()
        super(NamePresenter, self).clear()

    def cancelRemoteValidation(self):
        self._remoteValidator.clear()

    def dispose(self):
        self._remoteValidator.dispose()
        self._remoteValidator.onStatusChanged -= self._statusChangeHandler
        self.onValueChanged -= self._valueChangeHandler
        self.onFocusLost -= self._focusLostHandler
        self.viewModel.onSuggestionSelected -= self._suggestionSelectHandler
        self._asyncScope.destroy()
        super(NamePresenter, self).dispose()

    def _validateChangedValue(self):
        if self._isLocked:
            return
        self.viewModel.setErrorMessage('')
        self._remoteValidator.clear()

    def _validateValueWhenFocusChanged(self):
        if self._isLocked:
            return
        value = self._value
        if len(value) < FieldNameModel.NAME_LEN_MIN:
            self.viewModel.setErrorMessage(errors.nameIsTooShort())
        elif len(value) > FieldNameModel.NAME_LEN_MAX:
            self.viewModel.setErrorMessage(errors.nameIsTooLong())
        elif not _NAME_PATTERN.match(value):
            self.viewModel.setErrorMessage(errors.nameInvalid())

    def _statusChangeHandler(self):
        with self.viewModel.transaction() as model:
            status = self._remoteValidator.status
            model.setState(status)
            if status == NameStateEnum.ERROR:
                model.setErrorMessage(self._remoteValidator.error)
            suggestions = model.getSuggestions()
            suggestions.clear()
            for variant in self._remoteValidator.suggestions:
                suggestions.addString(variant)

            suggestions.invalidate()
        self.onChanged()

    def _focusLostHandler(self):
        if self._isLocked:
            return
        self._remoteValidator.validateNow(self.value)

    def _valueChangeHandler(self):
        if self._isLocked:
            return
        self._remoteValidator.invalidate(self.value)

    def _suggestionSelectHandler(self, args):
        suggestion = args.get('variant', '')
        self.setValue(suggestion)
        self.viewModel.setErrorMessage('')
        self._remoteValidator.clear()
        self._remoteValidator.invalidate(self.value)
