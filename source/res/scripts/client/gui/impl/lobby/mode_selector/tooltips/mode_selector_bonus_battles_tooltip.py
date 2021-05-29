# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/tooltips/mode_selector_bonus_battles_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.bonus_battles_tooltip_model import BonusBattlesTooltipModel
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class BonusBattlesTooltipView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.mode_selector.tooltips.BonusBattlesTooltip(), model=BonusBattlesTooltipModel())
        super(BonusBattlesTooltipView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        rankedController = dependency.instance(IRankedBattlesController)
        bonusBattles = rankedController.getClientBonusBattlesCount()
        model = self.getViewModel()
        model.setBattles(bonusBattles)
