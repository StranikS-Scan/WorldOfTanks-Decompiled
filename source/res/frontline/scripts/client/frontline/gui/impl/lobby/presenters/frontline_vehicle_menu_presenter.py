# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/frontline_vehicle_menu_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_presenter import VehicleMenuPresenter

class FrontlineVehicleMenuPresenter(VehicleMenuPresenter):

    def _getEasyEquipState(self):
        return VehicleMenuModel.UNAVAILABLE
