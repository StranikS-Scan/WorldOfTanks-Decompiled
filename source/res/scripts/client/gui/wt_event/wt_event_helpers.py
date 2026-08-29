# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_helpers.py
import logging
import BigWorld
from Queue import Queue
from functools import wraps
import BattleReplay
import CGF
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from gui.periodic_battles.models import AlertData, PrimeTimeStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles
from helpers import dependency, time_utils
from helpers.dependency import replace_none_kwargs
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared.utils import IHangarSpace
from white_tiger_common.wt_constants import WT_TEAMS
from gui.shared.formatters import time_formatters
from skeletons.gui.game_control import ILootBoxesController
_logger = logging.getLogger(__name__)
DEFAULT_SPEED = 1.0
PROGRESSION_QUEST_PREFIX = 'wtevent:progression'
SPECIAL_QUEST_PREFIX = 'wtevent:battle_quest:event:special'
BATTLE_QUEST_PREFIX = 'wtevent:battle_quest:event'

def isBossTeam(team):
    return team == WT_TEAMS.BOSS_TEAM


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


def getVehiclesFromAwards(awards):
    vehicles = [ bonus.getVehicles()[0][0] for bonus in awards if bonus.getName() == 'vehicles' ]
    return vehicles


def getReceivedVehiclesData(awards, boxType):
    res = []
    for bonus in awards:
        if bonus.getName() == 'vehicles':
            for vehicle, _ in bonus.getVehicles():
                customData = getVehicleCustomData(boxType, vehicle)
                if not bonus.checkIsCompensatedVehicle(vehicle) and customData:
                    if customData.get('video_show', '') != '':
                        res.append((vehicle, customData))

    return sorted(res, key=lambda x: x[1].get('priority', 1)) if res else []


@replace_none_kwargs(boxCtrl=ILootBoxesController)
def getVehicleCustomData(boxType, vehicle, boxCtrl=None):
    customData = boxCtrl.getVehiclesWithCustomData(boxType)
    for intCD, data in customData:
        if intCD == vehicle.intCD:
            return data

    return None


def __findVehicle(specialVehicle, vehicleBonuses, isVehicleObject):
    for bonus in vehicleBonuses:
        for vehicle, _ in bonus.getVehicles():
            if specialVehicle.intCD == vehicle.intCD and not bonus.checkIsCompensatedVehicle(vehicle):
                if not isVehicleObject:
                    return bonus
                return specialVehicle

    return None


class ExecuteAfterCondition(object):
    __slots__ = ('__queue', '__callbackID')

    def __init__(self):
        self.__queue = Queue()
        self.__callbackID = None
        return

    def __call__(self, func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            self._enqueueCall(func, *args, **kwargs)
            if self.__callbackID is None:
                self._checkCondition()
            return

        return wrapped

    @property
    def condition(self):
        raise NotImplementedError

    def _checkCondition(self):
        if not self.condition:
            self.__callbackID = BigWorld.callback(0.0, self._checkCondition)
            return
        else:
            self.__callbackID = None
            self._executeEnqueuedCalls()
            return

    def _enqueueCall(self, func, *args, **kwargs):
        self.__queue.put((func, args, kwargs))

    def _executeEnqueuedCalls(self):
        while not self.__queue.empty():
            f, args, kwargs = self.__queue.get()
            f(*args, **kwargs)


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
