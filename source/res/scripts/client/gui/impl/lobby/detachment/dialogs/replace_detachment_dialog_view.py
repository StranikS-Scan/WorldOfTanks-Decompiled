# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/replace_detachment_dialog_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.replace_detachment_dialog_view_model import ReplaceDetachmentDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from crew2 import settings_globals
from uilogging.detachment.loggers import DetachmentLogger
from uilogging.detachment.constants import GROUP, ACTION

class ReplaceDetachmentDialogView(FullScreenDialogView):
    uiLogger = DetachmentLogger(GROUP.DELETE_DETACHMENT_DIALOG)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ReplaceDetachmentDialogView())
        settings.model = ReplaceDetachmentDialogViewModel()
        super(ReplaceDetachmentDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ReplaceDetachmentDialogView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setAcceptButtonText(R.strings.detachment.common.submit())
            vm.setCancelButtonText(R.strings.detachment.common.cancel())
            vm.setTitleBody(R.strings.detachment.profile.replaceDetachment.title())
            vm.setFullBufferAmount(settings_globals.g_detachmentSettings.recycleBinMaxSize)

    def _onAcceptClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CONFIRM)
        super(ReplaceDetachmentDialogView, self)._onAcceptClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(ReplaceDetachmentDialogView, self)._onCancelClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(ReplaceDetachmentDialogView, self)._onExitClicked()
