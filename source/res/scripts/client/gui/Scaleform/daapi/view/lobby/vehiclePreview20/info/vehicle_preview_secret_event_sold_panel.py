# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_secret_event_sold_panel.py
from adisp import process
from gui import makeHtmlString, DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import RestoreExchangeCreditsMeta
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.VehiclePreviewSecretEventSoldPanelMeta import VehiclePreviewSecretEventSoldPanelMeta
from gui.impl import backport
from gui.impl.backport import getIntegralFormat
from gui.impl.gen import R
from gui.shared.event_dispatcher import mayObtainWithMoneyExchange, mayObtainForMoney, showVehicleBuyDialog, getShortageForObtainingForMoney
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController

class VehiclePreviewSecretEventSoldPanel(VehiclePreviewSecretEventSoldPanelMeta):
    gameEventController = dependency.descriptor(IGameEventController)

    @process
    def onRestoreClick(self):
        vehicle = self.gameEventController.getHeroTank().getInventoryItem()
        itemCD = self.gameEventController.getHeroTank().getVehicleCD()
        if mayObtainForMoney(vehicle.restorePrice):
            showVehicleBuyDialog(vehicle)
        elif mayObtainWithMoneyExchange(vehicle.restorePrice):
            isOk, _ = yield DialogsInterface.showDialog(RestoreExchangeCreditsMeta(itemCD=itemCD))
            if isOk:
                showVehicleBuyDialog(vehicle)

    def _populate(self):
        super(VehiclePreviewSecretEventSoldPanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateData)
        self.__updateData()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(VehiclePreviewSecretEventSoldPanel, self)._dispose()

    def __updateData(self, *args):
        self.as_setDataS(self.__getVO())

    def __getVO(self):
        vehicle = self.gameEventController.getHeroTank().getInventoryItem()
        restorePrice = vehicle.restorePrice
        restoreButtonEnabled = mayObtainForMoney(restorePrice) or mayObtainWithMoneyExchange(restorePrice)
        section = 'secretEventSoldTankRestoreCost' if restoreButtonEnabled else 'secretEventSoldTankRestoreCostError'
        restoreCostLabel = makeHtmlString('html_templates:lobby/vehicle_preview', section, {'value': getIntegralFormat(restorePrice.credits)})
        rBuyButton = R.strings.tooltips.vehiclePreview.buyButton
        tooltip = makeTooltip(text_styles.critical(backport.text(rBuyButton.notEnoughCredits.header())), text_styles.concatStylesToMultiLine(backport.text(rBuyButton.notEnoughCredits.body()), '', text_styles.concatStylesWithSpace(backport.text(R.strings.tooltips.vehiclePreview.notEnough()), text_styles.credits(backport.getIntegralFormat(getShortageForObtainingForMoney(restorePrice).credits)), icons.credits(vspace=-2)))) if not restoreButtonEnabled else ''
        return {'restoreButtonEnabled': restoreButtonEnabled,
         'restoreButtonLabel': backport.text(R.strings.event.previewWindow.restoreButton.label()),
         'restoreButtonHeader': backport.text(R.strings.event.previewWindow.restoreButton.header()),
         'restoreCostLabel': restoreCostLabel,
         'buttonTooltip': tooltip,
         'isShowSpecialTooltip': False}
