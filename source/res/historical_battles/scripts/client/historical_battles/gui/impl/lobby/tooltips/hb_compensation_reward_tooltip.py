# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_compensation_reward_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles_common.helpers_common import parseCompensationToken
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_compensation_reward_tooltip_model import HbCompensationRewardTooltipModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HbCompensationRewardTooltip(ViewImpl):
    __slots__ = ('__compensationTokenID',)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID, tokenID):
        settings = ViewSettings(layoutID)
        settings.model = HbCompensationRewardTooltipModel()
        super(HbCompensationRewardTooltip, self).__init__(settings)
        self.__compensationTokenID = tokenID

    @property
    def viewModel(self):
        return super(HbCompensationRewardTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HbCompensationRewardTooltip, self)._onLoading()
        self.__updateModel()

    def __updateModel(self):
        heroTankController = self.__gameEventController.heroTank
        heroTankVehicle = heroTankController.getVehicle()
        currency, amount = parseCompensationToken(self.__compensationTokenID)
        with self.viewModel.transaction() as model:
            model.setVehicleName(heroTankVehicle.userName)
            model.setVehicleLvl(heroTankVehicle.level)
            model.setCurrencyName(currency)
            model.setCurrencyAmount(amount)
