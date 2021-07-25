# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/close_intro_video_dialog_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView

class CloseIntroVideoDialogView(FullScreenDialogView):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ConfirmIntroVideoCloseDialogView())
        settings.model = FullScreenDialogWindowModel()
        super(CloseIntroVideoDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CloseIntroVideoDialogView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setAcceptButtonText(R.strings.detachment.introVideo.button.accept())
            model.setCancelButtonText(R.strings.detachment.introVideo.button.cancel())
            model.setTitleBody(R.strings.detachment.introVideo.title())
