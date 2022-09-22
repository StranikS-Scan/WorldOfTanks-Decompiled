# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/ranked.py
import typing
from gui.battle_results.br_constants import BattleResultsRecord
from gui.battle_results.components.ranked import RankedChangesInfoHelper
from gui.battle_results.reusable import sort_keys
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.events.event_types import EventTypes
from gui.impl.gen.view_models.views.lobby.postbattle.events.ranked.event_model import EventModel
from gui.impl.gen.view_models.views.lobby.postbattle.events.ranked.result_state import ResultState
from gui.impl.gen.view_models.views.lobby.postbattle.events.ranked.stage_state import StageState
from gui.ranked_battles.ranked_models import RankChangeStates
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel
_RESULT_STATES_MAPPING = {RANKEDBATTLES_ALIASES.SUBTASK_STATE_LEAGUE: ResultState.LEAGUE,
 RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION: ResultState.DIVISION,
 RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK: ResultState.RANK,
 RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK_LOST: ResultState.RANK_LOST,
 RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE: ResultState.STAGE}
_STAGE_STATES_MAPPING = {RankChangeStates.BONUS_STEPS_EARNED: StageState.STAGES_BONUS,
 RankChangeStates.STEPS_EARNED: StageState.STAGES,
 RankChangeStates.BONUS_STEP_EARNED: StageState.STAGE_BONUS,
 RankChangeStates.STEP_EARNED: StageState.STAGE,
 RankChangeStates.STEP_LOST: StageState.STAGE_LOST,
 RankChangeStates.NOTHING_CHANGED: StageState.STAGE_IDLE,
 RankChangeStates.RANK_UNBURN_PROTECTED: StageState.STAGE_IDLE}

def getRankedEvents(tooltipData, reusable, result):
    if not reusable.common.arenaVisitor.gui.isRankedBattle():
        return ()
    model = EventModel()
    helper = RankedChangesInfoHelper(reusable)
    resultState = _RESULT_STATES_MAPPING[helper.makeSubTaskState()]
    allies, _ = reusable.getBiDirectionTeamsIterator(result[BattleResultsRecord.VEHICLES], sort_keys.VehicleXpSortKey)
    title, separatedTitle, description, descriptionIcon = helper.makeTitleAndDescription(allies)
    model.setType(EventTypes.RANKED_BATTLES)
    model.setTitle(R.strings.postbattle_screen.eventTitle.ranked())
    model.setState(resultState)
    model.setStateTitle(title)
    model.setSeparatedStateTitle(separatedTitle)
    model.setDescription(description)
    model.setDescriptionIcon(descriptionIcon or R.invalid())
    _fillRankedInfo(model, resultState, helper.getRankChangeStatus(), reusable.personal.getRankInfo())
    return (model,)


@dependency.replace_none_kwargs(rankedController=IRankedBattlesController)
def _fillRankedInfo(model, state, rankChangeStatus, rankedInfo, rankedController=None):
    if state == ResultState.LEAGUE:
        pass
    elif state == ResultState.DIVISION:
        model.setDivisionID(rankedController.getDivision(rankedInfo.accRank + 1).getID())
    elif state == ResultState.RANK_LOST:
        model.setRankID(rankedInfo.prevAccRank)
        model.setDivisionID(rankedController.getDivision(rankedInfo.prevAccRank).getID())
    elif state == ResultState.RANK:
        model.setRankID(rankedInfo.accRank)
        model.setDivisionID(rankedController.getDivision(rankedInfo.accRank).getID())
        if rankedInfo.shieldHP is not None:
            model.setShieldHP(rankedInfo.shieldHP)
        if rankedController.getRank(rankedInfo.accRank).isVisualUnburnable():
            model.setIsUnburnable(True)
    else:
        model.setStageState(_STAGE_STATES_MAPPING[rankChangeStatus])
    model.setStepsBonusBattles(rankedInfo.qualificationBonusBattles)
    model.setEfficiencyBonusBattles(rankedInfo.additionalBonusBattles)
    return
