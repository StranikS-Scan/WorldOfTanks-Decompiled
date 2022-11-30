# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_helper.py
from constants import LOOTBOX_TOKEN_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.tooltips.ny_discount_reward_tooltip import NyDiscountRewardTooltip
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from helpers import dependency, getLanguageCode, int2roman
from items import new_year
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.ny_constants import Ny23CoinToken, NyATMReward
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from gui.shared.gui_items.loot_box import NewYearLootBoxes
_ARABIC_NUMBERS_LANGUAGE_CODES = ('ko', 'no')
IS_ROMAN_NUMBERS_ALLOWED = getLanguageCode() not in _ARABIC_NUMBERS_LANGUAGE_CODES
_BONUSES_ORDER = ({'bonusName': 'tmanToken'},
 {'bonusName': 'battleToken',
  'tagStartsWith': LOOTBOX_TOKEN_PREFIX},
 {'bonusName': 'entitlements'},
 {'bonusName': 'crewBooks',
  'tag': CREW_BOOK_RARITY.PERSONAL},
 {'bonusName': 'dossier',
  'tag': 'isPrefixBadge'},
 {'bonusName': 'customizations',
  'tag': 'style'},
 {'bonusName': 'customizations'},
 {'bonusName': 'dossier'},
 {'bonusName': 'vehicles'},
 {'bonusName': 'slots'},
 {'bonusNameStartsWith': 'BlueprintNation'},
 {'bonusNameStartsWith': 'Blueprint'},
 {'bonusName': 'goodies'},
 {'bonusName': 'crewBooks'})
_NATION_ORDER = ('ussr', 'germany', 'usa', 'china', 'france', 'uk', 'japan', 'sweden', 'italy', 'czech', 'poland')
BLUEPRINT_NATION_ORDER = tuple(('{}_{}'.format(BlueprintsBonusSubtypes.NATION_FRAGMENT, n) for n in _NATION_ORDER))
CREEBOOK_NATION_ORDER = tuple(('{}_{}'.format(CREW_BOOK_RARITY.CREW_RARE, n) for n in _NATION_ORDER))
_TOKEN_TO_NAME = {Ny23CoinToken.ID: Ny23CoinToken.TYPE,
 NyATMReward.MARKETPLACE_TOKEN: NyATMReward.MARKETPLACE,
 NyATMReward.DOG_TOKEN: NyATMReward.DOG}

def __getAdditionalNameBattleToken(bonus):
    tokens = [ t for t in bonus.getTokens() ]
    for tokenID, userName in _TOKEN_TO_NAME.iteritems():
        if tokenID in tokens:
            return userName

    return 'lootBox' if any((t.startswith(LOOTBOX_TOKEN_PREFIX) and t != Ny23CoinToken.ID for t in tokens)) else bonus.getName()


def __getAdditionalNameCustomizations(bonus):
    return 'customizations_style' if bonus.getC11nItem(first(bonus.getCustomizations())).itemTypeName == 'style' else bonus.getName()


def __getAdditionalNameGoodies(bonus):
    booster = first(bonus.getBoosters().keys())
    return booster.boosterGuiType if booster else bonus.getName()


def __getAdditionalNameCrewBooks(bonus):
    item = first(bonus.getItems())[0]
    if item.getBookType() == CREW_BOOK_RARITY.CREW_RARE:
        nation = item.getNation()
        if nation in _NATION_ORDER:
            return '{}_{}'.format(CREW_BOOK_RARITY.CREW_RARE, nation)
    return item.getBookType()


def __getAdditionalNameDossier(bonus):
    bonusRecords = bonus.getRecords()
    if bonusRecords:
        achievementType, _ = first(bonusRecords.keys())
        return achievementType
    return bonus.getName()


def __getAdditionalNameBlueprint(bonus):
    blueprintName = bonus.getBlueprintName()
    if blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
        nation = bonus.getImageCategory()
        if nation in _NATION_ORDER:
            return '{}_{}'.format(BlueprintsBonusSubtypes.NATION_FRAGMENT, nation)
    return blueprintName


ADDITIONAL_BONUS_NAME_GETTERS = {'battleToken': __getAdditionalNameBattleToken,
 'blueprints': __getAdditionalNameBlueprint,
 'customizations': __getAdditionalNameCustomizations,
 'crewBooks': __getAdditionalNameCrewBooks,
 'goodies': __getAdditionalNameGoodies,
 'dossier': __getAdditionalNameDossier}
_BONUSES_ORDER_CACHE = (('customizations', 'style'),
 ('customizations', 'projectionDecal'),
 ('customizations', 'emblem'),
 ('customizations', 'inscription'))

def nyBonusSortOrder(preformattedBonus):
    bonusName, tags = preformattedBonus.bonusName, preformattedBonus.postProcessTags
    if isinstance(tags, tuple):
        tags = '' if not tags else tags[0]
    primaryKey = (bonusName, tags)
    if primaryKey in _BONUSES_ORDER_CACHE:
        return _BONUSES_ORDER_CACHE.index(primaryKey)
    result = len(_BONUSES_ORDER)
    for index, criteria in enumerate(_BONUSES_ORDER):
        if 'bonusName' in criteria and bonusName != criteria['bonusName']:
            continue
        if 'bonusNameStartsWith' in criteria and not bonusName.startswith(criteria['bonusNameStartsWith']):
            continue
        if 'tag' in criteria and criteria['tag'] not in tags:
            continue
        if 'tagStartsWith' in criteria and not tags.startswith(criteria['tagStartsWith']):
            continue
        result = index
        break

    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getRewardKitsCount(itemsCache=None, lobbyContext=None):
    totalCount = 0
    if lobbyContext.getServerSettings().isLootBoxesEnabled():
        itemsByType = itemsCache.items.tokens.getLootBoxesCountByType()
        totalCount = 0
        categories = itemsByType.get(NewYearLootBoxes.PREMIUM, {})
        totalCount += categories.get(TOTAL_KEY, 0)
    return totalCount


def nyCreateToolTipContentDecorator(func):

    def wrapper(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyDiscountRewardTooltip():
            variadicID, discount, rewardLevel = event.getArgument('variadicID'), event.getArgument('discount'), event.getArgument('rewardLevel')
            return NyDiscountRewardTooltip(variadicID, discount, rewardLevel)
        return func(self, event, contentID)

    return wrapper


def backportTooltipDecorator(tooltipItemsName='_tooltips', dataExtractor=None):

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipId = event.getArgument('tooltipId')
                tooltipItems = getattr(self, tooltipItemsName, {})
                tooltipData = tooltipItems.get(tooltipId, None)
                if tooltipData is not None:
                    if dataExtractor:
                        tooltipData = dataExtractor(tooltipData)
                    window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                    window.load()
                    return window
            return func(self, event)

        return wrapper

    return decorator


def formatRomanNumber(number):
    return int2roman(number) if IS_ROMAN_NUMBERS_ALLOWED else str(number)


def extractCollectionsRewards(completedCollectionQuests):
    eventsCache = dependency.instance(IEventsCache)
    for collectionQuest in completedCollectionQuests:
        collectionStrID = new_year.g_cache.collectionIDByCollectionRewards[collectionQuest]
        quest = eventsCache.getQuestByID(collectionQuest)
        if quest:
            yield {collectionStrID: quest.getBonuses()}
