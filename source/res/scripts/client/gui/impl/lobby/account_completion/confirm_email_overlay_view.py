# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/confirm_email_overlay_view.py
import time
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.email_activate_curtain_model import EmailActivateCurtainModel
from gui.impl.lobby.account_completion.email_overlay_view import EmailOverlayView
from gui.impl.pub.lobby_window import LobbyWindow
from gui.platform.wgnp.controller import isConfirmationCodeIncorrect, isConfirmationCodeDeactivated, isEmailAlreadyTaken, isConfirmationCodeExpired
from gui.shared.event_dispatcher import showAddEmailOverlay
_DISABLE_BUTTON_TIME = 90
_NUMBER_OF_SLOTS = 4

class ConfirmEmailOverlayView(EmailOverlayView):
    __slots__ = ('_email',)
    _TITLE = R.strings.dialogs.accountCompletion.activate.title()

    def __init__(self, settings, email='', fadeAnimation=False):
        super(ConfirmEmailOverlayView, self).__init__(settings, fadeAnimation)
        self._email = email

    @property
    def viewModel(self):
        return super(ConfirmEmailOverlayView, self).getViewModel()

    def _addListeners(self):
        super(ConfirmEmailOverlayView, self)._addListeners()
        self.viewModel.onResendClicked += self._onResend

    def _removeListeners(self):
        self.viewModel.onResendClicked -= self._onResend
        super(ConfirmEmailOverlayView, self)._removeListeners()

    def _fillModel(self, model):
        super(ConfirmEmailOverlayView, self)._fillModel(model)
        model.setIsShowAccept(True)
        model.setEmail(self._email)
        model.setTimer(max(0, _DISABLE_BUTTON_TIME - int(time.time()) + self._wgnpCtrl.emailAddedTime))
        model.field.setFieldNum(_NUMBER_OF_SLOTS)

    def _handleError(self, value, response):
        if isConfirmationCodeExpired(response) or isConfirmationCodeDeactivated(response) or isEmailAlreadyTaken(response):
            message = self._getErrorMessage(response)
            with self.viewModel.transaction() as model:
                self._updateModel(model, errorMessage=message, buttonTimer=0)
        else:
            super(ConfirmEmailOverlayView, self)._handleError(value, response)

    def _doRequest(self, value):
        return self._wgnpCtrl.confirmEmail(value)

    def _getErrorMessage(self, response):
        if isConfirmationCodeIncorrect(response):
            message = R.strings.dialogs.accountCompletion.activate.keyError()
        elif isConfirmationCodeExpired(response):
            message = R.strings.dialogs.accountCompletion.activate.keyDied()
        elif isConfirmationCodeDeactivated(response):
            message = R.strings.dialogs.accountCompletion.activate.tooManyIncorrectTries()
        elif isEmailAlreadyTaken(response):
            message = R.strings.dialogs.accountCompletion.emailAlreadyTaken()
        else:
            message = super(ConfirmEmailOverlayView, self)._getErrorMessage(response)
        return message

    def _updateModel(self, model, value=None, isUnavailable=False, errorMessage=None, buttonTimer=None):
        super(ConfirmEmailOverlayView, self)._updateModel(model, value, isUnavailable, errorMessage)
        if buttonTimer is not None:
            model.setTimer(buttonTimer)
        return

    def _onResend(self):
        self._setAnimation(isFade=True, isShow=False)
        showAddEmailOverlay(initialEmail=self._email, fadeAnimation=True)
        self.destroyWindow(offOverlay=False)


class ConfirmEmailOverlayWindow(LobbyWindow):

    def __init__(self, email='', fadeAnimation=False):
        settings = ViewSettings(R.views.lobby.account_completion.EmailActivateCurtainView())
        settings.model = EmailActivateCurtainModel()
        super(ConfirmEmailOverlayWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=ConfirmEmailOverlayView(settings, email, fadeAnimation), layer=WindowLayer.TOP_WINDOW)
