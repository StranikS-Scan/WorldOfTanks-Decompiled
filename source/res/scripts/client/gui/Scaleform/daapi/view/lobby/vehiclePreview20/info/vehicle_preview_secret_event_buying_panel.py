# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_secret_event_buying_panel.py
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.VehiclePreviewSecretEventBuyingPanelMeta import VehiclePreviewSecretEventBuyingPanelMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import getGoldFormat, getIntegralFormat
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import mayObtainForMoney
from gui.shared.formatters import text_styles
from gui.shared.money import Currency, Money
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController

class VehiclePreviewSecretEventBuyingPanel(VehiclePreviewSecretEventBuyingPanelMeta):
    gameEventController = dependency.descriptor(IGameEventController)

    def onBuyClick(self):
        vehicle = self.gameEventController.getHeroTank().getStockItem()
        event_dispatcher.showVehicleBuyDialogFromEvent(vehicle)

    def _populate(self):
        super(VehiclePreviewSecretEventBuyingPanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self._draw)
        self.gameEventController.onProgressChanged += self._draw
        self._draw()

    def _dispose(self):
        self.gameEventController.onProgressChanged -= self._draw
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(VehiclePreviewSecretEventBuyingPanel, self)._dispose()

    def _draw(self, *args):
        self.as_setDataS(self._getVO())

    def _getVO(self):
        pw = R.strings.event.previewWindow
        htmlTemplate = 'html_templates:lobby/vehicle_preview'
        message = text_styles.concatStylesToSingleLine(self._getMessage(), makeHtmlString(htmlTemplate, 'secretEventInfoIcon'))
        eventHeroTank = self.gameEventController.getHeroTank()
        currency, defAmount = eventHeroTank.getDefPrice()
        currency, amount = eventHeroTank.getCurrentPrice()
        discount = eventHeroTank.getDiscount()
        price = Money.makeFrom(currency, defAmount)
        haveEnoughMoney = mayObtainForMoney(price)
        formatter = getGoldFormat if currency == Currency.GOLD else getIntegralFormat
        costTemplate = 'secretEventCostGold' if currency == Currency.GOLD else 'secretEventCostCredits'
        if not haveEnoughMoney:
            costTemplate += 'NotEnough'
        buyValue = makeHtmlString(htmlTemplate, costTemplate, {'value': formatter(amount)})
        buyValueOld = makeHtmlString(htmlTemplate, 'secretEventOldCost', {'value': formatter(defAmount)}) if discount != 0 else ''
        return {'messageLabel': message,
         'buyButtonEnabled': True,
         'buyButtonLabel': backport.text(pw.buyButton.label()),
         'messageTooltip': TOOLTIPS_CONSTANTS.EVENT_VEHICLE_PREVIEW_MESSAGE,
         'vehicleCost': {'buyValueLabel': buyValue,
                         'buyValueOldLabel': buyValueOld,
                         'discount': discount}}

    def _getMessage(self):
        return backport.text(R.strings.event.previewWindow.shop.message())
