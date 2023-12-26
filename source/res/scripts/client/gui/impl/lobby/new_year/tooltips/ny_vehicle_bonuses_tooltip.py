# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_vehicle_bonuses_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_vehicle_bonuses_tooltip_model import NyVehicleBonusesTooltipModel
from gui.impl.pub import ViewImpl

class NyVehicleBonusesTooltip(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__vehicleCD',)

    def __init__(self, *args):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyVehicleBonusesTooltip())
        settings.model = NyVehicleBonusesTooltipModel()
        self.__vehicleCD = args[0] if args else -1
        super(NyVehicleBonusesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyVehicleBonusesTooltip, self).getViewModel()
