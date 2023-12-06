# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_collection_bonus_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_collection_bonus_tooltip_model import NyCollectionBonusTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_collection_table_value_model import NyCollectionTableValueModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_single_collection_bonus_model import NySingleCollectionBonusModel
from new_year.ny_bonuses import BonusHelper
from gui.impl import backport
from gui.impl.lobby.new_year.albums.collections_builders import NY20SubCollectionBuilder
from shared_utils import inPercents

class NyCollectionBonusTooltip(View):
    __slots__ = ()

    def __init__(self, collection):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyCollectionBonusTooltip(), model=NyCollectionBonusTooltipModel())
        settings.args = (collection,)
        super(NyCollectionBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyCollectionBonusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyCollectionBonusTooltip, self)._onLoading(*args, **kwargs)
        selectedCollection = args[0]
        collectionNames = NY20SubCollectionBuilder.ORDER[:-1]
        collectionBonuses = {collectionName:BonusHelper.getCommonCollectionBonuses(collectionName) for collectionName in collectionNames}
        collectionLevels = BonusHelper.getCollectionLevels()
        with self.viewModel.transaction() as tx:
            tx.setSelectedCollection(selectedCollection)
            for i, interval in enumerate(BonusHelper.getCollectionBonusLevels()):
                row = NyCollectionTableValueModel()
                fromValue, toValue = interval
                if toValue is not None:
                    row.setInterval(backport.text(R.strings.ny.collectionBonusTooltip.levelsPattern(), lower=fromValue, higher=toValue))
                else:
                    row.setInterval(backport.text(R.strings.ny.collectionBonusTooltip.moreThan(), level=fromValue))
                row.setIsEnabled(BonusHelper.getCollectionLevelByName(selectedCollection) == i)
                for collectionName in collectionNames:
                    level = collectionLevels[collectionName]
                    bonus = NySingleCollectionBonusModel()
                    bonus.setValue(inPercents(collectionBonuses[collectionName][i], digitsToRound=2))
                    bonus.setIsEnabled(level == i)
                    row.collectionBonuses.addViewModel(bonus)

                self.viewModel.collectionsTable.addViewModel(row)

        return
