# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tanksetup/tooltips/not_enough_data_for_popular_loadouts_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tanksetup.tooltips.not_enough_data_for_popular_loadouts_tooltip_model import NotEnoughDataForPopularLoadoutsTooltipModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class NotEnoughDataForPopularLoadoutsTooltip(ViewImpl):
    __slots__ = ('_vehCompDescr',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehCompDescr):
        settings = ViewSettings(R.views.lobby.tanksetup.tooltips.NotEnoughDataForPopularLoadoutsTooltip())
        settings.model = NotEnoughDataForPopularLoadoutsTooltipModel()
        self._vehCompDescr = vehCompDescr
        super(NotEnoughDataForPopularLoadoutsTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        vehicle = self.__itemsCache.items.getItemByCD(self._vehCompDescr)
        with self.viewModel.transaction() as model:
            fillVehicleModel(model, vehicle)

    @property
    def viewModel(self):
        return super(NotEnoughDataForPopularLoadoutsTooltip, self).getViewModel()
