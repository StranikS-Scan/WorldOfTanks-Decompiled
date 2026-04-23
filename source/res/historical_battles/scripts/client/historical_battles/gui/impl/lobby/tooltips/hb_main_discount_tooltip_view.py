# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_main_discount_tooltip_view.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from skeletons.gui.shared import IItemsCache
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_main_discount_tooltip_view_model import HbMainDiscountTooltipViewModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HbMainDiscountTooltipView(ViewImpl):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IGameEventController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbMainDiscountTooltipView())
        settings.model = HbMainDiscountTooltipViewModel()
        super(HbMainDiscountTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HbMainDiscountTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HbMainDiscountTooltipView, self)._onLoading()
        heroTankController = self.__gameEventController.heroTank
        heroTankVehicle = heroTankController.getVehicle()
        isVehicleOwned = heroTankController.hasHeroVehicle()
        mainDiscountConf = self.__gameEventController.getMainDiscount()
        maxTokenCount = mainDiscountConf['maxTokenCount']
        tokenCount = maxTokenCount if isVehicleOwned else self.__itemsCache.items.tokens.getTokenCount(mainDiscountConf['tokenName'])
        with self.viewModel.transaction() as model:
            model.setMaxDiscountCount(maxTokenCount)
            model.setCurrentDiscountCount(tokenCount)
            model.setCurrentDiscountPercent(tokenCount * mainDiscountConf['discountPerToken'])
            model.setIcon(backport.image(R.images.gui.maps.icons.quests.bonuses.small.historical_battles_main_discount()))
            model.setVehicleName(heroTankVehicle.userName)
            model.setVehicleLvl(heroTankVehicle.level)
