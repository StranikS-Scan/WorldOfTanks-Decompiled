# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/demo_renaming_overlay_view.py
import typing
import BigWorld
from wg_async import wg_await, wg_async, AsyncReturn
from gui.impl.backport import text as loc
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.renaming_model import RenamingModel
from gui.impl.lobby.account_completion.common import errors
from gui.impl.lobby.account_completion.common.base_wgnp_overlay_view import BaseWGNPOverlayView
from gui.impl.lobby.account_completion.common.name_presenter import NamePresenter
from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
from gui.impl.lobby.account_completion.utils.common import DISABLE_BUTTON_TIME
from gui.impl.pub.dialog_window import DialogButtons
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.wgnp.demo_account.controller import NICKNAME_CONTEXT
from gui.shared.event_dispatcher import showDemoAccRenamingCompleteOverlay, showContactSupportOverlay, showDemoRenamingUnavailableOverlay
from helpers import dependency
from skeletons.gui.game_control import IDemoAccCompletionController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController
if typing.TYPE_CHECKING:
    from wg_async import _Future
    from gui.platform.wgnp.demo_account.request import ChangeNicknameParams
_res = R.strings.dialogs.accountCompletion.renamingOverlay

class DemoRenamingOverlayView(BaseWGNPOverlayView):
    __slots__ = ('_name', '_requestedName')
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.account_completion.RenamingView
    _VIEW_MODEL_CLASS = RenamingModel
    _TITLE = _res.title()
    _SUBTITLE = _res.subTitle()
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _demoAccController = dependency.descriptor(IDemoAccCompletionController)
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    _bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(DemoRenamingOverlayView, self).__init__()
        self._name = NamePresenter(self.viewModel.name)
        self._requestedName = ''

    @property
    def viewModel(self):
        return super(DemoRenamingOverlayView, self).getViewModel()

    def activate(self, *args, **kwargs):
        super(DemoRenamingOverlayView, self).activate(*args, **kwargs)
        self._wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.UNDEFINED, self._onRenamingDisabled, context=NICKNAME_CONTEXT)
        self._name.onChanged += self._updateConfirmButtonAvailability
        self._updateConfirmButtonAvailability()

    def deactivate(self):
        self._wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.UNDEFINED, self._onRenamingDisabled, context=NICKNAME_CONTEXT)
        self._name.onChanged -= self._updateConfirmButtonAvailability
        self._name.clear()
        super(DemoRenamingOverlayView, self).deactivate()

    @wg_async
    def _closeClickedHandler(self):
        CurtainWindow.getInstance().hide()
        if self._bootcampCtrl.isInBootcamp():
            builder = ResDialogBuilder()
            builder.setMessagesAndButtons(R.strings.dialogs.accountCompletion.renaming.skip)
            result = yield wg_await(dialogs.show(builder.build()))
            if result.result != DialogButtons.SUBMIT:
                CurtainWindow.getInstance().reveal()
                return
        super(DemoRenamingOverlayView, self)._closeClickedHandler()

    def _onRenamingDisabled(self, status):
        showDemoRenamingUnavailableOverlay(self._onClose)

    def _updateConfirmButtonAvailability(self):
        haveTimedWarning = self.viewModel.getWarningCountdown() and self.viewModel.getWarningText()
        self.viewModel.setIsConfirmEnabled(self._name.isValid and bool(self._name.value) and not haveTimedWarning)

    def _finalize(self):
        self._name.dispose()
        super(DemoRenamingOverlayView, self)._finalize()

    def _validateInput(self):
        self._name.validate()
        return self._name.isValid

    @wg_async
    def _confirmClickedHandler(self):
        if not self._name.isAlreadyRemotelyValidated:
            yield self._name.remotelyValidate()
        if self._name.isValid:
            super(DemoRenamingOverlayView, self)._confirmClickedHandler()

    def _doRequest(self):
        return self._request()

    @wg_async
    def _request(self):
        self._requestedName = self._name.value
        self._name.cancelRemoteValidation()
        status = yield wg_await(self._wgnpDemoAccCtrl.getNicknameStatus())
        response = yield wg_await(self._wgnpDemoAccCtrl.changeNickname(self._requestedName, status.cost))
        raise AsyncReturn(response)

    def _handleSuccess(self, *_):
        showDemoAccRenamingCompleteOverlay(self._requestedName, self._onClose)

    def _handleError(self, response):
        if response.isNameEmpty or response.isNameMinLength:
            self.viewModel.name.setErrorMessage(errors.nameIsTooShort())
        elif response.isNameInvalid:
            self.viewModel.name.setErrorMessage(errors.nameInvalid())
        elif response.isNameMaxLength:
            self.viewModel.name.setErrorMessage(errors.nameIsTooLong())
        elif response.isNameForbidden:
            self.viewModel.name.setErrorMessage(loc(_res.nameForbidden()))
        elif response.isNameExists:
            self.viewModel.name.setErrorMessage(loc(_res.nameTaken()))
        elif response.isTimeout or response.isAuthTokenExpired:
            message = loc(R.strings.dialogs.accountCompletion.warningServerUnavailableTimed())
            self._setWarning(message, DISABLE_BUTTON_TIME)
            self._name.lock()
        else:
            if response.isNeedNicknameStatusCheck:
                status = self._wgnpDemoAccCtrl.getCurrentStatus(context=NICKNAME_CONTEXT)
                if status in (StatusTypes.PROCESSING, StatusTypes.ADDED):
                    super(DemoRenamingOverlayView, self)._closeClickedHandler()
                    return
            message = loc(R.strings.dialogs.accountCompletion.error.renamingMalfunction(), nickname=BigWorld.player().name)
            showContactSupportOverlay(message=message, onClose=self._onClose)

    def _warningTimerHandler(self):
        self._name.unlock()
        super(DemoRenamingOverlayView, self)._warningTimerHandler()
