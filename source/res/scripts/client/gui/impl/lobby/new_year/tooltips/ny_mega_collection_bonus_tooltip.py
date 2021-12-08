# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_mega_collection_bonus_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_mega_collection_bonus_tooltip_model import NyMegaCollectionBonusTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_single_mega_collection_bonus_model import NySingleMegaCollectionBonusModel
from gui.impl.new_year.new_year_helper import fillBonusFormula
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from items.components.ny_constants import ToyTypes
from new_year.ny_bonuses import CreditsBonusHelper
from shared_utils import inPercents

class NyMegaCollectionBonusTooltip(View):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self):
        super(NyMegaCollectionBonusTooltip, self).__init__(ViewSettings(R.views.lobby.new_year.tooltips.NyMegaCollectionBonusTooltip(), model=NyMegaCollectionBonusTooltipModel()))

    @property
    def viewModel(self):
        return super(NyMegaCollectionBonusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyMegaCollectionBonusTooltip, self)._initialize(args, kwargs)
        ownedMegaToys = {toy.getToyType():toy.getID() for toy in self._itemsCache.items.festivity.getToys().values() if toy.isMega()}
        bonusValue = inPercents(CreditsBonusHelper.getMegaToysBonusValue())
        slots = self._itemsCache.items.festivity.getSlots()
        with self.viewModel.transaction() as tx:
            tx.setBonusValue(bonusValue)
            for toyType in ToyTypes.MEGA:
                row = NySingleMegaCollectionBonusModel()
                row.setType(toyType)
                row.setValue(bonusValue)
                if toyType in ownedMegaToys:
                    if ownedMegaToys[toyType] in slots:
                        row.setStatus(NySingleMegaCollectionBonusModel.INSTALLED)
                    else:
                        row.setStatus(NySingleMegaCollectionBonusModel.NOT_INSTALLED)
                else:
                    row.setStatus(NySingleMegaCollectionBonusModel.ABSENCE)
                tx.collectionsTable.addViewModel(row)

        fillBonusFormula(self.viewModel.bonusFormula)
