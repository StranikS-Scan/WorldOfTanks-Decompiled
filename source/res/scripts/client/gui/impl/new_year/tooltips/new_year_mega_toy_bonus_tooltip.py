# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_mega_toy_bonus_tooltip.py
from frameworks.wulf import ViewFlags, View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_mega_toy_bonus_tooltip_model import NewYearMegaToyBonusTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.single_mega_toys_bonus_model import SingleMegaToysBonusModel
from gui.impl.new_year.new_year_helper import fillBonusFormula
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from items.components.ny_constants import ToyTypes
from new_year.ny_bonuses import CreditsBonusHelper

class NewYearMegaToyBonusTooltip(View):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self):
        super(NewYearMegaToyBonusTooltip, self).__init__(ViewSettings(R.views.lobby.new_year.tooltips.new_year_mega_toy_tooltip.NewYearMegaToyBonusTooltip(), flags=ViewFlags.COMPONENT, model=NewYearMegaToyBonusTooltipModel()))

    @property
    def viewModel(self):
        return super(NewYearMegaToyBonusTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearMegaToyBonusTooltip, self)._initialize(args, kwargs)
        ownedMegaToys = {toy.getToyType():toy.getID() for toy in self._itemsCache.items.festivity.getToys().values() if toy.isMega()}
        bonusValue = CreditsBonusHelper.getMegaToysBonusValue()
        slots = self._itemsCache.items.festivity.getSlots()
        with self.viewModel.transaction() as tx:
            tx.setBonusValue(bonusValue)
            for toyType in ToyTypes.MEGA:
                row = SingleMegaToysBonusModel()
                row.setType(toyType)
                row.setValue(bonusValue)
                if toyType in ownedMegaToys:
                    if ownedMegaToys[toyType] in slots:
                        row.setStatus(SingleMegaToysBonusModel.INSTALLED)
                    else:
                        row.setStatus(SingleMegaToysBonusModel.NOT_INSTALLED)
                else:
                    row.setStatus(SingleMegaToysBonusModel.ABSENCE)
                tx.toysTable.addViewModel(row)

        fillBonusFormula(self.viewModel.bonusFormula)
