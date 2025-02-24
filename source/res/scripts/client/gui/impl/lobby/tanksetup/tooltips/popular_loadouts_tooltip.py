# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tanksetup/tooltips/popular_loadouts_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tanksetup.tooltips.popular_loadouts_tooltip_model import PopularLoadoutsTooltipModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class PopularLoadoutsTooltip(ViewImpl):
    __slots__ = ('_vehCompDescr', '_optionalDevicesResultType')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehCompDescr, optionalDevicesResultType):
        settings = ViewSettings(R.views.lobby.tanksetup.tooltips.PopularLoadoutsTooltip())
        settings.model = PopularLoadoutsTooltipModel()
        self._vehCompDescr = vehCompDescr
        self._optionalDevicesResultType = optionalDevicesResultType
        super(PopularLoadoutsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PopularLoadoutsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setOptionalDevicesResultType(self._optionalDevicesResultType)
            if self._vehCompDescr:
                vehicle = self.__itemsCache.items.getItemByCD(self._vehCompDescr)
                if vehicle:
                    fillVehicleModel(model, vehicle)
