# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_secret_event_buying_action_panel.py
from adisp import process
from gui.Scaleform.daapi.view.meta.VehiclePreviewSecretEventBuyingActionPanelMeta import VehiclePreviewSecretEventBuyingActionPanelMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import event_dispatcher

class VehiclePreviewSecretEventBuyingActionPanel(VehiclePreviewSecretEventBuyingActionPanelMeta):

    def onActionClick(self):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)
        event_dispatcher.loadSecretEventTabMenu(ActionMenuModel.MISSION)

    def _populate(self):
        super(VehiclePreviewSecretEventBuyingActionPanel, self)._populate()
        self.as_setActionDataS({'orLabel': backport.text(R.strings.event.previewWindow.c_or()),
         'actionButtonEnabled': True,
         'actionButtonLabel': backport.text(R.strings.event.previewWindow.actionButton.label())})

    def _getMessage(self):
        return backport.text(R.strings.event.previewWindow.message())

    @process
    def __doSelectAction(self, actionName):
        yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(actionName))
