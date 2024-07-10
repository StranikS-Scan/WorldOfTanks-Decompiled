# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/ability_tooltip_view.py
from frameworks.wulf import ViewSettings
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.ability_tooltip_view_model import AbilityTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class AbilityTooltipView(ViewImpl):
    __slots__ = ('_abilityData',)

    def __init__(self, abilityData):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.AbilityTooltipView())
        settings.model = AbilityTooltipViewModel()
        self._abilityData = abilityData
        super(AbilityTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AbilityTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        if self._abilityData is None:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.setTitle(self._abilityData.title)
                tx.setIconName(self._abilityData.iconName)
                tx.setCooldownSeconds(self._abilityData.cooldownSeconds)
                tx.setDescription(self._abilityData.description)
            return
