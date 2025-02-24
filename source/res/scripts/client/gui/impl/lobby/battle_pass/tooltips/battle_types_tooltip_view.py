# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_types_tooltip_view.py
from constants import MAX_VEHICLE_LEVEL
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.battle_pass.battle_pass_helpers import fillBattleTypes
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_types_tooltip_view_model import BattleTypesTooltipViewModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IBattlePassController

class BattleTypesTooltipView(ViewImpl):
    __slots__ = ()
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattleTypesTooltipView())
        settings.model = BattleTypesTooltipViewModel()
        super(BattleTypesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleTypesTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleTypesTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setVehicleLevelFrom(self.__battlePassController.getMinVehLevelToEarnPoints())
            model.setVehicleLevelTo(MAX_VEHICLE_LEVEL)
            fillBattleTypes(model)
