# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_collection_bonus_tooltip.py
from frameworks.wulf import ViewFlags, View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_collection_bonus_tooltip_model import NewYearCollectionBonusTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_collection_table_value import NewYearCollectionTableValue
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.single_collection_bonus_model import SingleCollectionBonusModel
from gui.impl.new_year.new_year_helper import fillBonusFormula
from new_year.ny_bonuses import CreditsBonusHelper
from gui.impl import backport
from gui.impl.new_year.views.album.collections_builders import NY20SubCollectionBuilder

class NewYearCollectionBonusTooltip(View):
    __slots__ = ()

    def __init__(self, collection):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_collection_bonus_tooltip.NewYearCollectionBonusTooltip(), flags=ViewFlags.COMPONENT, model=NewYearCollectionBonusTooltipModel())
        settings.args = (collection,)
        super(NewYearCollectionBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewYearCollectionBonusTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearCollectionBonusTooltip, self)._initialize(*args, **kwargs)
        selectedCollection = args[0]
        collectionNames = NY20SubCollectionBuilder.ORDER[:-1]
        collectionBonuses = {collectionName:CreditsBonusHelper.getCollectionBonuses(collectionName) for collectionName in collectionNames}
        collectionLevels = CreditsBonusHelper.getCollectionLevels()
        with self.viewModel.transaction() as tx:
            tx.setSelectedCollection(selectedCollection)
            fillBonusFormula(self.viewModel.bonusFormula)
            for i, interval in enumerate(CreditsBonusHelper.getCollectionBonusLevels()):
                row = NewYearCollectionTableValue()
                fromValue, toValue = interval
                if toValue is not None:
                    row.setInterval(backport.text(R.strings.ny.collectionBonusTooltip.levelsPattern(), lower=fromValue, higher=toValue))
                else:
                    row.setInterval(backport.text(R.strings.ny.collectionBonusTooltip.moreThan(), level=fromValue))
                row.setIsEnabled(CreditsBonusHelper.getCollectionLevelByName(selectedCollection) == i)
                for collectionName in collectionNames:
                    level = collectionLevels[collectionName]
                    bonus = SingleCollectionBonusModel()
                    bonus.setValue(collectionBonuses[collectionName][i])
                    bonus.setIsEnabled(level == i)
                    row.collectionBonuses.addViewModel(bonus)

                self.viewModel.collectionsTable.addViewModel(row)

        return
