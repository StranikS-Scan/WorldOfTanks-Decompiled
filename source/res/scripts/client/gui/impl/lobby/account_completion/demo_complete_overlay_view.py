# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/demo_complete_overlay_view.py
import BigWorld
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.complete_model import CompleteModel
from gui.impl.lobby.account_completion.common.base_overlay_view import BaseOverlayView
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class DemoCompleteOverlayView(BaseOverlayView):
    __slots__ = ()
    _IS_CLOSE_BUTTON_VISIBLE = False
    _bootcampController = dependency.descriptor(IBootcampController)
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.account_completion.CompleteView
    _VIEW_MODEL_CLASS = CompleteModel

    @property
    def viewModel(self):
        return super(DemoCompleteOverlayView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DemoCompleteOverlayView, self)._onLoading(*args, **kwargs)
        self.viewModel.setTitle(R.strings.dialogs.accountCompletion.demoComplete.title())
        self.viewModel.setSubTitle(R.strings.dialogs.accountCompletion.demoComplete.description())

    def _finalize(self):
        if self._bootcampController.isInBootcamp():
            BigWorld.callback(0, self._bootcampController.finishBootcamp)
        super(DemoCompleteOverlayView, self)._finalize()
