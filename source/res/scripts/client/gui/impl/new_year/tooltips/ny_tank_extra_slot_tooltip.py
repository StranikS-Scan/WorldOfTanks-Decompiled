# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/ny_tank_extra_slot_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_tank_extra_slot_tooltip_model import NyTankExtraSlotTooltipModel
from new_year.ny_constants import PERCENT
from new_year.vehicle_branch import getExtraSlotBonusesConfig

class NYTankExtraSlotTooltipContent(View):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.ny_tank_extra_slot_tooltip.NYTankExtraSlotTooltipContent())
        settings.model = NyTankExtraSlotTooltipModel()
        super(NYTankExtraSlotTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NYTankExtraSlotTooltipContent, self).getViewModel()

    def _initialize(self):
        super(NYTankExtraSlotTooltipContent, self)._initialize()
        with self.viewModel.transaction() as model:
            for _, (bonusType, bonusValue) in getExtraSlotBonusesConfig().iteritems():
                if bonusType == 'xpFactor':
                    model.setXpFactor(PERCENT * bonusValue)
                if bonusType == 'freeXPFactor':
                    model.setFreeXPFactor(PERCENT * bonusValue)
                if bonusType == 'tankmenXPFactor':
                    model.setTankmenXPFactor(PERCENT * bonusValue)
