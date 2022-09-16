# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/demo_confirm_credentials_overlay_view.py
import typing
import BigWorld
from gui.impl.backport import text as loc
from gui.impl.gen import R
from gui.impl.lobby.account_completion.common import errors
from gui.impl.lobby.account_completion.common.base_confirm_credentials_overlay_view import BaseConfirmCredentialsOverlayView
from gui.impl.lobby.account_completion.utils.common import DISABLE_BUTTON_TIME, AccountCompletionType
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showDemoAddCredentialsOverlay, showDemoCompleteOverlay, showContactSupportOverlay, showDemoWaitingForTokenOverlayViewOverlay
from helpers import dependency
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController
if typing.TYPE_CHECKING:
    from wg_async import _Future
    from gui.platform.wgnp.demo_account.request import ConfirmCredentialsParams
res = R.strings.dialogs.accountCompletion

class DemoConfirmCredentialsOverlayView(BaseConfirmCredentialsOverlayView):
    __slots__ = ()
    _IS_CLOSE_BUTTON_VISIBLE = False
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)

    def activate(self, *args, **kwargs):
        super(DemoConfirmCredentialsOverlayView, self).activate(*args, **kwargs)
        self._wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)

    def deactivate(self):
        self._wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)
        super(DemoConfirmCredentialsOverlayView, self).deactivate()

    def _getEmailAddedTime(self):
        return self._wgnpDemoAccCtrl.credentialsAddedTime

    def _doRequest(self):
        return self._wgnpDemoAccCtrl.confirmCredentials(self._code.value)

    def _handleSuccess(self, *_):
        self._handleTokenWaiting()

    def _handleTokenWaiting(self):
        status = self._wgnpDemoAccCtrl.getCurrentStatus()
        if status == StatusTypes.CONFIRMED:
            showDemoCompleteOverlay(completionType=AccountCompletionType.DOI)
        else:
            showDemoWaitingForTokenOverlayViewOverlay(completionType=AccountCompletionType.DOI)

    def _handleError(self, response):
        if response.isConfirmationCodeExpired:
            self._updateErrorModel(errorMessage=res.activate.keyDied(), isButtonVisible=False, buttonTimer=0)
        elif response.isConfirmationCodeIncorrect:
            self._updateErrorModel(errorMessage=errors.keyErrorResID(), isButtonEnabled=False, buttonTimer=DISABLE_BUTTON_TIME)
        elif response.isConfirmationCodeDeactivated:
            self._updateErrorModel(errorMessage=errors.tooManyIncorrectTriesResID(), isButtonVisible=False, buttonTimer=0, resendButtonLabelResID=res.activate.enterCredentialsAgain())
        elif response.isInvalidChoice:
            message = loc(res.error.somethingWentWrong(), nickname=BigWorld.player().name)
            showContactSupportOverlay(message=message, isCloseVisible=False)
        elif response.isLoginAlreadyTaken:
            self._updateErrorModel(errorMessage=res.loginAlreadyTaken(), isButtonVisible=False, buttonTimer=0)
        elif response.isAccountAlreadyHasLogin:
            self._handleTokenWaiting()
        elif response.isSpaWeakPassword:
            showDemoAddCredentialsOverlay(initialEmail=self._email, emailError=errors.spaPasswordIsWeak())
        else:
            self._setWarning(loc(res.warningServerUnavailable()))

    def _onResend(self):
        showDemoAddCredentialsOverlay(initialEmail=self._email)

    def __confirmedHandler(self, *_):
        self._setWaiting(False)
        showDemoCompleteOverlay(completionType=AccountCompletionType.DOI)
