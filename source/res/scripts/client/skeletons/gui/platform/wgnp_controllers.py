# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/platform/wgnp_controllers.py
import typing
import async
from gui.platform.base.statuses.constants import DEFAULT_CONTEXT
from skeletons.gui.platform.controller import IPlatformRequestController
if typing.TYPE_CHECKING:
    from helpers.server_settings import _Wgnp
    from gui.platform.base.statuses.events_mgr import StatusEventsManager
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.platform.wgnp.steam_account.request import AddEmailParams, ConfirmEmailParams
    from gui.platform.wgnp.demo_account.statuses import DemoAccCredentialsStatus, DemoAccNicknameStatus
    from gui.platform.wgnp.demo_account.request import AddCredentialsParams, ConfirmCredentialsParams, ChangeNicknameParams, ValidateNicknameParams
    from gui.platform.base.statuses.constants import StatusTypes

class IWGNPRequestController(IPlatformRequestController):

    @property
    def settings(self):
        raise NotImplementedError


class IWGNPSteamAccRequestController(IWGNPRequestController):

    @async.async
    def addEmail(self, email, waitingID=None):
        raise NotImplementedError

    @async.async
    def getEmailStatus(self, waitingID=None):
        raise NotImplementedError

    @async.async
    def confirmEmail(self, code, waitingID=None):
        raise NotImplementedError

    @property
    def emailAddedTime(self):
        raise NotImplementedError

    @property
    def statusEvents(self):
        raise NotImplementedError


class IWGNPDemoAccRequestController(IWGNPRequestController):

    @async.async
    def getCredentialsStatus(self, waitingID=None):
        raise NotImplementedError

    @async.async
    def addCredentials(self, login, password, waitingID=None):
        raise NotImplementedError

    @async.async
    def confirmCredentials(self, code, waitingID=None):
        raise NotImplementedError

    @property
    def credentialsAddedTime(self):
        raise NotImplementedError

    @property
    def statusEvents(self):
        raise NotImplementedError

    def getCurrentStatus(self, context=DEFAULT_CONTEXT):
        raise NotImplementedError

    @async.async
    def getNicknameStatus(self, waitingID=None):
        raise NotImplementedError

    @async.async
    def validateNickname(self, nickname, waitingID=None):
        raise NotImplementedError

    @async.async
    def changeNickname(self, nickname, cost, waitingID=None):
        raise NotImplementedError
