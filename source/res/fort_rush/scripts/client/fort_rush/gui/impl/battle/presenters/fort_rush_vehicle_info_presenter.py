# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/presenters/fort_rush_vehicle_info_presenter.py
from __future__ import absolute_import
import typing
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from gui.impl.lobby.common.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class FortRushVehiclesInfoPresenter(VehiclesInfoPresenter):
    __battleController = dependency.descriptor(IFortRushBattleController)

    def _toModelItem(self, vehicle):
        modelItem = super(FortRushVehiclesInfoPresenter, self)._toModelItem(vehicle)
        modelItem['crystalEarning'] = False
        modelItem['isSuitableVehicle'] = self.__battleController.isSuitableVehicle(vehicle) is None
        return modelItem
