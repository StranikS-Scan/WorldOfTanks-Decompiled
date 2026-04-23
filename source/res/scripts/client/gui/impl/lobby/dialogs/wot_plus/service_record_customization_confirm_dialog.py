# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/wot_plus/service_record_customization_confirm_dialog.py
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import MonoButtonTemplate
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_view_model import MonoDialogTemplateViewModel
from gui.impl.lobby.dialogs.wot_plus.base_dialog import BaseDialog
from gui.impl.pub.dialog_window import DialogButtons

class ServiceRecordCustomizationConfirmDialog(BaseDialog):

    def __init__(self, *args, **kwargs):
        super(ServiceRecordCustomizationConfirmDialog, self).__init__({}, self._buildResourcesParams(), *args, **kwargs)

    def _buildResourcesParams(self):
        return {'titleString': backport.text(R.strings.dialogs.wotPlusServiceRecordCustomizationDialog.title())}

    def _setButtons(self):
        with self.viewModel.transaction() as vm:
            buttonsArray = vm.getButtons()
            buttonsArray.clear()
            confirmButton = MonoButtonTemplate(MonoDialogTemplateViewModel.ACTION_CONFIRM, R.strings.dialogs.wotPlusServiceRecordCustomizationDialog.save(), 'Button', ButtonType.PRIMARY, False)
            cancelButton = MonoButtonTemplate(MonoDialogTemplateViewModel.ACTION_CANCEL, R.strings.dialogs.common.cancel(), 'Button', ButtonType.SECONDARY, False)
            self._addButton(confirmButton)
            self._addButton(cancelButton)

    def _onAction(self, event):
        act = event.get('action')
        if act == MonoDialogTemplateViewModel.ACTION_CANCEL:
            self._setResult(DialogButtons.CANCEL)
            return
        if act == MonoDialogTemplateViewModel.ACTION_CLOSE or act == MonoDialogTemplateViewModel.ACTION_ESCAPE:
            self._setResult('')
            return
        super(ServiceRecordCustomizationConfirmDialog, self)._onAction(event)
