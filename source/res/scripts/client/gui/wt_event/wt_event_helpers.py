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
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.periodic_battles.models import CalendarStatusVO
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.decorators import ExecuteAfterCondition
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from shared_utils import first
from constants import WT_TEAMS
_logger = logging.getLogger(__name__)
DEFAULT_SPEED = 1.0
PROGRESSION_QUEST_PREFIX = 'wtevent:progression'
EXCHANGE_QUEST_PREFIX = 'wtevent:exchange'
SPECIAL_QUEST_PREFIX = 'wtevent:battle_quest:event:special'
BATTLE_QUEST_PREFIX = 'wtevent:battle_quest:event'
_COMP_TOOLTIP = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()

def isBossTeam(team):
    return team == WT_TEAMS.BOSS_TEAM


def isBoss(tags):
    return VEHICLE_TAGS.EVENT_BOSS in tags


def getSpeed():
    return BattleReplay.g_replayCtrl.playbackSpeed if BattleReplay.isPlaying() else DEFAULT_SPEED


def getInfoPageURL():
    return GUI_SETTINGS.wtEvent.get('infoPage')


def getIntroVideoURL():
    return GUI_SETTINGS.wtEvent.get('introVideo')


def getPortalCost(lootBoxType):
    portalCosts = getEventSettings().portals.portalsCost
    if lootBoxType == EventLootBoxes.WT_HUNTER:
        return portalCosts['hunterPortal']
    return portalCosts['bossPortal'] if lootBoxType == EventLootBoxes.WT_BOSS else 0


@replace_none_kwargs(eventCtrl=IGameEventController, eventsCache=IEventsCache)
def getSpecialVehicle(eventCtrl=None, eventsCache=None):
    exchangeConfig = eventCtrl.getConfig().exchange
    exchangeQuest = eventsCache.getHiddenQuests().get(exchangeConfig['quest'])
    if exchangeQuest is None:
        _logger.debug('There is not exchange quest')
        return
    else:
        for bonus in exchangeQuest.getBonuses():
            if bonus.getName() == 'vehicles':
                return first(bonus.getVehicles())[0]

        _logger.debug('There is not bonus vehicle')
        return


@dependency.replace_none_kwargs(gameEventCtrl=IGameEventController, connectionMgr=IConnectionManager)
def getAlertStatusVO(gameEventCtrl=None, connectionMgr=None):
    status, _, _ = gameEventCtrl.getPrimeTimeStatus()
    errorStr = backport.text(R.strings.event.serverAlertMessage(), serverName=connectionMgr.serverUserNameShort)
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
    return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.event.serverAlertMessage.button()), buttonVisible=showPrimeTimeAlert and gameEventCtrl.hasAvailablePrimeTimeServers(), buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(errorStr), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.EVENT_BATTLES_CALENDAR, isSimpleTooltip=False)


@dependency.replace_none_kwargs(gameEventController=IGameEventController)
def getDaysLeftFormatted(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    if season is None:
        return ''
    else:
        currentCycleEnd = season.getCycleEndDate()
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))
        return backport.text(R.strings.event.status.timeLeft.lessHour()) if timeLeft < time_utils.ONE_HOUR else backport.getTillTimeStringByRClass(timeLeft, R.strings.event.status.timeLeft)


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
                    window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def hasWTEventQuest(completedQuestIDs):
    for questId in completedQuestIDs:
        if isWTEventProgressionQuest(questId) or isWtEventExchangeQuest(questId) or isWtEventSpecialQuest(questId):
            return True

    return False


def isWTEventProgressionQuest(questId):
    return questId.startswith(PROGRESSION_QUEST_PREFIX)


def isWtEventExchangeQuest(questId):
    return questId.startswith(EXCHANGE_QUEST_PREFIX)


def isWtEventSpecialQuest(questId):
    return questId.startswith(SPECIAL_QUEST_PREFIX)


def isWtEventBattleQuest(questId):
    return questId.startswith(BATTLE_QUEST_PREFIX)


def findSpecialVehicle(vehicleBonuses):
    specialVehicle = getSpecialVehicle()
    if specialVehicle is None:
        return
    else:
        for bonus in vehicleBonuses:
            for vehicle, _ in bonus.getVehicles():
                if vehicle.intCD == specialVehicle.intCD and not bonus.checkIsCompensatedVehicle(vehicle):
                    return bonus

        return


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
            isCameraMovementEnabled = space.getCameraManager().isCameraMovementEnabled()
            return allVehicleLoaded and isCameraMovementEnabled


g_execute_after_all_event_vehicles_loaded = ExecuteAfterAllEventVehiclesLoaded()

class ExecuteAfterAllEventVehiclesAndMainView(ExecuteAfterCondition):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __gameEventCtrl = dependency.descriptor(IGameEventController)

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
            isCameraMovementEnabled = space.getCameraManager().isCameraMovementEnabled()
            if self.__gameEventCtrl.isEventPrbActive() and self.__gameEventCtrl.isEnabled():
                isMainViewLoaded = self.__gameEventCtrl.mainViewLoaded
            else:
                isMainViewLoaded = True
            return allVehicleLoaded and isCameraMovementEnabled and isMainViewLoaded


g_execute_after_all_event_vehicles_and_main_view_loaded = ExecuteAfterAllEventVehiclesAndMainView()
