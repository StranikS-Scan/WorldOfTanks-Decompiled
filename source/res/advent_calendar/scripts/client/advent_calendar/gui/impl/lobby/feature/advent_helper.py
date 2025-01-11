# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/advent_helper.py
import logging
from collections import namedtuple
from itertools import chain
from typing import Optional
import BigWorld
from account_helpers import AccountSettings
from account_helpers.AccountSettings import AdventCalendar
from advent_calendar.gui.feature.constants import ADVENT_PRESETS_WITH_DISABLED_ANIMATION
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorState
from advent_calendar.gui.impl.gen.view_models.views.lobby.progression_reward_item_view_model import RewardType
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from advent_calendar_common.advent_calendar_constants import DoorMarkType
from constants import SECONDS_IN_DAY
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import TmanTemplateTokensBonus, LootBoxTokensBonus, CustomizationsBonus
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from new_year.ny_constants import RESOURCES_ORDER
from shared_utils import findFirst, first
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from wg_async import wg_async, wg_await
_logger = logging.getLogger(__name__)
LootBoxInfo = namedtuple('LootBoxInfo', ('id', 'name', 'category', 'bonuses'))
NyResourceInfo = namedtuple('NyResource', ('resourceName', 'resourceValue'))

def getQuestNeededTokensCount(quest):
    if quest is not None:
        tokens = quest.accountReqs.getTokens()
        if tokens:
            return tokens[-1].getNeededCount()
    return 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getAccountTokensAmount(token, itemsCache=None):
    return itemsCache.items.tokens.getTokenCount(token)


@wg_async
@dependency.replace_none_kwargs(controller=IAdventCalendarController)
def openAndWaitDoor(dayID, currency='', callback=None, controller=None):
    doorOpenStatus = yield wg_await(controller.awaitDoorOpenQuestCompletion(dayID, currency=currency))
    if not doorOpenStatus:
        pushOpenDoorFailedError()
    if callback:
        callback(result=doorOpenStatus)


def pushOpenDoorFailedError():
    SystemMessages.pushMessage(text=backport.text(R.strings.advent_calendar.server_error()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.HIGH)


def getProgressionRewardType(bonus):
    if isinstance(bonus, CustomizationsBonus):
        return RewardType.STYLE_2D
    if isinstance(bonus, TmanTemplateTokensBonus):
        return RewardType.CREW_MEMBER
    if isinstance(bonus, LootBoxTokensBonus):
        return RewardType.BIG_LOOTBOX
    _logger.error('Unknown Reward Type for bonus %s', bonus)


def getFlattenedBonuses(quests):
    return chain.from_iterable([ q.getBonuses() for q in quests ])


@dependency.replace_none_kwargs(adventController=IAdventCalendarController)
def getDoorState(dayID, firstClosedDayID=None, adventController=None):
    if adventController.isInPostActivePhase():
        if firstClosedDayID is None:
            firstClosedDayID = getFirstClosedDayID(adventController=adventController)
        if firstClosedDayID == dayID:
            return DoorState.READY_TO_OPEN
        if adventController.isDoorOpened(dayID):
            return DoorState.OPENED
        return DoorState.EXPIRED
    currentDayNumber = adventController.getCurrentDayNumber()
    if adventController.isDoorOpened(dayID):
        return DoorState.OPENED
    elif dayID > currentDayNumber:
        return DoorState.CLOSED
    else:
        return DoorState.EXPIRED if dayID < currentDayNumber - 1 else DoorState.READY_TO_OPEN


@dependency.replace_none_kwargs(adventController=IAdventCalendarController)
def getFirstClosedDayID(adventController=None):
    return findFirst(lambda dayID: not adventController.isDoorOpened(dayID), range(1, adventController.config.doorsCount + 1))


@dependency.replace_none_kwargs(adventController=IAdventCalendarController)
def getHolidayOpsStartTime(adventController=None):
    doorsConfig = adventController.config.doors
    door = findFirst(lambda d: d.get('mark', DoorMarkType.NONE) == DoorMarkType.NY_START, doorsConfig)
    doorIdx = doorsConfig.index(door) if door is not None else 0
    return adventController.config.startDate + SECONDS_IN_DAY * doorIdx


def isAdventAnimationEnabled():
    return BigWorld.detectGraphicsPresetFromSystemSettings() not in ADVENT_PRESETS_WITH_DISABLED_ANIMATION


def getAdventCalendarSetting(settingName):
    return AccountSettings.getSettings(AdventCalendar.SETTINGS).get(settingName)


def setAdventCalendarSetting(settingName, settingValue):
    settings = AccountSettings.getSettings(AdventCalendar.SETTINGS)
    settings.update({settingName: settingValue})
    AccountSettings.setSettings(AdventCalendar.SETTINGS, settings)


@dependency.replace_none_kwargs(controller=INewYearController)
def getMaxResource(controller=None):
    defaultResource = first(RESOURCES_ORDER)
    maxResource = NyResourceInfo(resourceName=defaultResource, resourceValue=controller.currencies.getResouceBalance(defaultResource.value))
    for r in RESOURCES_ORDER:
        currenResourceValue = controller.currencies.getResouceBalance(r.value)
        if currenResourceValue > maxResource.resourceValue:
            maxResource = NyResourceInfo(resourceName=r, resourceValue=currenResourceValue)

    return maxResource
