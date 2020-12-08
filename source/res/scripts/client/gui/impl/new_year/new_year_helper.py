# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_helper.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_EXTRA_SLOT_LAST_LEVEL_SHOWN, NY_TALISMAN_GIFT_LAST_SHOWN_STAGE
from constants import SECONDS_IN_DAY, LOOTBOX_TOKEN_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.tooltips.ny_discount_reward_tooltip import NyDiscountRewardTooltip
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils, getLanguageCode, int2roman
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.ny_constants import CurrentNYConstants, VEH_BRANCH_EXTRA_SLOT_TOKEN
from skeletons.new_year import INewYearController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from gui.shared.gui_items.loot_box import NewYearLootBoxes
_ARABIC_NUMBERS_LANGUAGE_CODES = ('ko', 'no')
IS_ROMAN_NUMBERS_ALLOWED = getLanguageCode() not in _ARABIC_NUMBERS_LANGUAGE_CODES
BONUS_ICONS = {'xpFactor': R.images.gui.maps.icons.new_year.vehicles_view.icons.icon_battle_exp_main(),
 'freeXPFactor': R.images.gui.maps.icons.new_year.vehicles_view.icons.icon_free_exp_main_screen(),
 'tankmenXPFactor': R.images.gui.maps.icons.new_year.vehicles_view.icons.icon_crew_exp_main()}
_BONUSES_ORDER = ({'bonusName': 'tmanToken'},
 {'bonusName': CurrentNYConstants.FILLERS},
 {'bonusName': 'battleToken',
  'tagStartsWith': LOOTBOX_TOKEN_PREFIX},
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
 {'bonusName': CurrentNYConstants.TOY_FRAGMENTS},
 {'bonusName': 'crewBooks'})
_BONUSES_ORDER_CACHE = {}

@dependency.replace_none_kwargs(nyController=INewYearController)
def fillBonusFormula(formulaViewModel, nyController=None):
    with formulaViewModel.transaction() as tx:
        tx.setCreditsBonus(nyController.getActiveSettingBonusValue())
        tx.setMultiplier(nyController.getActiveMultiplier())
        tx.setMegaBonus(nyController.getActiveMegaToysBonus())
        tx.setCollectionBonus(nyController.getActiveCollectionsBonus())


def nyBonusSortOrder(preformattedBonus):
    bonusName, tags = preformattedBonus.bonusName, preformattedBonus.postProcessTags
    if isinstance(tags, tuple):
        tags = '' if not tags else tags[0]
    primaryKey = (bonusName, tags)
    if primaryKey in _BONUSES_ORDER_CACHE:
        return _BONUSES_ORDER_CACHE[primaryKey]
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

    _BONUSES_ORDER_CACHE[primaryKey] = result
    return result


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


def nyCreateToolTipContentDecorator(func):

    def wrapper(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyDiscountRewardTooltip():
            variadicID, discount = event.getArgument('variadicID'), event.getArgument('discount')
            return NyDiscountRewardTooltip(variadicID, discount)
        if contentID == R.views.lobby.new_year.tooltips.ny_tank_extra_slot_tooltip.NYTankExtraSlotTooltipContent():
            from gui.impl.new_year.tooltips.ny_tank_extra_slot_tooltip import NYTankExtraSlotTooltipContent
            return NYTankExtraSlotTooltipContent()
        return func(self, event, contentID)

    return wrapper


def backportTooltipDecorator(tooltipItemsName='_tooltips'):

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = _getTooltipDataByEvent(event, getattr(self, tooltipItemsName, {}))
                if tooltipData is None:
                    return
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def _getTooltipDataByEvent(event, tooltipItems):
    tooltipId = event.getArgument('tooltipId')
    return None if tooltipId is None else tooltipItems.get(tooltipId, None)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasNewExtraSlotLevel(itemsCache=None):
    if not itemsCache.items.tokens.isTokenAvailable(VEH_BRANCH_EXTRA_SLOT_TOKEN):
        return False
    maxLevel = itemsCache.items.festivity.getMaxLevel()
    return AccountSettings.getUIFlag(NY_EXTRA_SLOT_LAST_LEVEL_SHOWN) < maxLevel


def setLastObservedGiftStage(stage):
    return AccountSettings.setUIFlag(NY_TALISMAN_GIFT_LAST_SHOWN_STAGE, stage)


def getLastObservedGiftStage():
    return AccountSettings.getUIFlag(NY_TALISMAN_GIFT_LAST_SHOWN_STAGE)


def getTalismanGiftCooldown(nextGameTime=None):
    if nextGameTime is None:
        nextGameTime = getNextGameTime()
    return max(nextGameTime - time_utils.getCurrentTimestamp(), 0)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getNextGameTime(lobbyContext=None):
    gameDayStartingTime = lobbyContext.getServerSettings().regionals.getGameDayStartingTime()
    currentTime = time_utils.getCurrentTimestamp()
    newGameDayStartTime = (int((currentTime - gameDayStartingTime) // SECONDS_IN_DAY) + 1) * SECONDS_IN_DAY
    return newGameDayStartTime + gameDayStartingTime


class TalismanGiftNotifier(PeriodicNotifier):

    def __init__(self, updateFunc):
        super(TalismanGiftNotifier, self).__init__(deltaFunc=self.__getNextDelta, updateFunc=self.__update, periods=(time_utils.ONE_MINUTE,))
        self.__updateFunc = updateFunc
        self.__nextGameTime = 0

    def startNotification(self):
        self.__nextGameTime = getNextGameTime()
        self.__invokeUpdateFunc()
        super(TalismanGiftNotifier, self).startNotification()

    def __update(self):
        self.__invokeUpdateFunc()

    def __invokeUpdateFunc(self):
        if self.__updateFunc is not None:
            self.__updateFunc(self.__getTalismanGiftCooldown())
        return

    def __getTalismanGiftCooldown(self):
        return getTalismanGiftCooldown(self.__nextGameTime) if self.__nextGameTime else 0

    def __getNextDelta(self):
        return self.__getTalismanGiftCooldown()


def formatRomanNumber(number):
    return int2roman(number) if IS_ROMAN_NUMBERS_ALLOWED else str(number)
