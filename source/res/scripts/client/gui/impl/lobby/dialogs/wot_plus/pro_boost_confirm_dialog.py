# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/wot_plus/pro_boost_confirm_dialog.py
import json
from collections import namedtuple
import WWISE
from typing import Dict
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_view_model import MonoDialogTemplateViewModel
from gui.impl.lobby.dialogs.wot_plus.base_dialog import BaseDialog
_ProBoostConfirmDialogParams = namedtuple('confirmDialogParams', ['vehicleName', 'cooldown', 'bonusPercentage'])

class ProBoostConfirmDialog(BaseDialog):

    def __init__(self, contentParams, *args, **kwargs):
        contentParams = self._buildContentParams(contentParams)
        resourcesParams = self._buildResourcesParams()
        super(ProBoostConfirmDialog, self).__init__(contentParams, resourcesParams, *args, **kwargs)

    def _buildContentParams(self, contentParams):
        return {'titleStringParams': json.dumps({'vehicle': contentParams.vehicleName}),
         'descriptionStringParams': json.dumps({'boostInterval': str(contentParams.cooldown)}),
         'footerStringParams': json.dumps({'bonusPercent': str(contentParams.bonusPercentage) + '%'}),
         'footerHighlightColor': '#FFEEA9'}

    def _buildResourcesParams(self):
        return {'titleString': backport.text(R.strings.dialogs.wotPlusProBoostActivationDialog.title()),
         'iconImage': backport.image(R.images.gui.maps.icons.subscription.pro_boost_activation_dialog.pro_boost_activation_icon()),
         'descriptionString': backport.text(R.strings.dialogs.wotPlusProBoostActivationDialog.description()),
         'footerString': backport.text(R.strings.dialogs.wotPlusProBoostActivationDialog.footer()),
         'footerImage': backport.image(R.images.gui.maps.icons.subscription.pro_boost_activation_dialog.pro_boost_footer_icon())}

    def _setButtons(self):
        with self.viewModel.transaction() as vm:
            buttonsArray = vm.getButtons()
            buttonsArray.clear()
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CONFIRM, R.strings.dialogs.wotPlusProBoostActivationDialog.confirm(), ButtonType.PRIMARY, False))
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CANCEL, R.strings.dialogs.common.cancel(), ButtonType.SECONDARY, False))

    def _onAction(self, event):
        super(ProBoostConfirmDialog, self)._onAction(event)
        actionType = event.get('action')
        if actionType == MonoDialogTemplateViewModel.ACTION_CONFIRM:
            WWISE.WW_eventGlobal(backport.sound(R.sounds.gui_wotp_proboost_activate()))
