# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_secret_event_bought_panel.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.VehiclePreviewSecretEventBoughtPanelMeta import VehiclePreviewSecretEventBoughtPanelMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController

class VehiclePreviewSecretEventBoughtPanel(VehiclePreviewSecretEventBoughtPanelMeta):
    gameEventController = dependency.descriptor(IGameEventController)

    def onShowInHangarClick(self):
        event_dispatcher.selectVehicleInHangar(self.gameEventController.getHeroTank().getVehicleCD())

    def _populate(self):
        super(VehiclePreviewSecretEventBoughtPanel, self)._populate()
        self.__updateData()

    def __updateData(self):
        self.as_setDataS(self.__getVO())

    def __getVO(self):
        return {'showButtonEnabled': True,
         'showButtonHeader': makeHtmlString('html_templates:lobby/vehicle_preview', 'secretEventReceivedTank'),
         'showButtonLabel': backport.text(R.strings.event.previewWindow.showButton.label())}
