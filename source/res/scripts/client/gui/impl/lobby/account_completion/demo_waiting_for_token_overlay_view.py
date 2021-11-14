# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/demo_waiting_for_token_overlay_view.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_overlay_view_model import BaseOverlayViewModel
from gui.impl.lobby.account_completion.common.base_overlay_view import BaseOverlayView
from gui.impl.lobby.account_completion.utils.common import AccountCompletionType
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showDemoCompleteOverlay
from helpers import dependency
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController

class DemoWaitingForTokenOverlayView(BaseOverlayView):
    __slots__ = ('_completionType',)
    _IS_CLOSE_BUTTON_VISIBLE = False
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.account_completion.EmptyView
    _VIEW_MODEL_CLASS = BaseOverlayViewModel

    def __init__(self):
        super(DemoWaitingForTokenOverlayView, self).__init__()
        self._completionType = AccountCompletionType.UNDEFINED

    def activate(self, completionType=AccountCompletionType.UNDEFINED, *args, **kwargs):
        super(DemoWaitingForTokenOverlayView, self).activate(*args, **kwargs)
        self._completionType = completionType
        self._wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)

    def deactivate(self):
        self._wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__confirmedHandler)
        super(DemoWaitingForTokenOverlayView, self).deactivate()

    def _onLoading(self, *args, **kwargs):
        super(DemoWaitingForTokenOverlayView, self)._onLoading(*args, **kwargs)
        self._setWaiting(True, R.strings.dialogs.accountCompletion.waiting.confirmation())

    def __confirmedHandler(self, *_):
        showDemoCompleteOverlay(completionType=self._completionType)
