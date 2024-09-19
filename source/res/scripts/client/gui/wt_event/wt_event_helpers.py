# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_helpers.py
import logging
import BattleReplay
import CGF
from gui import GUI_SETTINGS
from gui.doc_loaders.event_settings_loader import getEventSettings
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tank_reward import EventTankType
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.periodic_battles.models import AlertData, PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.decorators import ExecuteAfterCondition
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from shared_utils import first
from constants import WT_TEAMS
_logger = logging.getLogger(__name__)
DEFAULT_SPEED = 1.0
PROGRESSION_QUEST_PREFIX = 'wtevent:progression'
SPECIAL_QUEST_PREFIX = 'wtevent:battle_quest:event:special'
BATTLE_QUEST_PREFIX = 'wtevent:battle_quest:event'
WT_TOKEN_PREFIX = 'wtevent:'
WT_RENTAL_TOKEN = WT_TOKEN_PREFIX + 'wte100drop'
WT_VEHICLE_TOKEN = WT_TOKEN_PREFIX + 'got_lb_vehicle_stop'
_COMP_TOOLTIP = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()

def isBossTeam(team):
    return team == WT_TEAMS.BOSS_TEAM


def isBoss(tags):
    return VEHICLE_TAGS.EVENT_BOSS in tags


def getSpeed():
    return BattleReplay.g_replayCtrl.playbackSpeed if BattleReplay.isPlaying() else DEFAULT_SPEED


def getInfoPageURL():
    return GUI_SETTINGS.wtEventInfoPage


def getIntroVideoURL():
    return GUI_SETTINGS.wtEventIntroVideo


def getPortalCost(lootBoxType):
    portalCosts = getEventSettings().portals.portalsCost
    if lootBoxType == EventLootBoxes.WT_HUNTER:
        return portalCosts['hunterPortal']
    return portalCosts['bossPortal'] if lootBoxType == EventLootBoxes.WT_BOSS else 0


def getEventTankType(value):
    for evenType in EventTankType:
        if evenType.value == value:
            return evenType

    return EventTankType.PRIMARY


@replace_none_kwargs(eventCtrl=IEventBattlesController, itemsCache=IItemsCache)
def getSpecialVehicles(eventCtrl=None, itemsCache=None):
    specialVehicles = eventCtrl.getConfig().specialVehicles
    items = []
    for vehicleDescr in specialVehicles:
        items.append(itemsCache.items.getItemByCD(vehicleDescr))

    return items


@dependency.replace_none_kwargs(gameEventCtrl=IEventBattlesController, connectionMgr=IConnectionManager)
def getAlertStatusVO(gameEventCtrl=None, connectionMgr=None):
    status, _, _ = gameEventCtrl.getPrimeTimeStatus()
    errorStr = backport.text(R.strings.event.serverAlertMessage(), serverName=connectionMgr.serverUserNameShort)
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
    return AlertData(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.event.serverAlertMessage.button()), buttonVisible=showPrimeTimeAlert and gameEventCtrl.hasAvailablePrimeTimeServers(), buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(errorStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.EVENT_BATTLES_CALENDAR, isSimpleTooltip=False)


@dependency.replace_none_kwargs(gameEventController=IEventBattlesController)
def getDaysLeftFormatted(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    if season is None:
        return ''
    else:
        currentCycleEnd = season.getCycleEndDate()
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))
        return backport.text(R.strings.event.status.timeLeft.lessHour()) if timeLeft < time_utils.ONE_HOUR else backport.getTillTimeStringByRClass(timeLeft, R.strings.event.status.timeLeft)


@dependency.replace_none_kwargs(gameEventController=IEventBattlesController)
def getSecondsLeft(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    if not season:
        return 0
    currentCycleEnd = season.getCycleEndDate()
    return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))


def backportTooltipDecorator(tooltipItemsName='_tooltipItems'):

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = _getTooltipDataByEvent(event, getattr(self, tooltipItemsName, {}))
                if tooltipData is None:
                    return
                if tooltipData.specialAlias == TOOLTIPS_CONSTANTS.EVENT_LOOTBOX:
                    lootboxType = first(tooltipData.specialArgs)
                    window = DecoratedTooltipWindow(WtEventLootBoxTooltipView(isHunterLootBox=lootboxType == EventLootBoxes.WT_HUNTER), parent=self.getParentWindow(), useDecorator=False)
                    window.move(event.mouse.positionX, event.mouse.positionY)
                elif tooltipData.specialAlias == TOOLTIPS_CONSTANTS.EVENT_VEHICLE_COMPENSATION:
                    window = DecoratedTooltipWindow(VehicleCompensationTooltipContent(_COMP_TOOLTIP, viewModelClazz=LootBoxVehicleCompensationTooltipModel, **tooltipData.specialArgs))
                    window.move(event.mouse.positionX, event.mouse.positionY)
                else:
                    window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


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


def findSpecialVehicle(vehicleBonuses, isVehicleObject=False):
    specialVehicles = getSpecialVehicles()
    for bonus in vehicleBonuses:
        for vehicle, _ in bonus.getVehicles():
            if any((x.intCD == vehicle.intCD for x in specialVehicles)) and not bonus.checkIsCompensatedVehicle(vehicle):
                if not isVehicleObject:
                    return bonus
                return vehicle

    return None


def isSpecialVehicleReceived(bonuses):
    vehicles = [ bonus for bonus in bonuses if bonus.getName() == 'vehicles' ]
    return findSpecialVehicle(vehicles) is not None if vehicles else False


def _getTooltipDataByEvent(event, tooltipItems):
    tooltipId = event.getArgument('tooltipId')
    if tooltipId is None:
        return
    else:
        tooltipData = tooltipItems.get(tooltipId)
        return None if tooltipData is None else tooltipData


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
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

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
