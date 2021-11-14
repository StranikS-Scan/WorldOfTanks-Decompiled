# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/wot_plus_vehicle_preview.py
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.daapi.view.meta.VehiclePreviewWotPlusPanelMeta import VehiclePreviewWotPlusPanelMeta
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
import async as future_async
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatDate
from gui.shared.event_dispatcher import showWotPlusRentDialog
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName
from gui.shop import showRentVehicleOverlay

class WotPlusVehiclePreview(VehiclePreview):

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.WOT_PLUS_PANEL_LINKAGE)


class VPWotPlusPanel(VehiclePreviewWotPlusPanelMeta):

    def _populate(self):
        super(VPWotPlusPanel, self)._populate()
        self.as_setDataS({'rentButtonLabel': backport.text(R.strings.subscription.rentButton.label()),
         'isRentButtonEnable': True})

    def onRentClick(self):
        self.__purchaseSubRent()

    def setOffers(self, offers):
        self.__buyParams = offers[0].buyParams

    @future_async.async
    def __purchaseSubRent(self):

        def successCallback():
            showRentVehicleOverlay(self.__buyParams)

        title = backport.text(R.strings.dialogs.wotPlusRental.title())
        title = title % g_currentPreviewVehicle.item.userName
        date = formatDate(BigWorld.player().renewableSubscription.getExpiryTime())
        description = backport.text(R.strings.dialogs.wotPlusRental.description()) % date
        iconName = getIconResourceName(getNationLessName(g_currentPreviewVehicle.item.name))
        icon = R.images.gui.maps.shop.vehicles.c_360x270.dyn(iconName)()
        yield future_async.await(showWotPlusRentDialog(title, description, icon, successCallback))
