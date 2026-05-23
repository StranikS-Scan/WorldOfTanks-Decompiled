# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_close_confirmation_dialog.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.customization.customization_close_confirmation_dialog_model import CustomizationCloseConfirmationDialogModel
from gui.impl.pub import ViewImpl

class CustomizationCloseConfirmationDialog(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CustomizationCloseConfirmationDialogModel()
        super(CustomizationCloseConfirmationDialog, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CustomizationCloseConfirmationDialog, self).getViewModel()
