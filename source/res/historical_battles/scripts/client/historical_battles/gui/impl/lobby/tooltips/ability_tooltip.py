# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/ability_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from items import vehicles
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.ability_tooltip_model import AbilityTooltipModel
from gui.impl.pub import ViewImpl

class AbilityTooltip(ViewImpl):

    def __init__(self, abilityID, isRoleAbility):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.AbilityTooltip())
        model = AbilityTooltipModel()
        ability = vehicles.g_cache.equipments()[abilityID]
        model.setTitle(ability.userString)
        model.setDescr(ability.description)
        model.setIcon(ability.iconName)
        model.setIsRoleAbility(bool(isRoleAbility))
        settings.model = model
        super(AbilityTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AbilityTooltip, self).getViewModel()
