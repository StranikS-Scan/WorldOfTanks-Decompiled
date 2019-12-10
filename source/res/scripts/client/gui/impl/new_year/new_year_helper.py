# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_helper.py
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.new_year import INewYearController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from gui.shared.gui_items.loot_box import NewYearLootBoxes
_BONUSES_ORDER = ('ny20Fillers', 'battleToken', 'crewBooks', 'customizations', 'dossier', 'vehicles', 'slots', 'blueprints', 'goodies')

@dependency.replace_none_kwargs(nyController=INewYearController)
def fillBonusFormula(formulaViewiewModel, nyController=None):
    with formulaViewiewModel.transaction() as tx:
        tx.setCreditsBonus(nyController.getActiveSettingBonusValue())
        tx.setMultiplier(nyController.getActiveMultiplier())
        tx.setMegaBonus(nyController.getActiveMegaToysBonus())
        tx.setCollectionBonus(nyController.getActiveCollectionsBonus())


def nyBonusSortOrder(bonus):
    if bonus.getName() in _BONUSES_ORDER:
        if bonus.getName() == 'crewBooks':
            for item, _ in bonus.getItems():
                if item.getBookType() == CREW_BOOK_RARITY.PERSONAL:
                    return _BONUSES_ORDER.index(bonus.getName())

        else:
            return _BONUSES_ORDER.index(bonus.getName())
    return len(_BONUSES_ORDER)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getNYLootboxCount(itemsCache=None, lobbyContext=None):
    totalCount = 0
    if lobbyContext.getServerSettings().isLootBoxesEnabled():
        itemsByType = itemsCache.items.tokens.getLootBoxesCountByType()
        totalCount = 0
        for boxType in NewYearLootBoxes.ALL():
            categories = itemsByType.get(boxType, {})
            totalCount += categories.get(TOTAL_KEY, 0)

    return totalCount
