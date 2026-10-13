# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/widgets/vehicle_title_view.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTitleViewModel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_vehicle_view_model import VehicleTypes

class VehicleTitlePresenter(ViewComponent[VehicleTitleViewModel]):

    def __init__(self):
        super(VehicleTitlePresenter, self).__init__(R.aliases.halloween.shared.VehicleTitle(), VehicleTitleViewModel)

    def _onLoading(self, *args, **kwargs):
        super(VehicleTitlePresenter, self)._onLoading(*args, **kwargs)
        self._fillVehicle()

    @property
    def viewModel(self):
        return super(VehicleTitlePresenter, self).getViewModel()

    def _getEvents(self):
        return [(g_currentVehicle.onChanged, self.__onCurrentVehicleChanged)]

    def _fillVehicle(self):
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            with self.viewModel.transaction() as tx:
                tx.setName(vehicle.userName)
                tx.setLevel(vehicle.level)
                tx.setIsPremium(vehicle.isPremium)
                tx.setVehicleType(VehicleTypes(vehicle.type) if vehicle.type != '' else VehicleTypes.NONE)
        return

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            self._fillVehicle()
            return
