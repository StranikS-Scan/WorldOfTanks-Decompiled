# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/steam_add_email_overlay_view.py
import typing
from gui.impl.backport import text as loc
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.tooltips.tooltip_constants import TooltipConstants
from gui.impl.lobby.account_completion.common import errors
from gui.impl.lobby.account_completion.common.base_credentials_overlay_view import BaseCredentialsOverlayView
from gui.impl.lobby.account_completion.utils.common import showAccountAlreadyHasEmail, RESTRICTED_REQUEST_MIN_TIME
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.shared.event_dispatcher import showSteamConfirmEmailOverlay
from helpers import dependency
from helpers.time_utils import getTimeDeltaFromNow
from skeletons.gui.game_control import ISteamCompletionController
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
if typing.TYPE_CHECKING:
    from wg_async import _Future
    from gui.platform.wgnp.steam_account.request import AddEmailParams as WGNPSAAddEmailParams
    from gui.impl.gen.view_models.views.lobby.account_completion.add_credentials_model import AddCredentialsModel
rAccCompletion = R.strings.dialogs.accountCompletion

class SteamAddEmailOverlayView(BaseCredentialsOverlayView):
    __slots__ = ()
    _TITLE = rAccCompletion.email.title()
    _SUBTITLE = rAccCompletion.email.subTitle()
    _REWARDS_TITLE = rAccCompletion.rewardsTitle()
    __wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    __accountCompletionCtrl = dependency.descriptor(ISteamCompletionController)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SUBTITLE:
                return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=loc(R.strings.tooltips.accountCompletion.email.titleTooltip()))
            return super(SteamAddEmailOverlayView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(SteamAddEmailOverlayView, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsPasswordInputVisible(False)
        self.__accountCompletionCtrl.setAddEmailOverlayShown()

    def _validateInput(self):
        return self._email.validate()

    def _doRequest(self):
        return self.__wgnpSteamAccCtrl.addEmail(self._email.value)

    def _handleSuccess(self, *_):
        self.__accountCompletionCtrl.setConfirmEmailOverlayAllowed(isAllowed=True)
        showSteamConfirmEmailOverlay(email=self._email.value)

    def _handleError(self, response):
        if response.isRequestLimitExceeded:
            with self.viewModel.transaction() as model:
                message = loc(rAccCompletion.emailOverlay.error.codeAlreadySent())
                errorTime = max(RESTRICTED_REQUEST_MIN_TIME, getTimeDeltaFromNow(response.requestRestrictedUntilTime))
                model.email.setErrorMessage(message)
                model.email.setErrorTime(errorTime)
        elif response.isAccountAlreadyHasEmail:
            showAccountAlreadyHasEmail(self.viewModel)
        else:
            super(SteamAddEmailOverlayView, self)._handleError(response)

    def _getEmailErrorMessage(self, response):
        if response.isEmailRestrictedByCountry:
            message = errors.emailRestrictedByCountry()
        elif response.isEmailBannedInCountry:
            message = loc(rAccCompletion.emailProviderBanned())
        elif response.isEmailInvalid:
            message = errors.emailIsInvalid()
        elif response.isEmailForbidden:
            message = loc(rAccCompletion.emailForbidden())
        elif response.isEmailMinLength:
            message = errors.emailIsTooShort()
        elif response.isEmailMaxLength:
            message = errors.emailIsTooLong()
        elif response.isEmailAlreadyTaken:
            message = errors.emailAlreadyTaken()
        else:
            message = super(SteamAddEmailOverlayView, self)._getEmailErrorMessage(response)
        return message
