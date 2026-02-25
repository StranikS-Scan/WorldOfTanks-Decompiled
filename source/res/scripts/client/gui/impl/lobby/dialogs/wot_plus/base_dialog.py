# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/wot_plus/base_dialog.py
from typing import Dict
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialog_template_button import MonoButtonTemplate
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_view_model import MonoDialogTemplateViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
CLOSE_DIALOG_ACTIONS = (MonoDialogTemplateViewModel.ACTION_CLOSE, MonoDialogTemplateViewModel.ACTION_ESCAPE, MonoDialogTemplateViewModel.ACTION_CANCEL)

class BaseDialog(FullScreenDialogBaseView):
    LAYOUT_ID = R.views.mono.dialogs.default_dialog()
    VIEW_MODEL = MonoDialogTemplateViewModel
    DEFAULT_DIMMER_ALPHA = 0.6
    BACKGROUND_IMAGE = None

    def __init__(self, contentParams, resourcesParams, *args, **kwargs):
        customLayoutID = contentParams.pop('customLayoutID') if 'customLayoutID' in contentParams else None
        settings = ViewSettings(customLayoutID or self.LAYOUT_ID)
        model = settings.model = self.VIEW_MODEL()
        settings.args = args
        settings.kwargs = kwargs
        self._contentParams = contentParams
        self._resourcesParams = resourcesParams
        super(BaseDialog, self).__init__(settings, *args, **kwargs)
        model.setDimmerAlpha(self.DEFAULT_DIMMER_ALPHA)
        if self.BACKGROUND_IMAGE:
            model.setBackgroundImage(self.BACKGROUND_IMAGE)
        self._buttons = self.viewModel.getButtons()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onAction, self._onAction),)

    def _onLoading(self, *args, **kwargs):
        super(BaseDialog, self)._onLoading(*args, **kwargs)
        self._dumpContentParams()
        self._dumpResourcesParams()
        self._setButtons()

    def _addButton(self, monoButton):
        self._buttons.addViewModel(monoButton.viewModel)

    def _buildButton(self, action, label, buttonType, isDisabled=False):
        button = MonoButtonTemplate(action, label, 'Button', buttonType, isDisabled)
        return button

    def _dumpContentParams(self):
        with self.viewModel.transaction() as vm:
            content = vm.getContent()
            content.clear()
            for key, value in self._contentParams.iteritems():
                content.set(key, value)

    def _dumpResourcesParams(self):
        with self.viewModel.transaction() as vm:
            resources = vm.getResources()
            resources.clear()
            for key, value in self._resourcesParams.iteritems():
                resources.set(key, value)

    def _setButtons(self):
        pass

    def _onAction(self, event):
        actionType = event.get('action')
        if actionType in CLOSE_DIALOG_ACTIONS:
            self.destroy()
        elif actionType == MonoDialogTemplateViewModel.ACTION_CONFIRM:
            self._setResult(DialogButtons.SUBMIT)
