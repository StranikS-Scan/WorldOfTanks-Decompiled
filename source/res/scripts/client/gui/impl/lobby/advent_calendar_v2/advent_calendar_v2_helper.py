# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_helper.py
import BigWorld
import logging
import re
from collections import namedtuple
from itertools import chain
from BWUtil import AsyncReturn
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_progression_reward_item_view_model import RewardType
from gui.server_events.bonuses import TmanTemplateTokensBonus, NYCoinTokenBonus, LootBoxTokensBonus
from gui.shared.advent_calendar_v2_consts import ADVENT_CALENDAR_QUEST_POSTFIX, ADVENT_CALENDAR_TOKEN, ADVENT_CALENDAR_QUEST_PREFIX, ADVENT_CALENDAR_PROGRESSION_QUEST, ADVENT_PRESETS_WITH_DISABLED_ANIMATION
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, int2roman
from items.components.ny_constants import ToyTypes
from new_year.ny_constants import RESOURCES_ORDER, GuestsQuestsTokens
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.gui.game_control import IAdventCalendarV2Controller
from skeletons.new_year import INewYearController
from wg_async import wg_async, wg_await
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_DAY_PATTERN = '{}(\\d+){}'.format(ADVENT_CALENDAR_QUEST_PREFIX, ADVENT_CALENDAR_QUEST_POSTFIX)
_VEHICLES_TIER_THRESHOLD = 8
LootBoxInfo = namedtuple('LootBoxInfo', ('id', 'name', 'category', 'bonuses'))
NyResourceInfo = namedtuple('NyResource', ('resourceName', 'resourceValue'))

@dependency.replace_none_kwargs(controller=IAdventCalendarV2Controller)
def getProgressionQuestMayComplete(tokens=1, controller=None):
    userTokens = getAccountTokensAmount(ADVENT_CALENDAR_TOKEN)
    for quest in controller.progressionRewardQuestsOrdered:
        required = getQuestNeededTokensCount(quest)
        if required == userTokens + tokens:
            return quest

    return None


def getQuestNeededTokensCount(quest):
    if quest is not None:
        tokens = quest.accountReqs.getTokens()
        if tokens:
            return tokens[-1].getNeededCount()
    return 0


@wg_async
def showAdventCalendarRewardWindow(dayId=1, isProgressionReward=False, data=None, parent=None, currencyName=''):
    from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_reward_view import AdventCalendarRewardView
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    wrapper = FullScreenDialogWindowWrapper(AdventCalendarRewardView(data, dayId, isProgressionReward, currencyName=currencyName), parent, doBlur=False, layer=WindowLayer.FULLSCREEN_WINDOW)
    yield wg_await(dialogs.showSimple(wrapper))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getAccountTokensAmount(token, itemsCache=None):
    return itemsCache.items.tokens.getTokenCount(token)


@wg_async
@dependency.replace_none_kwargs(controller=IAdventCalendarV2Controller)
def openAndWaitAdventCalendarDoor(dayID, currencyName='', callback=None, controller=None):
    doorOpenStatus = yield wg_await(controller.awaitDoorOpenQuestCompletion(dayID=dayID, currencyName=currencyName))
    if not doorOpenStatus:
        pushOpenDoorFailedError()
    if callback:
        callback(result=doorOpenStatus)


def pushOpenDoorFailedError():
    SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.adventCalendar.server_error()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isHighTierBonusVehicle(bonus, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(bonus.getValue().keys()[0])
    return vehicle.level >= _VEHICLES_TIER_THRESHOLD if vehicle else None


def extractCustomizationBonus(bonus):
    value = bonus.getValue()
    if isinstance(value, list):
        value = value[0]
    return bonus.getC11nItem(value)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def extractItemBonus(bonus, itemsCache=None):
    item = itemsCache.items.getItemByCD(bonus.getValue().keys()[0])
    return item.userName if item else ''


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def extractVehicleBonus(bonus, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(bonus.getValue().keys()[0])
    return '{vehName} ({vehLevel})'.format(vehName=vehicle.userName, vehLevel=int2roman(vehicle.level)) if vehicle else ''


_BONUS_TYPE_VALUE_EXTRACTOR = {'items': extractItemBonus,
 'highTierVehicles': extractVehicleBonus,
 'lowTierVehicles': extractVehicleBonus}

def processProbabilityBonuses(probabilityGroups):
    processedBonuses = {}
    for probabilityGroup in probabilityGroups:
        bonusItems = {}
        for bonus in probabilityGroup.bonuses:
            bonusType = bonus.getName()
            if bonusType == 'currencies':
                bonusType = bonus.getCode()
            elif bonusType == 'vehicles':
                bonusType = 'highTierVehicles' if isHighTierBonusVehicle(bonus) else 'lowTierVehicles'
            elif bonusType == 'customizations':
                value = extractCustomizationBonus(bonus)
                if value:
                    bonusType = value.itemTypeName
                    if bonusType == 'style':
                        bonusType += '_3d' if value.is3D else '_2d'
                    bonusItems.setdefault(bonusType, set()).add(value.userName)
                    continue
            elif bonusType == 'battleToken':
                value = bonus.getValue()
                if GuestsQuestsTokens.TOKEN_CAT in value:
                    bonusItems.setdefault('guest_cat', set()).add(str(value[GuestsQuestsTokens.TOKEN_CAT]['count']))
                    continue
            elif bonusType == 'randomNy24Toy':
                toyId = bonus.getContext().get('toyId')
                if toyId is not None and NewYearCurrentToyInfo(toyId).getToyType() == ToyTypes.COLOR_FIR:
                    bonusType = ToyTypes.COLOR_FIR
            bonusItems.setdefault(bonusType, set()).add(_BONUS_TYPE_VALUE_EXTRACTOR.get(bonusType, lambda b: str(b.getValue()))(bonus))

        processedBonuses.setdefault(probabilityGroup.name, {}).setdefault(probabilityGroup.probability, {}).update(bonusItems)

    return processedBonuses


def getProgressionRewardType(quest):
    bonus = quest.getBonuses()[0]
    if isinstance(bonus, NYCoinTokenBonus):
        return RewardType.GIFT_MACHINE_TOKEN
    if isinstance(bonus, TmanTemplateTokensBonus):
        return RewardType.CREW_MEMBER
    if isinstance(bonus, LootBoxTokensBonus):
        return RewardType.BIG_LOOTBOX
    _logger.error('Unknown Reward Type for quest %s', quest.getID())


def getProgressionRewardQuestBonus(quest):
    for bonus in quest.getBonuses():
        for value in bonus.getValue():
            return value


def getFlattenedBonuses(quests):
    return chain.from_iterable([ q.getBonuses() for q in quests ])


@wg_async
def showAdventCalendarPurchaseDialogWindow(dayId=1, price=0, parent=None):
    from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_purchase_dialog_view import AdventCalendarPurchaseDialogView
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    wrapper = FullScreenDialogWindowWrapper(AdventCalendarPurchaseDialogView(dayId, price), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW, doBlur=False)
    result = yield wg_await(dialogs.show(wrapper))
    result = None if result.result == DialogButtons.CANCEL else result.data
    raise AsyncReturn(result)
    return


def isAdventCalendarV2Quest(questID):
    return questID.startswith(ADVENT_CALENDAR_QUEST_PREFIX) and questID.endswith(ADVENT_CALENDAR_QUEST_POSTFIX)


def isAdventCalendarV2ProgressionQuest(questID):
    return questID.startswith(ADVENT_CALENDAR_PROGRESSION_QUEST)


def getDayIdFromQuest(questID):
    match = re.search(_DAY_PATTERN, questID)
    return match.group(1) if match is not None else None


@dependency.replace_none_kwargs(controller=INewYearController)
def getMaxResource(controller=None):
    defaultRessource = RESOURCES_ORDER[0]
    maxResource = NyResourceInfo(resourceName=defaultRessource, resourceValue=controller.currencies.getResouceBalance(defaultRessource.value))
    for r in RESOURCES_ORDER:
        currenResourceValue = controller.currencies.getResouceBalance(r.value)
        if currenResourceValue > maxResource.resourceValue:
            maxResource = NyResourceInfo(resourceName=r, resourceValue=currenResourceValue)

    return maxResource


def getMaxResourceCount():
    return getMaxResource().resourceValue


def isAdventAnimationEnabled():
    return BigWorld.detectGraphicsPresetFromSystemSettings() not in ADVENT_PRESETS_WITH_DISABLED_ANIMATION
