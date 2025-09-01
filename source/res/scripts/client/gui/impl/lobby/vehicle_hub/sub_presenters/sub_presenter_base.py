# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/sub_presenter_base.py
from __future__ import absolute_import
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle
    from gui.impl.lobby.vehicle_hub.vehicle_hub_main_view import VehicleHubCtx

class SubPresenterBase(SubModelPresenter):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, model, parentView):
        self.__vhCtx = None
        super(SubPresenterBase, self).__init__(model, parentView)
        return

    @property
    def vehicleHubCtx(self):
        return self.__vhCtx

    @property
    def currentVehicle(self):
        return self._itemsCache.items.getItemByCD(self.__vhCtx.intCD) if self.vehicleHubCtx else None

    def setVehicleHubCtx(self, vhCtx):
        self.__vhCtx = vhCtx

    def initialize(self, vhCtx, *args, **kwargs):
        super(SubPresenterBase, self).initialize(*args, **kwargs)
        self.setVehicleHubCtx(vhCtx)
