# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/demo_account/controller.py
import typing
import time
import wg_async
from BWUtil import AsyncReturn
from constants import EMAIL_CONFIRMATION_TOKEN_NAME
from gui.platform.base.statuses.controller_mixin import StatusesMixin
from gui.platform.base.statuses.constants import DEFAULT_CONTEXT, StatusTypes
from gui.platform.wgnp.base.controller import WGNPRequestController
from gui.platform.wgnp.demo_account.request import CredentialsStatusParams, AddCredentialsParams, ConfirmCredentialsParams, NicknameStatusParams, ChangeNicknameParams, ValidateNicknameParams
from gui.platform.wgnp.demo_account.statuses import DemoAccCredentialsStatus, createCredentialsConfirmationStatus, createCredentialStatusFromResponse, DemoAccNicknameStatus, createNicknameStatusFromResponse
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController
NICKNAME_CONTEXT = '<nickname>'

class WGNPDemoAccRequestController(StatusesMixin, WGNPRequestController, IWGNPDemoAccRequestController):

    def __init__(self):
        super(WGNPDemoAccRequestController, self).__init__()
        self._credentialsAddedTime = 0

    @property
    def credentialsAddedTime(self):
        return self._credentialsAddedTime

    @wg_async.wg_async
    def getCredentialsStatus(self, waitingID=None):
        status = self._getStatus()
        self._logger.debug('Getting credential status from cache=%s, waitingID=%s.', status, waitingID)
        if status.isUndefined:
            response = yield self._request(CredentialsStatusParams(self.settings.getUrl()), waitingID=waitingID)
            status = createCredentialStatusFromResponse(response)
            self._updateStatus(status)
        raise AsyncReturn(status)

    @wg_async.wg_async
    def addCredentials(self, login, password, waitingID=None):
        self._logger.debug('Adding credentials waitingID=%s.', waitingID)
        response = yield self._request(AddCredentialsParams(self.settings.getUrl(), login, password), waitingID=waitingID)
        if response.isSuccess():
            if response.isCreated:
                self._updateStatus(createCredentialsConfirmationStatus())
            else:
                self._credentialsAddedTime = int(time.time())
                self._updateStatus(DemoAccCredentialsStatus(StatusTypes.ADDED, {'login': login}))
        elif response.isAccountAlreadyHasLogin:
            self._updateStatus(createCredentialsConfirmationStatus())
        raise AsyncReturn(response)

    @wg_async.wg_async
    def confirmCredentials(self, code, waitingID=None):
        self._logger.debug('Confirm credentials with waitingID=%s.', waitingID)
        response = yield self._request(ConfirmCredentialsParams(self.settings.getUrl(), code), waitingID=waitingID)
        if response.isSuccess() or response.isAccountAlreadyHasLogin:
            self._updateStatus(createCredentialsConfirmationStatus())
        elif response.isConfirmationCodeDeactivated or response.isConfirmationCodeExpired or response.isLoginAlreadyTaken or response.isSpaWeakPassword:
            self._updateStatus(DemoAccCredentialsStatus(StatusTypes.ADD_NEEDED))
        raise AsyncReturn(response)

    @wg_async.wg_async
    def getNicknameStatus(self, waitingID=None, force=False):
        status = self._getStatus(context=NICKNAME_CONTEXT)
        self._logger.debug('Getting nickname status from cache=%s, waitingID=%s.', status, waitingID)
        if status.isUndefined or force:
            response = yield self._renameRequest(NicknameStatusParams(self.settings.getUrl()), waitingID=waitingID)
            status = createNicknameStatusFromResponse(response)
            self._updateStatus(status, context=NICKNAME_CONTEXT)
        raise AsyncReturn(status)

    @wg_async.wg_async
    def validateNickname(self, nickname, waitingID=None):
        self._logger.debug('Validate nickname to %s, waitingID=%s.', nickname, waitingID)
        response = yield self._renameRequest(ValidateNicknameParams(self.settings.getUrl(), nickname), waitingID=waitingID)
        raise AsyncReturn(response)

    @wg_async.wg_async
    def changeNickname(self, nickname, cost, waitingID=None):
        self._logger.debug('Change nickname to %s for %s, waitingID=%s.', nickname, cost, waitingID)
        response = yield self._renameRequest(ChangeNicknameParams(self.settings.getUrl(), nickname, cost), waitingID=waitingID)
        if response.isSuccess():
            self._updateStatus(DemoAccNicknameStatus(StatusTypes.PROCESSING), context=NICKNAME_CONTEXT)
        elif response.isNeedNicknameStatusCheck:
            yield self.getNicknameStatus(force=True)
        raise AsyncReturn(response)

    @wg_async.wg_async
    def _renameRequest(self, params, waitingID=None):
        if not self.settings.isRenameApiEnabled():
            response = params.response.createServiceDisabled()
            self._logger.debug('Rename api disabled.')
        else:
            response = yield self._request(params, waitingID=waitingID)
        raise AsyncReturn(response)

    def _checkIsEnabled(self, diff):
        super(WGNPDemoAccRequestController, self)._checkIsEnabled(diff)
        if not self.settings.isRenameApiEnabled():
            self._updateStatus(DemoAccNicknameStatus(StatusTypes.UNDEFINED), context=NICKNAME_CONTEXT)

    def _getStatusTokensSettings(self):
        return [(EMAIL_CONFIRMATION_TOKEN_NAME, DEFAULT_CONTEXT, DemoAccCredentialsStatus(StatusTypes.CONFIRMED))]
