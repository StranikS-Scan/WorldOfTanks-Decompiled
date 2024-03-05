# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/battle/cosmic_hud/tooltips/ability_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.tooltips.ability_tooltip_model import AbilityTooltipModel

class AbilityTooltip(ViewImpl):
    __slots__ = ('_ability',)

    def __init__(self, ability):
        settings = ViewSettings(R.views.cosmic_event.battle.cosmic_hud.tooltips.AbilityTooltip())
        settings.model = AbilityTooltipModel()
        super(AbilityTooltip, self).__init__(settings)
        self._ability = ability

    @property
    def viewModel(self):
        return super(AbilityTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(AbilityTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setAbility(self._ability)
