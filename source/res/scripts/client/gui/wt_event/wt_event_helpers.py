# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_helpers.py
import logging
import BattleReplay
import CGF
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from gui.periodic_battles.models import AlertData, PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.decorators import ExecuteAfterCondition
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from constants import WT_TEAMS
from gui.shared.formatters import time_formatters
_logger = logging.getLogger(__name__)
DEFAULT_SPEED = 1.0
PROGRESSION_QUEST_PREFIX = 'wtevent:progression'
SPECIAL_QUEST_PREFIX = 'wtevent:battle_quest:event:special'
BATTLE_QUEST_PREFIX = 'wtevent:battle_quest:event'

def isBossTeam(team):
    return team == WT_TEAMS.BOSS_TEAM


def isBoss(tags):
    return VEHICLE_TAGS.EVENT_BOSS in tags


def getSpeed():
    return BattleReplay.g_replayCtrl.playbackSpeed if BattleReplay.isPlaying() else DEFAULT_SPEED


def getInfoPageURL():
    return GUI_SETTINGS.lookup('infoPageWhiteTiger')


def getIntroVideoURL():
    return GUI_SETTINGS.lookup('whiteTigerIntroVideoUrl')


@replace_none_kwargs(eventCtrl=IWhiteTigerController)
def getPortalCost(lootBoxType, eventCtrl=None):
    config = eventCtrl.getConfig()
    if lootBoxType == WhiteTigerLootBoxes.WT_HUNTER:
        return config.hunterPortalPrice
    if lootBoxType == WhiteTigerLootBoxes.WT_BOSS:
        return config.bossPortalPrice
    return config.tankPortalPrice if lootBoxType == WhiteTigerLootBoxes.WT_TANK else 0


@replace_none_kwargs(eventCtrl=IWhiteTigerController, itemsCache=IItemsCache)
def getMainVehicle(eventCtrl=None, itemsCache=None):
    mainVehicle = eventCtrl.getConfig().mainVehiclePrize
    return itemsCache.items.getItemByCD(mainVehicle)


@replace_none_kwargs(eventCtrl=IWhiteTigerController, itemsCache=IItemsCache)
def getBossMainVehicle(eventCtrl=None, itemsCache=None):
    bossMainVehicle = eventCtrl.getConfig().bossMainVehicle
    return itemsCache.items.getItemByCD(bossMainVehicle)


@replace_none_kwargs(eventCtrl=IWhiteTigerController, itemsCache=IItemsCache)
def getSpecialVehicles(eventCtrl=None, itemsCache=None):
    specialVehicles = eventCtrl.getConfig().specialVehicles
    items = []
    for vehicleDescr in specialVehicles:
        items.append(itemsCache.items.getItemByCD(vehicleDescr))

    return items


@dependency.replace_none_kwargs(gameEventCtrl=IWhiteTigerController, connectionMgr=IConnectionManager)
def getAlertStatusVO(gameEventCtrl=None, connectionMgr=None):
    status, _, _ = gameEventCtrl.getPrimeTimeStatus()
    isBattlesEnd = gameEventCtrl.isBattlesEnd()
    errorStr = backport.text(R.strings.event.serverAlertMessage(), serverName=connectionMgr.serverUserNameShort)
    if isBattlesEnd:
        errorStr = backport.text(R.strings.event.serverAlertMessage.battlesEnd())
    elif gameEventCtrl.hasAvailablePrimeTimeServers():
        errorStr = backport.text(R.strings.event.serverAlertMessage.unsuitablePeriphery())
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE and not isBattlesEnd
    shadowFilterVisible = status != PrimeTimeStatus.AVAILABLE
    return AlertData(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.event.serverAlertMessage.button()), buttonVisible=showPrimeTimeAlert and gameEventCtrl.hasAvailablePrimeTimeServers(), buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(errorStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=shadowFilterVisible, tooltip=TOOLTIPS_CONSTANTS.EVENT_BATTLES_END if isBattlesEnd else TOOLTIPS_CONSTANTS.EVENT_BATTLES_CALENDAR, isSimpleTooltip=False, isWulfTooltip=isBattlesEnd)


@dependency.replace_none_kwargs(gameEventController=IWhiteTigerController)
def getDaysLeftFormatted(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    if season is None:
        return ''
    else:
        currentCycleEnd = season.getCycleEndDate()
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))
        return backport.text(R.strings.event.status.timeLeft.lessHour()) if timeLeft < time_utils.ONE_HOUR else backport.getTillTimeStringByRClass(timeLeft, R.strings.event.status.timeLeft)


@dependency.replace_none_kwargs(gameEventController=IWhiteTigerController)
def getSecondsLeft(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    return 0 if not season else time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(season.getEndDate()))


def getFormattedTimeLeft(seconds):
    return time_formatters.getTillTimeByResource(seconds, R.strings.white_tiger.status.timeLeft, removeLeadingZeros=True)


def hasWTEventQuest(completedQuestIDs):
    for questId in completedQuestIDs:
        if isWTEventProgressionQuest(questId) or isWtEventSpecialQuest(questId):
            return True

    return False


def isWTEventProgressionQuest(questId):
    return questId.startswith(PROGRESSION_QUEST_PREFIX)


def isWtEventSpecialQuest(questId):
    return questId.startswith(SPECIAL_QUEST_PREFIX)


def isWtEventBattleQuest(questId):
    return questId.startswith(BATTLE_QUEST_PREFIX)


def findMainVehicle(vehicleBonuses, isVehicleObject=False):
    mainVehicle = getMainVehicle()
    return __findVehicle(mainVehicle, vehicleBonuses, isVehicleObject)


def findBossMainVehicle(vehicleBonuses, isVehicleObject=False):
    bossMainVehicle = getBossMainVehicle()
    return __findVehicle(bossMainVehicle, vehicleBonuses, isVehicleObject)


def findSpecialVehicle(vehicleBonuses, isVehicleObject=False):
    specialVehicles = getSpecialVehicles()
    for bonus in vehicleBonuses:
        for vehicle, _ in bonus.getVehicles():
            if any((x.intCD == vehicle.intCD for x in specialVehicles)) and not bonus.checkIsCompensatedVehicle(vehicle):
                if not isVehicleObject:
                    return bonus
                return vehicle

    return None


def isBossMainVehicleReceived(bonuses):
    vehicles = [ bonus for bonus in bonuses if bonus.getName() == 'vehicles' ]
    return findBossMainVehicle(vehicles) is not None if vehicles else False


def isSpecialVehicleReceived(bonuses):
    vehicles = [ bonus for bonus in bonuses if bonus.getName() == 'vehicles' ]
    return findSpecialVehicle(vehicles) is not None if vehicles else False


def __findVehicle(specialVehicle, vehicleBonuses, isVehicleObject):
    for bonus in vehicleBonuses:
        for vehicle, _ in bonus.getVehicles():
            if specialVehicle.intCD == vehicle.intCD and not bonus.checkIsCompensatedVehicle(vehicle):
                if not isVehicleObject:
                    return bonus
                return specialVehicle

    return None


class ExecuteAfterAllEventVehiclesLoaded(ExecuteAfterCondition):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    @property
    def condition(self):
        if not self.__hangarSpace.spaceInited:
            return False
        else:
            space = self.__hangarSpace.space
            if space is None:
                return False
            from EventVehicle import EventVehicle
            query = CGF.Query(space.getSpaceID(), EventVehicle)
            if query.empty():
                return False
            allVehicleLoaded = all([ vehicle.model is not None for vehicle in query.values() ])
            return allVehicleLoaded


g_execute_after_all_event_vehicles_loaded = ExecuteAfterAllEventVehiclesLoaded()

class ExecuteAfterAllEventVehiclesAndMainView(ExecuteAfterCondition):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    @property
    def condition(self):
        if not self.__hangarSpace.spaceInited:
            return False
        else:
            space = self.__hangarSpace.space
            if space is None:
                return False
            from EventVehicle import EventVehicle
            query = CGF.Query(space.getSpaceID(), EventVehicle)
            if query.empty():
                return False
            allVehicleLoaded = all([ vehicle.model is not None for vehicle in query.values() ])
            if self.__gameEventCtrl.isEventPrbActive() and self.__gameEventCtrl.isEnabled():
                isMainViewLoaded = self.__gameEventCtrl.mainViewLoaded
            else:
                isMainViewLoaded = True
            return allVehicleLoaded and isMainViewLoaded


g_execute_after_all_event_vehicles_and_main_view_loaded = ExecuteAfterAllEventVehiclesAndMainView()
