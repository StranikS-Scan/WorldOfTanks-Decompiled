# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_special_vehicles_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_special_vehicles_tooltip_model import HbSpecialVehiclesTooltipModel
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from historical_battles.gui.server_events.game_event.front_progress import FrontProgress
_UNLOCK_VEHICLE_STAGE = 5

class HBSpecialVehiclesTooltip(ViewImpl):
    __slots__ = ()
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hbProgression = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbSpecialVehiclesTooltip())
        settings.model = HbSpecialVehiclesTooltipModel()
        super(HBSpecialVehiclesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HBSpecialVehiclesTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HBSpecialVehiclesTooltip, self)._onLoading(*args, **kwargs)
        front = self._gameEventController.frontController.getSelectedFront()
        vehiclesData = front.getVehiclesByLevel()
        maxLevel = max(vehiclesData.keys())
        vehicles = vehiclesData[maxLevel]
        with self.viewModel.transaction() as model:
            currentStage = self._hbProgression.getCurrentStageData().get('currentStage', 0)
            if currentStage > _UNLOCK_VEHICLE_STAGE:
                model.setIsVehiclesUnlocked(True)
            arr = model.getVehicles()
            arr.clear()
            items = self._itemsCache.items
            for vehCD in vehicles:
                arr.addString(items.getItemByCD(vehCD).shortUserName)

            arr.invalidate()
