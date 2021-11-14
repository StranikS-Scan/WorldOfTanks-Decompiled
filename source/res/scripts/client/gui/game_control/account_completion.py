# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/account_completion.py
import typing
import constants
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SHOW_DEMO_ACC_REGISTRATION
from async import async, await
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.impl.lobby.account_completion.common import errors
from gui.platform.base.settings import CONTENT_WAITING
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showSteamAddEmailOverlay, showSteamConfirmEmailOverlay, showDemoAddCredentialsOverlay, showDemoErrorOverlay, showDemoConfirmCredentialsOverlay, showDemoCompleteOverlay, showDemoWaitingForTokenOverlayViewOverlay
from helpers import dependency
from skeletons.gui.game_control import IOverlayController, IBootcampController, ISteamCompletionController, IDemoAccCompletionController
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController, IWGNPDemoAccRequestController
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.platform.wgnp.demo_account.statuses import DemoAccCredentialsStatus

class SteamCompletionController(ISteamCompletionController):
    _loginManager = dependency.descriptor(ILoginManager)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    _bootcampController = dependency.descriptor(IBootcampController)
    _overlayController = dependency.descriptor(IOverlayController)

    def __init__(self):
        super(SteamCompletionController, self).__init__()
        self._bootcampNotFinished = False
        self._bootcampExit = False
        self._overlayDestroyed = False

    def init(self):
        g_bootcampEvents.onBootcampFinished += self.__onExitBootcamp
        self._hangarSpace.onSpaceCreate += self.__onSpaceCreate

    def fini(self):
        g_bootcampEvents.onBootcampFinished -= self.__onExitBootcamp
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self._overlayDestroyed = True

    @property
    def isSteamAccount(self):
        return self._loginManager.isWgcSteam

    def __onExitBootcamp(self, *args, **kwargs):
        self._bootcampExit = True

    @async
    def __onSpaceCreate(self, *args, **kwargs):
        if not self._bootcampExit or self._bootcampController.isInBootcamp() or self._overlayController.isActive or not self.isSteamAccount:
            return
        self._bootcampExit = False
        status = yield await(self._wgnpSteamAccCtrl.getEmailStatus(waitingID=CONTENT_WAITING))
        if self._overlayDestroyed or status.isUndefined or not self._hangarSpace.spaceInited:
            return
        if status.typeIs(StatusTypes.ADD_NEEDED):
            showSteamAddEmailOverlay()
        elif status.typeIs(StatusTypes.ADDED):
            showSteamConfirmEmailOverlay(email=status.email)


class DemoAccCompletionController(IDemoAccCompletionController):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _bootcampCtrl = dependency.descriptor(IBootcampController)
    _overlayController = dependency.descriptor(IOverlayController)
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)

    def __init__(self):
        super(DemoAccCompletionController, self).__init__()
        self._isDemoAccount = False
        self._controllerDestroyed = False

    def init(self):
        g_playerEvents.onClientUpdated += self._onClientUpdate
        self._hangarSpace.onSpaceCreate += self._onSpaceCreated

    def fini(self):
        g_playerEvents.onClientUpdated -= self._onClientUpdate
        self._hangarSpace.onSpaceCreate -= self._onSpaceCreated
        self._controllerDestroyed = True

    @property
    def isDemoAccount(self):
        return self._isDemoAccount

    @property
    def isInDemoAccRegistration(self):
        needShow = AccountSettings.getSettings(SHOW_DEMO_ACC_REGISTRATION)
        return self.isDemoAccount and needShow

    @isInDemoAccRegistration.setter
    def isInDemoAccRegistration(self, value):
        AccountSettings.setSettings(SHOW_DEMO_ACC_REGISTRATION, value)

    def runDemoAccRegistration(self):
        self.isInDemoAccRegistration = True
        if self._hangarSpace.spaceInited:
            self._showDemoAccOverlay()

    @async
    def updateOverlayState(self, waitingID=None, onComplete=None):
        status = yield await(self._wgnpDemoAccCtrl.getCredentialsStatus(waitingID))
        if self._controllerDestroyed or not self._hangarSpace.spaceInited:
            return
        else:
            if status.typeIs(StatusTypes.ADD_NEEDED):
                if status.isSpaWeakPassword:
                    showDemoAddCredentialsOverlay(initialEmail=status.login, emailError=errors.spaPasswordIsWeak())
                else:
                    showDemoAddCredentialsOverlay()
            elif status.typeIs(StatusTypes.ADDED):
                showDemoConfirmCredentialsOverlay(email=status.login)
            elif status.typeIs(StatusTypes.CONFIRMATION_SENT):
                showDemoWaitingForTokenOverlayViewOverlay()
            elif status.typeIs(StatusTypes.CONFIRMED):
                showDemoCompleteOverlay()
            elif status.isUndefined:
                showDemoErrorOverlay()
            if onComplete is not None:
                onComplete()
            return

    def _onSpaceCreated(self):
        if self._bootcampCtrl.isInBootcamp() and self.isInDemoAccRegistration:
            self._showDemoAccOverlay()

    @async
    def _showDemoAccOverlay(self):
        if self._overlayController.isActive:
            return
        yield await(self.updateOverlayState(waitingID=CONTENT_WAITING))

    def _onClientUpdate(self, diff, _):
        if constants.DEMO_ACCOUNT_ATTR in diff:
            self._isDemoAccount = bool(diff.get(constants.DEMO_ACCOUNT_ATTR))
