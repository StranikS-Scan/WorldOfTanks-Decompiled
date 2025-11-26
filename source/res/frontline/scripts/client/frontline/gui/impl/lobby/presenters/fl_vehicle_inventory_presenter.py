# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/fl_vehicle_inventory_presenter.py
from frontline.gui.impl.lobby.tooltips.carousel_vehicle_tooltip import FLCarouselVehicleTooltipView
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.gen import R

class FLVehicleInventoryPresenter(VehicleInventoryPresenter):

    def _getIsBpEntityValid(self):
        return False

    def createToolTipContent(self, event, contentID):
        return FLCarouselVehicleTooltipView(event.getArgument('inventoryId')) if contentID == R.views.mono.hangar.vehicle_tooltip() else super(FLVehicleInventoryPresenter, self).createToolTipContent(event=event, contentID=contentID)
