# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_upgrade_style_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText
from gui.battle_pass.battle_pass_helpers import getStyleForChapter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_upgrade_style_tooltip_view_model import BattlePassUpgradeStyleTooltipViewModel
from gui.impl.pub import ViewImpl

class BattlePassUpgradeStyleTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassUpgradeStyleTooltipView())
        settings.model = BattlePassUpgradeStyleTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattlePassUpgradeStyleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassUpgradeStyleTooltipView, self).getViewModel()

    def _onLoading(self, chapter, level, *args, **kwargs):
        customizationItem = getStyleForChapter(chapter)
        with self.viewModel.transaction() as model:
            if customizationItem is not None:
                model.setStyleId(customizationItem.id)
                model.setStyleName(customizationItem.userName)
                model.setVehicles(getSuitableText(customizationItem, formatVehicle=False))
            else:
                model.setStyleId(0)
                model.setStyleName('')
                model.setVehicles('')
            model.setLevel(level)
        return
