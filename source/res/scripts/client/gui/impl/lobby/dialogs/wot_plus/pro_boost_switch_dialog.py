# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/wot_plus/pro_boost_switch_dialog.py
import json
from collections import namedtuple
import WWISE
from typing import Dict
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_button_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.mono_dialog_template_view_model import MonoDialogTemplateViewModel
from gui.impl.lobby.dialogs.wot_plus.base_dialog import BaseDialog
_ProBoostSwitchDialogVehicleParams = namedtuple('_ProBoostSwitchDialogVehicleParams', ['vehicleItemImagePath',
 'vehicleName',
 'vehicleTier',
 'vehicleIcon'])
_ProBoostSwitchDialogParams = namedtuple('_ProBoostSwitchDialogParams', ['vehicleFrom',
 'vehicleTo',
 'cooldown',
 'bonusPercentage'])

class ProBoostSwitchDialog(BaseDialog):
    LAYOUT_ID = R.views.mono.dialogs.pro_boost_switch_dialog()

    def __init__(self, params, *args, **kwargs):
        contentParams = self._buildContentParams(params)
        resourcesParams = self._buildResourcesParams(params)
        super(ProBoostSwitchDialog, self).__init__(contentParams, resourcesParams, *args, **kwargs)

    def _buildContentParams(self, contentParams):
        return {'fromItemLabelParams': json.dumps({'tier': contentParams.vehicleFrom.vehicleTier,
                                 'type_image': backport.image(contentParams.vehicleFrom.vehicleIcon()),
                                 'name': contentParams.vehicleFrom.vehicleName}),
         'toItemLabelParams': json.dumps({'tier': contentParams.vehicleTo.vehicleTier,
                               'type_image': backport.image(contentParams.vehicleTo.vehicleIcon()),
                               'name': contentParams.vehicleTo.vehicleName}),
         'titleStringParams': json.dumps({'vehicle': contentParams.vehicleTo.vehicleName}),
         'descriptionStringParams': json.dumps({'boostInterval': str(contentParams.cooldown)}),
         'footerStringParams': json.dumps({'bonusPercent': str(contentParams.bonusPercentage) + '%'}),
         'footerHighlightColor': '#FFEEA9'}

    def _buildResourcesParams(self, contentParams):
        return {'fromItemImage': backport.image(contentParams.vehicleFrom.vehicleItemImagePath),
         'fromItemLabel': backport.text(R.strings.dialogs.wotPlusProBoostSwitchDialog.vehicle()),
         'toItemImage': backport.image(contentParams.vehicleTo.vehicleItemImagePath),
         'toItemLabel': backport.text(R.strings.dialogs.wotPlusProBoostSwitchDialog.vehicle()),
         'titleString': backport.text(R.strings.dialogs.wotPlusProBoostSwitchDialog.title()),
         'descriptionString': backport.text(R.strings.dialogs.wotPlusProBoostSwitchDialog.description()),
         'footerString': backport.text(R.strings.dialogs.wotPlusProBoostSwitchDialog.footer()),
         'footerImage': backport.image(R.images.gui.maps.icons.subscription.pro_boost_activation_dialog.pro_boost_footer_icon())}

    def _setButtons(self):
        with self.viewModel.transaction() as model:
            buttonsArray = model.getButtons()
            buttonsArray.clear()
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CONFIRM, R.strings.dialogs.wotPlusProBoostSwitchDialog.confirm(), ButtonType.PRIMARY, False))
            self._addButton(self._buildButton(MonoDialogTemplateViewModel.ACTION_CANCEL, R.strings.dialogs.common.cancel(), ButtonType.SECONDARY, False))

    def _onAction(self, event):
        super(ProBoostSwitchDialog, self)._onAction(event)
        actionType = event.get('action')
        if actionType == MonoDialogTemplateViewModel.ACTION_CONFIRM:
            WWISE.WW_eventGlobal(backport.sound(R.sounds.gui_wotp_proboost_activate()))
