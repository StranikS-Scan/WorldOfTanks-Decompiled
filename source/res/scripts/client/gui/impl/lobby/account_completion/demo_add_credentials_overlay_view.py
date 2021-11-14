# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/demo_add_credentials_overlay_view.py
import typing
from helpers.time_utils import getTimeDeltaFromNow
import BigWorld
from gui.impl.backport import text as loc
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.tooltips.tooltip_constants import TooltipConstants
from gui.impl.lobby.account_completion.common import errors
from gui.impl.lobby.account_completion.common.base_credentials_overlay_view import BaseCredentialsOverlayView
from gui.impl.lobby.account_completion.utils.common import RESTRICTED_REQUEST_MIN_TIME, AccountCompletionType
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showDemoConfirmCredentialsOverlay, showDemoCompleteOverlay, showContactSupportOverlay, showDemoWaitingForTokenOverlayViewOverlay
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController
from uilogging.account_completion.constants import LogGroup, ViewClosingResult
from uilogging.account_completion.loggers import AccountCompletionViewLogger
rAccCompletion = R.strings.dialogs.accountCompletion
if typing.TYPE_CHECKING:
    from async import _Future
    from gui.platform.wgnp.demo_account.request import AddCredentialsParams

class DemoAddCredentialsOverlayView(BaseCredentialsOverlayView):
    _TITLE = rAccCompletion.credentials.title()
    _SUBTITLE = rAccCompletion.credentials.subTitle()
    _REWARDS_TITLE = rAccCompletion.registrationRewardsTitle()
    _IS_CLOSE_BUTTON_VISIBLE = False
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    _bootcampController = dependency.descriptor(IBootcampController)
    _uiLogger = AccountCompletionViewLogger(LogGroup.CREDENTIALS)

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SUBTITLE:
                return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), header=loc(R.strings.tooltips.accountCompletion.credentials.subtitle.header()), body=loc(R.strings.tooltips.accountCompletion.credentials.subtitle.body()))
        return super(DemoAddCredentialsOverlayView, self).createToolTipContent(event, contentID)

    def activate(self, *args, **kwargs):
        super(DemoAddCredentialsOverlayView, self).activate(*args, **kwargs)
        self._wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)
        self._uiLogger.viewOpened(self.getParentWindow(), type=AccountCompletionType.UNDEFINED)

    def deactivate(self):
        self._wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)
        pwd = self._password
        self._uiLogger.viewClosed(was_eye_clicked=pwd.wasPasswordVisibilityChanged, is_eye_on=pwd.isPasswordVisible)
        super(DemoAddCredentialsOverlayView, self).deactivate()

    def _validateInput(self):
        self._email.validate()
        self._password.validate()
        return self._email.isValid and self._password.isValid

    def _doRequest(self):
        email = self._email.value
        password = self._password.value
        return self._wgnpDemoAccCtrl.addCredentials(email, password)

    def _handleSuccess(self, response):
        self._uiLogger.setParams(result=ViewClosingResult.SUCCESS)
        self._handleTokenWaiting(response)

    def _handleTokenWaiting(self, response):
        completionType = AccountCompletionType.SOI if response.isCreated else AccountCompletionType.DOI
        self._uiLogger.setParams(type=completionType)
        status = self._wgnpDemoAccCtrl.getCurrentStatus()
        if status == StatusTypes.CONFIRMATION_SENT:
            showDemoWaitingForTokenOverlayViewOverlay(completionType=completionType)
        elif status == StatusTypes.CONFIRMED:
            showDemoCompleteOverlay(completionType=completionType)
        else:
            showDemoConfirmCredentialsOverlay(email=self._email.value)

    def _handleError(self, response):
        if response.isCredentialsNotFound:
            message = loc(rAccCompletion.error.somethingWentWrong(), nickname=BigWorld.player().name)
            showContactSupportOverlay(message=message, isCloseVisible=False)
        elif response.isRequestLimitExceeded:
            message = loc(rAccCompletion.tooManyRequests())
            errorTime = max(RESTRICTED_REQUEST_MIN_TIME, getTimeDeltaFromNow(response.requestRestrictedUntilTime))
            self._setWarning(message, errorTime)
        elif response.isAccountAlreadyHasLogin:
            self._handleTokenWaiting(response)
        else:
            super(DemoAddCredentialsOverlayView, self)._handleError(response)
            self._updateConfirmButtonAvailability()

    def _getEmailErrorMessage(self, response):
        if response.isRestrictedByCountryPolicy:
            message = errors.emailRestrictedByCountry()
        elif response.isLoginInvalid:
            message = errors.emailIsInvalid()
        elif response.isLoginMinLength or response.isLoginEmpty:
            message = errors.emailIsTooShort()
        elif response.isLoginMaxLength:
            message = errors.emailIsTooLong()
        elif response.isLoginAlreadyTaken:
            message = errors.emailAlreadyTaken()
        else:
            message = super(DemoAddCredentialsOverlayView, self)._getEmailErrorMessage(response)
        return message

    def _getPasswordErrorMessage(self, response):
        if response.isPasswordMinLength or response.isPasswordEmpty:
            message = errors.passwordIsTooShort()
        elif response.isPasswordMaxLength:
            message = errors.passwordIsTooLong()
        elif response.isPasswordWeak:
            message = loc(rAccCompletion.passwordIsWeak())
        elif response.isPasswordInvalid:
            message = errors.passwordIsInvalid()
        else:
            message = super(DemoAddCredentialsOverlayView, self)._getEmailErrorMessage(response)
        return message

    def __confirmedHandler(self, *_):
        showDemoCompleteOverlay(completionType=AccountCompletionType.SOI)
