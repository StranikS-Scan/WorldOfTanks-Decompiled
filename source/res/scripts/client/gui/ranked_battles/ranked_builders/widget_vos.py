# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/widget_vos.py
from collections import namedtuple
import logging
import typing
from gui.impl.gen import R
from gui.impl import backport
from gui.ranked_battles.ranked_helpers import getBonusMultiplierLabel
from gui.ranked_battles.ranked_builders import shared_vos
from gui.ranked_battles.ranked_models import Rank
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.formatters import text_styles
from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)
QualAddVOs = namedtuple('QualAddVOs', 'currentBattles, totalBattles')
LeagueAddVOs = namedtuple('LeagueAddVOs', 'currentEfficiencyVO, currentRatingVO, lastEfficiencyVO, lastRatingVO')
StateBlock = namedtuple('StateBlock', 'state, lastID, currentID, additionalVOs')
WidgetPreferences = namedtuple('WidgetPreferences', 'isAnimationEnabled, isHuge, hasAdditionalRankInfo')

class StepsStatesCollector(object):
    __slots__ = ()

    def getStates(self, rank):
        result = []
        if rank is not None:
            progress = rank.getProgress()
            if progress is not None:
                for step in progress.getSteps():
                    baseState = self.__getBaseState(rank, step)
                    specializedState = self._getSpecializedState(baseState)
                    result.append(_getBonusBattleState(specializedState) if step.isBonus() else specializedState)

        return result

    def _getSpecializedState(self, state):
        return state

    @staticmethod
    def __getBaseState(rank, step):
        if step.isAcquired():
            stepState = RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE
            if step.isNewForPlayer():
                stepState = RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE
                if rank.isNewForPlayer():
                    stepState = RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE
        elif step.isLost() and step.isNewForPlayer():
            stepState = RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE
        else:
            stepState = RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE
        return stepState


class CustomStepsStatesCollector(StepsStatesCollector):
    __slots__ = ('_resultState',)

    def __init__(self, resultState):
        super(CustomStepsStatesCollector, self).__init__()
        self._resultState = resultState

    def _getSpecializedState(self, state):
        return self._resultState


class AcquiredStepsStatesCollector(CustomStepsStatesCollector):

    def _getSpecializedState(self, state):
        if state in (RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE, RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE):
            state = self._resultState
        return state


class LostStepsStatesCollector(CustomStepsStatesCollector):

    def _getSpecializedState(self, state):
        if state == RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE:
            state = self._resultState
        return state


class _SequencePart(CONST_CONTAINER):
    NOT_IN_CHAIN = 0
    CHAIN_HEAD = 1
    CHAIN_MIDDLE = 2
    CHAIN_TAIL = 3


_NEUTRAL_SEQUENCE_STEPS = {_SequencePart.NOT_IN_CHAIN: StepsStatesCollector(),
 _SequencePart.CHAIN_HEAD: StepsStatesCollector(),
 _SequencePart.CHAIN_MIDDLE: StepsStatesCollector(),
 _SequencePart.CHAIN_TAIL: StepsStatesCollector()}
_INCREASE_SEQUENCE_STEPS = {_SequencePart.NOT_IN_CHAIN: StepsStatesCollector(),
 _SequencePart.CHAIN_HEAD: StepsStatesCollector(),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_RECEIVED_POSITIVE_STATE),
 _SequencePart.CHAIN_TAIL: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_RECEIVED_POSITIVE_STATE)}
_INCREASE_SEQUENCE_NEW_STEPS = {_SequencePart.NOT_IN_CHAIN: AcquiredStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE),
 _SequencePart.CHAIN_HEAD: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE),
 _SequencePart.CHAIN_TAIL: AcquiredStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE)}
_DECREASE_SEQUENCE_STEPS = {_SequencePart.NOT_IN_CHAIN: LostStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_JUST_LOST_SHORT_STATE),
 _SequencePart.CHAIN_HEAD: LostStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_JUST_LOST_SHORT_STATE),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE),
 _SequencePart.CHAIN_TAIL: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE)}
_DECREASE_SEQUENCE_NEW_STEPS = {_SequencePart.NOT_IN_CHAIN: LostStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_LOST_BLINK_STATE),
 _SequencePart.CHAIN_HEAD: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_LOST_BLINK_STATE),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_LOST_BLINK_STATE),
 _SequencePart.CHAIN_TAIL: LostStepsStatesCollector(RANKEDBATTLES_ALIASES.STEP_LOST_BLINK_STATE)}
_BONUS_STEPS = {RANKEDBATTLES_ALIASES.STEP_RECEIVED_POSITIVE_STATE: RANKEDBATTLES_ALIASES.STEP_RECEIVED_BONUS_STATE,
 RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE: RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_BONUS_STATE,
 RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE: RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_BONUS_STATE,
 RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE: RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_BONUS_STATE}

def getVOsSequence(preferences, stateBlocks, ranks):
    result = []
    sequenceStates = [_SequencePart.NOT_IN_CHAIN]
    if len(stateBlocks) > 1:
        sequenceStates = [ _SequencePart.CHAIN_MIDDLE for _ in stateBlocks ]
        sequenceStates[0] = _SequencePart.CHAIN_HEAD
        sequenceStates[-1] = _SequencePart.CHAIN_TAIL
    for index, block in enumerate(stateBlocks):
        builder = _BLOCKS_VOS_BUILDERS.get(block.state)
        if builder is not None:
            result.append(builder(preferences, block, sequenceStates[index], ranks))
        _logger.error('Can not find builder for state = %s', block.state)

    return result


def getQualAddVOs(battlesInQualification, totalQualificationBattles):
    return QualAddVOs(battlesInQualification, totalQualificationBattles)


def getLeagueAdditionalVOs(currentEfficiency, currentEfficiencyDiff, currentRating, lastEfficiency=None, lastEfficiencyDiff=None, lastRating=None):
    currentEfficiencyVO = shared_vos.getEfficiencyVO(currentEfficiency, currentEfficiencyDiff)
    currentRatingVO = shared_vos.getRatingVO(currentRating)
    lastEfficiencyVO = shared_vos.getEfficiencyVO(lastEfficiency, lastEfficiencyDiff)
    lastRatingVO = shared_vos.getRatingVO(lastRating)
    return LeagueAddVOs(currentEfficiencyVO, currentRatingVO, lastEfficiencyVO, lastRatingVO)


def _buildInitRankVO(preferences, stateBlock, sequenceState, ranks):
    nextRank = ranks[stateBlock.currentID + 1]
    stepsOverrider = _NEUTRAL_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(nextRank, preferences, stepsOverrider)
    rankRightVO = _getRankVO(nextRank, preferences)
    return _getBlockVO(preferences, stateBlock.state, rankRightVO=rankRightVO, steps=steps, finalState=_getFinalState(preferences, stateBlock.state, rankRightVO=_getRankVO(nextRank, preferences), steps=_getStepsVO(nextRank, preferences, stepsOverrider)))


def _buildDecreaseRankVO(preferences, stateBlock, sequenceState, ranks):
    lastRank = ranks[stateBlock.lastID]
    currentRank = ranks[stateBlock.currentID]
    nextRank = ranks[stateBlock.lastID + 1]
    stepsOverrider = _DECREASE_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(nextRank, preferences, stepsOverrider)
    newStepsOverrider = _DECREASE_SEQUENCE_NEW_STEPS[sequenceState]
    newSteps = _getStepsVO(lastRank, preferences, newStepsOverrider)
    if stateBlock.state == RANKEDBATTLES_ALIASES.FIRST_RANK_LOST_STATE:
        currentRank = None
    rankLeftVO = _getRankVO(lastRank, preferences, True)
    rankRightVO = _getRankVO(nextRank, preferences)
    newRankVO = _getRankVO(currentRank, preferences, True)
    return _getBlockVO(preferences, stateBlock.state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, finalState=_getFinalState(preferences, stateBlock.state, rankLeftVO=_getRankVO(currentRank, preferences, True), rankRightVO=_getRankVO(lastRank, preferences), steps=_getStepsVO(lastRank, preferences, newStepsOverrider)))


def _buildIncreaseRankVO(preferences, stateBlock, sequenceState, ranks):
    lastRank = ranks[stateBlock.lastID]
    currentRank = ranks[stateBlock.currentID]
    nextRank = ranks[stateBlock.currentID + 1]
    stepsOverrider = _INCREASE_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(currentRank, preferences, stepsOverrider)
    newStepsOverrider = _INCREASE_SEQUENCE_NEW_STEPS[sequenceState]
    newSteps = _getStepsVO(nextRank, preferences, newStepsOverrider)
    infoText, nextInfoText = _getInfoTexts(stateBlock)
    lastRank = None if lastRank.isInitialForNextDivision() else lastRank
    rankLeftVO = _getRankVO(lastRank, preferences, True)
    rankRightVO = _getRankVO(currentRank, preferences)
    newRankVO = _getRankVO(nextRank, preferences)
    return _getBlockVO(preferences, stateBlock.state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, infoText=infoText, nextInfoText=nextInfoText, finalState=_getFinalState(preferences, stateBlock.state, rankLeftVO=_getRankVO(currentRank, preferences, True), rankRightVO=_getRankVO(nextRank, preferences), steps=_getStepsVO(nextRank, preferences, newStepsOverrider)))


def _buildSameRankVO(preferences, stateBlock, sequenceState, ranks):
    currentRank = ranks[stateBlock.currentID]
    nextRank = ranks[stateBlock.currentID + 1]
    stepsOverrider = _NEUTRAL_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(nextRank, preferences, stepsOverrider)
    rankLeftVO = _getRankVO(currentRank, preferences, True)
    rankRightVO = _getRankVO(nextRank, preferences)
    isShieldOneRankState = stateBlock.state in RANKEDBATTLES_ALIASES.ANIM_SHIELD_ONE_RANK_STATES
    return _getBlockVO(preferences, stateBlock.state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps, finalState=_getFinalState(preferences, stateBlock.state, rankLeftVO=_getRankVO(currentRank, preferences, True), rankRightVO=None if isShieldOneRankState else _getRankVO(nextRank, preferences), steps=None if isShieldOneRankState else _getStepsVO(nextRank, preferences, stepsOverrider)))


def _buildDivisionRecieveVO(preferences, stateBlock, sequenceState, ranks):
    lastRank = ranks[stateBlock.lastID]
    currentRank = ranks[stateBlock.currentID]
    nextRank = ranks[stateBlock.currentID + 1]
    stepsOverrider = _INCREASE_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(currentRank, preferences, stepsOverrider)
    newStepsOverrider = _INCREASE_SEQUENCE_NEW_STEPS[sequenceState]
    newSteps = _getStepsVO(nextRank, preferences, newStepsOverrider)
    rankLeftVO = _getRankVO(lastRank, preferences, True)
    rankRightVO = _getRankVO(currentRank, preferences)
    newRankVO = _getRankVO(nextRank, preferences)
    divisionVO = _getDivisionVO(currentRank.getDivision().getID(), nextRank.getDivision().getID())
    return _getBlockVO(preferences, stateBlock.state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, divisionVO=divisionVO)


def _buildQualificationIdleVO(preferences, stateBlock, sequenceState, ranks):
    nextRank = ranks[stateBlock.currentID + 1]
    infoText, nextInfoText = _getInfoTexts(stateBlock)
    rankRightVO = _getQualificationVO(nextRank)
    return _getBlockVO(preferences, stateBlock.state, rankRightVO=rankRightVO, infoText=infoText, nextInfoText=nextInfoText)


def _buildQualificationRecieveVO(preferences, stateBlock, sequenceState, ranks):
    currentRank = ranks[stateBlock.currentID]
    nextRank = ranks[stateBlock.currentID + 1]
    newStepsOverrider = _INCREASE_SEQUENCE_NEW_STEPS[sequenceState]
    newSteps = _getStepsVO(nextRank, preferences, newStepsOverrider)
    infoText, nextInfoText = _getInfoTexts(stateBlock)
    rankRightVO = _getQualificationVO(currentRank)
    newRankVO = _getRankVO(nextRank, preferences)
    divisionVO = _getDivisionVO(currentRank.getDivision().getID(), nextRank.getDivision().getID())
    return _getBlockVO(preferences, stateBlock.state, rankRightVO=rankRightVO, newRankVO=newRankVO, infoText=infoText, nextInfoText=nextInfoText, newSteps=newSteps, divisionVO=divisionVO)


def _buildLeagueRecieveVO(preferences, stateBlock, sequenceState, ranks):
    lastRank = ranks[stateBlock.lastID]
    currentRank = ranks[stateBlock.lastID + 1]
    stepsOverrider = _INCREASE_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(currentRank, preferences, stepsOverrider)
    rankLeftVO = _getRankVO(lastRank, preferences, True)
    rankRightVO = _getRankVO(currentRank, preferences)
    leagueVO = _getLeagueVO(stateBlock.currentID, stateBlock.additionalVOs.currentEfficiencyVO, stateBlock.additionalVOs.currentRatingVO, backport.text(R.strings.ranked_battles.rankedBattlesWidget.leaguesAchievment.title()), backport.text(R.strings.ranked_battles.rankedBattlesWidget.leaguesAchievment.info()))
    return _getBlockVO(preferences, stateBlock.state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps, leagueVO=leagueVO)


def _buildLeagueUpdateVO(preferences, stateBlock, sequenceState, ranks):
    leagueVO = _getLeagueVO(stateBlock.currentID, stateBlock.additionalVOs.currentEfficiencyVO, stateBlock.additionalVOs.currentRatingVO)
    newLeagueVO = None
    if stateBlock.state != RANKEDBATTLES_ALIASES.LEAGUE_IDLE_STATE:
        leagueVO = _getLeagueVO(stateBlock.lastID, stateBlock.additionalVOs.lastEfficiencyVO, stateBlock.additionalVOs.lastRatingVO)
        title = ''
        infoText = ''
        newLeagueName = backport.text(R.strings.ranked_battles.rankedBattlesWidget.dyn('league{}'.format(stateBlock.currentID))())
        if stateBlock.state == RANKEDBATTLES_ALIASES.LEAGUE_INCREASE_STATE:
            title = backport.text(R.strings.ranked_battles.rankedBattlesWidget.leagueIncrease.title())
            infoText = backport.text(R.strings.ranked_battles.rankedBattlesWidget.leagueIncrease.info(), leagueName=newLeagueName)
        if stateBlock.state == RANKEDBATTLES_ALIASES.LEAGUE_DECREASE_STATE:
            title = backport.text(R.strings.ranked_battles.rankedBattlesWidget.leagueDecrease.title())
            infoText = backport.text(R.strings.ranked_battles.rankedBattlesWidget.leagueDecrease.info(), leagueName=newLeagueName)
        newLeagueVO = _getLeagueVO(stateBlock.currentID, stateBlock.additionalVOs.currentEfficiencyVO, stateBlock.additionalVOs.currentRatingVO, title, infoText)
    return _getBlockVO(preferences, stateBlock.state, leagueVO=leagueVO, newLeagueVO=newLeagueVO)


_BLOCKS_VOS_BUILDERS = {RANKEDBATTLES_ALIASES.RANK_IDLE_STATE: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.RANK_INIT_STATE: _buildInitRankVO,
 RANKEDBATTLES_ALIASES.RANK_LOST_STATE: _buildDecreaseRankVO,
 RANKEDBATTLES_ALIASES.FIRST_RANK_LOST_STATE: _buildDecreaseRankVO,
 RANKEDBATTLES_ALIASES.FIRST_RANK_RECEIVE_STATE: _buildIncreaseRankVO,
 RANKEDBATTLES_ALIASES.FIRST_RANK_REACHIVE_STATE: _buildIncreaseRankVO,
 RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE: _buildIncreaseRankVO,
 RANKEDBATTLES_ALIASES.RANK_REACHIVE_STATE: _buildIncreaseRankVO,
 RANKEDBATTLES_ALIASES.QUAL_IDLE_STATE: _buildQualificationIdleVO,
 RANKEDBATTLES_ALIASES.QUAL_DIVISION_FINISHED_STATE: _buildQualificationRecieveVO,
 RANKEDBATTLES_ALIASES.DIVISION_RECEIVE_STATE: _buildDivisionRecieveVO,
 RANKEDBATTLES_ALIASES.LEAGUE_RECEIVE_STATE: _buildLeagueRecieveVO,
 RANKEDBATTLES_ALIASES.LEAGUE_INCREASE_STATE: _buildLeagueUpdateVO,
 RANKEDBATTLES_ALIASES.LEAGUE_DECREASE_STATE: _buildLeagueUpdateVO,
 RANKEDBATTLES_ALIASES.LEAGUE_IDLE_STATE: _buildLeagueUpdateVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_NOT_FULL: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_RENEW: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_FULL_RENEW: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE_FROM_FULL: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE_STEP_FROM_FULL: _buildSameRankVO,
 RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE_STEP: _buildSameRankVO}

def _getStepsVO(rank, preferences, statesCollector=StepsStatesCollector()):
    infoText = ''
    if rank is not None:
        progress = rank.getProgress()
        if progress and preferences.isHuge and progress.getBonusSteps():
            infoText = _getBonusStepsLabel()
    return {'steps': statesCollector.getStates(rank),
     'infoText': infoText}


def _getRankVO(rank, preferences, isEnabled=False):
    return shared_vos.buildRankVO(rank=rank, isEnabled=isEnabled, imageSize=RANKEDBATTLES_ALIASES.WIDGET_HUGE if preferences.isHuge else RANKEDBATTLES_ALIASES.WIDGET_MEDIUM, hasTooltip=preferences.hasAdditionalRankInfo, shieldStatus=rank.getShieldStatus(), shieldAnimated=True, showUnburnable=True) if rank is not None else None


def _getQualificationVO(rank):
    return {'imageSrc': backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_80x110.c_0()),
     'smallImageSrc': backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_58x80.c_0()),
     'isEnabled': True,
     'rankID': str(rank.getID()),
     'hasTooltip': False,
     'shield': None}


def _getDivisionVO(divisionID, newDivisionID):
    return {'division': divisionID,
     'newDivision': newDivisionID,
     'title': backport.text(R.strings.ranked_battles.rankedBattlesWidget.newDivisionCongrat.title()),
     'infoText': backport.text(R.strings.ranked_battles.rankedBattlesWidget.newDivisionCongrat.info())}


def _getLeagueVO(leagueID, efficiencyVO, positionVO, title='', infoText=''):
    return {'league': leagueID,
     'efficiency': efficiencyVO,
     'position': positionVO,
     'title': title,
     'infoText': infoText}


def _getBlockVO(preferences, state, infoText='', nextInfoText='', rankLeftVO=None, rankRightVO=None, newRankVO=None, steps=None, newSteps=None, leagueVO=None, newLeagueVO=None, divisionVO=None, finalState=None):
    return {'state': state,
     'rankLeftVO': rankLeftVO,
     'rankRightVO': rankRightVO,
     'newRankVO': newRankVO,
     'stepsContainerVO': steps or {'steps': (),
                          'infoText': ''},
     'newStepsContainerVO': newSteps or {'steps': (),
                             'infoText': ''},
     'infoText': infoText,
     'nextInfoText': nextInfoText,
     'divisionVO': divisionVO,
     'leagueVO': leagueVO,
     'newLeagueVO': newLeagueVO,
     'isHuge': preferences.isHuge,
     'animationEnabled': preferences.isAnimationEnabled,
     'finalState': finalState}


def _getFinalState(preferences, state, rankLeftVO=None, rankRightVO=None, steps=None):
    if preferences.isAnimationEnabled:
        return
    else:
        if rankLeftVO is not None:
            rankLeftVO = _updateShield(rankLeftVO)
        if rankRightVO is not None:
            rankRightVO = _updateShield(rankRightVO)
        steps = _updateSteps(steps)
        return _getBlockVO(preferences, state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps)


def _getBonusBattleState(state):
    return _BONUS_STEPS.get(state, state)


def _getBonusStepsLabel():
    label = getBonusMultiplierLabel()
    if label:
        label = text_styles.concatStylesToMultiLine(text_styles.heroTitleYellow(label), text_styles.middleTitle(backport.text(R.strings.ranked_battles.rankedBattlesWidget.bonusSteps())))
    return label


def _getInfoTexts(stateBlock):
    infoText = ''
    newInfoText = ''
    if stateBlock.state in (RANKEDBATTLES_ALIASES.QUAL_IDLE_STATE, RANKEDBATTLES_ALIASES.QUAL_DIVISION_FINISHED_STATE):
        infoText = text_styles.highlightText(backport.text(R.strings.ranked_battles.rankedBattlesWidget.qualificationIdleText(), currentBattles=text_styles.highlightText(stateBlock.additionalVOs.currentBattles), totalBattles=text_styles.mainBig(stateBlock.additionalVOs.totalBattles)))
    if stateBlock.state in (RANKEDBATTLES_ALIASES.FIRST_RANK_RECEIVE_STATE, RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE):
        newInfoText = text_styles.hightlight(backport.text(R.strings.ranked_battles.rankedBattlesWidget.newRankCongrat()))
    return (infoText, newInfoText)


def _updateShield(rankVO):
    shield = rankVO.get('shield', None)
    if shield is not None:
        if shield['newState'] is not None:
            shield['state'] = shield['newState']
            shield['newState'] = None
            rankVO['shield'] = shield
    return rankVO


def _updateSteps(stepsVO):
    resultVO = []
    infoText = ''
    if stepsVO is not None:
        for step in stepsVO.get('steps'):
            if step in RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATES:
                resultVO.append(RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE)
            resultVO.append(RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE)

        infoText = stepsVO.get('infoText', '')
    return {'steps': resultVO,
     'infoText': infoText}
