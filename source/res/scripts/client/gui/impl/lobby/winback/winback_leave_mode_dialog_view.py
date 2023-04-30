# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_leave_mode_dialog_view.py
from functools import partial
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.winback_leave_mode_dialog_view_model import WinbackLeaveModeDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons

class WinbackLeaveModeDialogView(FullScreenDialogBaseView):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.winback.WinbackLeaveModeDialogView())
        settings.flags = ViewFlags.VIEW
        settings.model = WinbackLeaveModeDialogViewModel()
        super(WinbackLeaveModeDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackLeaveModeDialogView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onLeaveMode, partial(self._setResult, DialogButtons.SUBMIT)), (self.viewModel.onClose, partial(self._setResult, DialogButtons.CANCEL)))
