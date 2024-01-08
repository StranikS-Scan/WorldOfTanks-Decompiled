# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_completed_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_helpers import getChapterType, getReceivedTankmenCount, getTankmenShopPackages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view_model import BattlePassCompletedTooltipViewModel, ChapterType
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class BattlePassCompletedTooltipView(ViewImpl):
    __battlePass = dependency.descriptor(IBattlePassController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView())
        settings.model = BattlePassCompletedTooltipViewModel()
        super(BattlePassCompletedTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassCompletedTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassCompletedTooltipView, self)._onLoading(*args, **kwargs)
        isBought = all((self.__battlePass.isBought(chapterID=chapter) for chapter in self.__battlePass.getChapterIDs()))
        with self.getViewModel().transaction() as model:
            model.setIsBattlePassPurchased(isBought)
            model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
            model.setChapterType(ChapterType(getChapterType(self.__battlePass.getExtraChapterID())))
            model.setIsAvailableTankmen(self.__isAvailableTankmen(getTankmenShopPackages()))

    def __isAvailableTankmen(self, shopPackages):
        return any((packageCount - getReceivedTankmenCount(tankman) != 0 for tankman, packageCount in shopPackages.iteritems()))
