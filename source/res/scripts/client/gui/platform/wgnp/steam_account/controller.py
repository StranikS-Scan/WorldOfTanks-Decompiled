# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/steam_account/controller.py
import typing
import time
import wg_async
from BWUtil import AsyncReturn
from constants import EMAIL_CONFIRMATION_TOKEN_NAME
from gui.platform.base.statuses.controller_mixin import StatusesMixin
from gui.platform.base.statuses.constants import StatusTypes, DEFAULT_CONTEXT
from gui.platform.wgnp.base.controller import WGNPRequestController
from gui.platform.wgnp.steam_account.request import EmailStatusParams, AddEmailParams, ConfirmEmailParams
from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus, createEmailStatusFromResponse
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController

class WGNPSteamAccRequestController(StatusesMixin, WGNPRequestController, IWGNPSteamAccRequestController):

    def __init__(self):
        super(WGNPSteamAccRequestController, self).__init__()
        self._emailAddedTime = 0

    @property
    def emailAddedTime(self):
        return self._emailAddedTime

    @wg_async.wg_async
    def getEmailStatus(self, waitingID=None):
        status = self._getStatus()
        self._logger.debug('Getting email status from cache=%s, waitingID=%s.', status, waitingID)
        if status.isUndefined:
            response = yield self._request(EmailStatusParams(self.settings.getUrl()), waitingID=waitingID)
            status = createEmailStatusFromResponse(response)
            self._updateStatus(status)
        raise AsyncReturn(status)

    @wg_async.wg_async
    def addEmail(self, email, waitingID=None):
        self._logger.debug('Adding waitingID=%s.', waitingID)
        response = yield self._request(AddEmailParams(self.settings.getUrl(), email), waitingID=waitingID)
        if response.isSuccess():
            self._emailAddedTime = int(time.time())
            self._updateStatus(SteamAccEmailStatus(StatusTypes.ADDED, data={'email': email}))
        elif response.isAccountAlreadyHasEmail:
            self._updateStatus(SteamAccEmailStatus(StatusTypes.CONFIRMED))
        raise AsyncReturn(response)

    @wg_async.wg_async
    def confirmEmail(self, code, waitingID=None):
        self._logger.debug('Confirm email with waitingID=%s.', waitingID)
        response = yield self._request(ConfirmEmailParams(self.settings.getUrl(), code), waitingID=waitingID)
        if response.isSuccess() or response.isAccountAlreadyHasEmail:
            self._updateStatus(SteamAccEmailStatus(StatusTypes.CONFIRMED))
        elif response.isConfirmationCodeDeactivated or response.isConfirmationCodeExpired or response.isEmailAlreadyTaken:
            self._updateStatus(SteamAccEmailStatus(StatusTypes.ADD_NEEDED))
        raise AsyncReturn(response)

    def _getStatusTokensSettings(self):
        return [(EMAIL_CONFIRMATION_TOKEN_NAME, DEFAULT_CONTEXT, SteamAccEmailStatus(StatusTypes.CONFIRMED))]
