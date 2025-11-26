# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_vehicle_inventory_presenter.py
from __future__ import absolute_import
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.lobby.tooltips.carousel_vehicle_tooltip import getUnsuitable2queueTooltip

class FunRandomVehicleInventoryPresenter(VehicleInventoryPresenter, FunAssetPacksMixin, FunSubModesWatcher):

    def createToolTip(self, event):
        if event.contentID == R.views.mono.hangar.vehicle_tooltip():
            desiredSubMode = self.getDesiredSubMode()
            if desiredSubMode is not None:
                vehicle = self._itemsCache.items.getVehicle(event.getArgument('inventoryId'))
                validationResult = desiredSubMode.isSuitableVehicle(vehicle)
                if validationResult is not None:
                    resPath = R.strings.fun_random.funRandomCarousel.lockedTooltip
                    return getUnsuitable2queueTooltip(self.getParentWindow(), event, validationResult, resPath, modeName=self.getModeUserName())
        return super(FunRandomVehicleInventoryPresenter, self).createToolTip(event)
