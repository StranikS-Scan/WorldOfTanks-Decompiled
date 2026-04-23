# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_vehicle_reward_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_vehicle_reward_tooltip_model import HbVehicleRewardTooltipModel
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache

class HBVehicleRewardTooltip(ViewImpl):
    __slots__ = ()
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hbProgression = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbVehicleRewardTooltip())
        settings.model = HbVehicleRewardTooltipModel()
        super(HBVehicleRewardTooltip, self).__init__(settings)
        discount = 0
        data = self._hbProgression.getProgressionData()
        discountsByLevel = data['discountsByLevel']
        curPoints = data['curPoints']
        for level, levelPoints in enumerate(data['pointsForLevel'], 1):
            if curPoints < levelPoints:
                break
            discount = discountsByLevel.get(level, discount)

        if discount:
            self.getViewModel().setDiscount(discount)
