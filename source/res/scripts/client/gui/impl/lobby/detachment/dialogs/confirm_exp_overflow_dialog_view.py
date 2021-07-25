# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/confirm_exp_overflow_dialog_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.confirm_exp_overflow_dialog_view_model import ConfirmExpOverflowDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView

class ConfirmExpOverflowDialogView(FullScreenDialogView):

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ConfirmExpOverflowView(), model=ConfirmExpOverflowDialogViewModel())
        super(ConfirmExpOverflowDialogView, self).__init__(settings)
        self.__experienceOverflow = ctx.get('xpOverflow')

    @property
    def viewModel(self):
        return super(ConfirmExpOverflowDialogView, self).getViewModel()

    def _setBaseParams(self, model):
        with model.transaction() as viewModel:
            viewModel.setAmount(self.__experienceOverflow)
            viewModel.setTitleBody(R.strings.dialogs.detachment.confirmExpOverflow.title())
            viewModel.setAcceptButtonText(R.strings.detachment.common.submit())
            viewModel.setCancelButtonText(R.strings.detachment.common.cancel())
            super(ConfirmExpOverflowDialogView, self)._setBaseParams(model)
