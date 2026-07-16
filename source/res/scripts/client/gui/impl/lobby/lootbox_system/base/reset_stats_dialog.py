# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/reset_stats_dialog.py
from typing import Dict
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import MonoButtonTemplate
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_view_model import MonoDialogTemplateViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.lootbox_system.base.common import getTextResource
CLOSE_DIALOG_ACTIONS = (MonoDialogTemplateViewModel.ACTION_CLOSE, MonoDialogTemplateViewModel.ACTION_ESCAPE, MonoDialogTemplateViewModel.ACTION_CANCEL)

class ResetStatsDialog(FullScreenDialogBaseView):
    LAYOUT_ID = R.views.mono.dialogs.default_dialog()
    VIEW_MODEL = MonoDialogTemplateViewModel
    DEFAULT_DIMMER_ALPHA = 0.8

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=self.LAYOUT_ID, model=self.VIEW_MODEL())
        settings.args = args
        settings.kwargs = kwargs
        super(ResetStatsDialog, self).__init__(settings, *args, **kwargs)
        self._buttons = self.viewModel.getButtons()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onAction, self._onAction),)

    def _onLoading(self, *args, **kwargs):
        super(ResetStatsDialog, self)._onLoading(*args, **kwargs)
        self.__eventName = kwargs.get('eventName')
        self._resourcesParams = self._buildResourcesParams()
        self._dumpResourcesParams()
        self._setButtons()
        with self.viewModel.transaction() as model:
            model.setDimmerAlpha(self.DEFAULT_DIMMER_ALPHA)

    def _addButton(self, monoButton):
        self._buttons.addViewModel(monoButton.viewModel)

    def _buildButton(self, action, label, buttonType, isDisabled=False):
        button = MonoButtonTemplate(action, label, 'Button', buttonType, isDisabled)
        return button

    def _dumpResourcesParams(self):
        with self.viewModel.transaction() as vm:
            resources = vm.getResources()
            resources.clear()
            for key, value in self._resourcesParams.iteritems():
                resources.set(key, value)

    def _setButtons(self):
        with self.viewModel.transaction() as vm:
            buttonsArray = vm.getButtons()
            buttonsArray.clear()
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CONFIRM, R.strings.lootbox_system.confirmResetLootBoxStatistics.submit(), ButtonType.PRIMARY, False))
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CANCEL, R.strings.lootbox_system.confirmResetLootBoxStatistics.cancel(), ButtonType.SECONDARY, False))

    def _onAction(self, event):
        actionType = event.get('action')
        if actionType in CLOSE_DIALOG_ACTIONS:
            self._setResult(DialogButtons.CANCEL)
        elif actionType == MonoDialogTemplateViewModel.ACTION_CONFIRM:
            self._setResult(DialogButtons.SUBMIT)

    def _buildResourcesParams(self):
        descriptionPath = ['confirmResetLootBoxStatistics', 'description']
        return {'titleString': backport.text(R.strings.lootbox_system.confirmResetLootBoxStatistics.title()),
         'descriptionString': backport.text(getTextResource(descriptionPath, self.__eventName)())}
