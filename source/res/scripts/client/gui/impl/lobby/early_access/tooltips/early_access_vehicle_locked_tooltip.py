# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/tooltips/early_access_vehicle_locked_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.tooltips.early_access_vehicle_locked_tooltip_model import EarlyAccessVehicleLockedTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController

class EarlyAccessVehicleLockedTooltip(ViewImpl):
    __slots__ = ()
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessVehicleLockedTooltip())
        settings.model = EarlyAccessVehicleLockedTooltipModel()
        super(EarlyAccessVehicleLockedTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessVehicleLockedTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        _, endDate = self.__earlyAccessCtrl.getSeasonInterval()
        self.viewModel.setWillAvailableTimestamp(endDate)
