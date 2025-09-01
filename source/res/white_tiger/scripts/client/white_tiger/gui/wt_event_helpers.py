# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_event_helpers.py
import logging
from helpers import dependency, time_utils
import BattleReplay
from gui import GUI_SETTINGS
from gui.impl.gen import R
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS, WT_TEAMS
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.simplified_quests_view_model import SimplifiedQuestsViewModel
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
    return WT_VEHICLE_TAGS.BOSS in tags


def getSpeed():
    return BattleReplay.g_replayCtrl.playbackSpeed if BattleReplay.isPlaying() else DEFAULT_SPEED


def getInfoPageURL():
    return GUI_SETTINGS.lookup('wtEventInfoPage')


def getIntroVideoURL():
    return GUI_SETTINGS.lookup('wtEventIntroVideo')


def isWTEventProgressionQuest(questId):
    return questId.startswith(PROGRESSION_QUEST_PREFIX)


def isWtEventSpecialQuest(questId):
    return questId.startswith(SPECIAL_QUEST_PREFIX)


def isWtEventBattleQuest(questId):
    return questId.startswith(BATTLE_QUEST_PREFIX)


def _getTooltipDataByEvent(event, tooltipItems):
    tooltipId = event.getArgument('tooltipId')
    if tooltipId is None:
        return
    else:
        tooltipData = tooltipItems.get(tooltipId)
        return None if tooltipData is None else tooltipData


@dependency.replace_none_kwargs(gameEventController=IWhiteTigerController)
def getSecondsLeft(gameEventController=None):
    season = gameEventController.getCurrentSeason()
    if not season:
        return 0
    currentCycleEnd = season.getCycleEndDate()
    return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))


def packWTBonus(preFormattedConditionTuple):
    model = SimplifiedQuestsViewModel()
    if preFormattedConditionTuple.iconKey:
        iconKey = preFormattedConditionTuple.iconKey
        model.setIcon(iconKey)
    if preFormattedConditionTuple.current:
        current = preFormattedConditionTuple.current
        model.setCurrentProgress(current)
    if preFormattedConditionTuple.earned:
        model.setLastProgressValue(max(preFormattedConditionTuple.earned, 0))
    if preFormattedConditionTuple.total:
        total = preFormattedConditionTuple.total
        model.setTotalProgress(total)
    return model
