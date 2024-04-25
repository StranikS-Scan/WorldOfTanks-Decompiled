# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ranked_battles_widget.py
import logging
import SoundGroups
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ENABLE_RANKED_ANIMATIONS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RankedBattlesHangarWidgetMeta import RankedBattlesHangarWidgetMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.ranked_battles.constants import ZERO_DIVISION_ID
from gui.ranked_battles.ranked_builders.widget_vos import StateBlock, WidgetPreferences, getQualAddVOs, getVOsSequence, getLeagueAdditionalVOs
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from gui.shared.event_dispatcher import showRankedProgressionWindow
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
_logger = logging.getLogger(__name__)

class _RankedWidgetSoundManager(object):

    class CALLER(object):
        HANGAR = 'hangar'
        POST_BATTLE = 'post_battle'

    def __init__(self):
        self.__sound = None
        self.__isHangarBlocked = False
        g_playerEvents.onBattleResultsReceived += self.switchHangarLock
        return

    def switchHangarLock(self, *args, **kwargs):
        self.__isHangarBlocked = kwargs.get('isLocked', True)

    def playInstantSound(self, eventName, caller):
        if not self.__callerBlocked(caller):
            SoundGroups.g_instance.playSound2D(eventName)

    def __callerBlocked(self, caller):
        return self.__isHangarBlocked and caller == self.CALLER.HANGAR


class RankedBattleResultsWidget(RankedBattlesHangarWidgetMeta):
    rankedController = dependency.descriptor(IRankedBattlesController)
    _soundMgr = _RankedWidgetSoundManager()
    __slots__ = ('_soundCallerType',)

    def __init__(self):
        super(RankedBattleResultsWidget, self).__init__()
        self._maxRank = None
        self._clientMaxRank = None
        self._soundCallerType = self._soundMgr.CALLER.POST_BATTLE
        return

    def update(self, lastRank=None, clientMaxRank=None, currentRank=None, ranksChain=None):
        self._update(lastRank, clientMaxRank, currentRank, ranksChain)

    def _update(self, lastRankID=None, clientMaxRankID=None, currentRankID=None, ranksChain=None):
        lastRankID = self.rankedController.getClientRank()[0] if lastRankID is None else lastRankID
        clientMaxRankID = self.rankedController.getClientMaxRank()[0] if clientMaxRankID is None else clientMaxRankID
        currentRankID = self.rankedController.getCurrentRank()[0] if currentRankID is None else currentRankID
        ranksChain = ranksChain if ranksChain is not None else self.rankedController.getRanksChain(min(lastRankID, currentRankID), max(lastRankID, currentRankID) + 1)
        preferences = WidgetPreferences(self._isAnimationEnabled(), self._isHuge(), self._hasAdditionalRankInfo())
        statesSequence = self._buildStatesSequence(lastRankID, currentRankID, clientMaxRankID, ranksChain)
        statesSequence = self.__extendWithQualificationStatesSequence(statesSequence)
        statesSequence = self.__extendWithLeagueStatesSequence(statesSequence)
        vosSequence = getVOsSequence(preferences, statesSequence, ranksChain)
        self.rankedController.updateClientValues()
        if vosSequence:
            self.as_setDataS(vosSequence)
        return

    def onAnimationFinished(self):
        pass

    def onSoundTrigger(self, triggerName):
        self._soundMgr.playInstantSound(triggerName, self._soundCallerType)

    def onWidgetClick(self):
        pass

    def _dispose(self):
        self._soundMgr.switchHangarLock(isLocked=False)
        super(RankedBattleResultsWidget, self)._dispose()

    def _buildStatesSequence(self, lastRankID, currentRankID, maxRankID, ranks):
        states = []
        lastRank = ranks[lastRankID]
        currentRank = ranks[currentRankID]
        if maxRankID < lastRankID:
            _logger.error('Last rank can not be more then max rank')
        if currentRank.isNewForPlayer():
            if lastRank.isAcquired():
                for rankID, nextRankID in zip(range(lastRankID, currentRankID), range(lastRankID + 1, currentRankID + 1)):
                    rank = ranks[rankID]
                    nextRank = ranks[nextRankID]
                    if rank.isInitialForNextDivision() or nextRank.isInitialForNextDivision():
                        if rank.isInitialForNextDivision():
                            if rankID < maxRankID:
                                states.append(StateBlock(RANKEDBATTLES_ALIASES.FIRST_RANK_REACHIVE_STATE, rankID, nextRankID, None))
                            else:
                                states.append(StateBlock(RANKEDBATTLES_ALIASES.FIRST_RANK_RECEIVE_STATE, rankID, nextRankID, None))
                        if nextRank.isInitialForNextDivision() and not nextRank.isQualification():
                            states.append(StateBlock(RANKEDBATTLES_ALIASES.DIVISION_RECEIVE_STATE, rankID, nextRankID, None))
                    if rankID < maxRankID:
                        states.append(StateBlock(RANKEDBATTLES_ALIASES.RANK_REACHIVE_STATE, rankID, nextRankID, None))
                    states.append(StateBlock(RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE, rankID, nextRankID, None))

                if lastRank.isInitial() and lastRank.isQualification():
                    states[0] = StateBlock(RANKEDBATTLES_ALIASES.QUAL_DIVISION_FINISHED_STATE, lastRankID, lastRankID + 1, None)
                if currentRank.isFinal():
                    states[-1] = StateBlock(RANKEDBATTLES_ALIASES.LEAGUE_RECEIVE_STATE, currentRankID - 1, currentRankID, None)
            if lastRank.isLost():
                for rankID, prevRankID in zip(reversed(range(currentRankID + 1, lastRankID + 1)), reversed(range(currentRankID, lastRankID))):
                    if ranks[prevRankID].isInitialForNextDivision():
                        states.append(StateBlock(RANKEDBATTLES_ALIASES.FIRST_RANK_LOST_STATE, rankID, prevRankID, None))
                    states.append(StateBlock(RANKEDBATTLES_ALIASES.RANK_LOST_STATE, rankID, prevRankID, None))

            return states
        else:
            shieldStatus = currentRank.getShieldStatus()
            if shieldStatus is not None:
                prevShieldHP, shiedHP, maxHP, shieldState, _ = shieldStatus
                if shieldState == RANKEDBATTLES_ALIASES.SHIELD_ENABLED:
                    if shiedHP < maxHP:
                        state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_NOT_FULL
                    else:
                        state = RANKEDBATTLES_ALIASES.RANK_IDLE_STATE
                elif shieldState == RANKEDBATTLES_ALIASES.SHIELD_RENEW:
                    state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_RENEW
                elif shieldState == RANKEDBATTLES_ALIASES.SHIELD_FULL_RENEW:
                    state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_FULL_RENEW
                elif shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
                    if prevShieldHP == maxHP:
                        state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE_FROM_FULL
                    else:
                        state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE
                elif shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP:
                    if prevShieldHP == maxHP:
                        state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE_STEP_FROM_FULL
                    else:
                        state = RANKEDBATTLES_ALIASES.ANIM_SHIELD_LOSE_STEP
                else:
                    state = RANKEDBATTLES_ALIASES.RANK_IDLE_STATE
            else:
                state = RANKEDBATTLES_ALIASES.RANK_IDLE_STATE
            if state == RANKEDBATTLES_ALIASES.RANK_IDLE_STATE:
                if currentRank.isInitialForNextDivision():
                    state = RANKEDBATTLES_ALIASES.RANK_INIT_STATE
                if currentRank.isInitial() and currentRank.isQualification():
                    state = RANKEDBATTLES_ALIASES.QUAL_IDLE_STATE
                if state == RANKEDBATTLES_ALIASES.RANK_IDLE_STATE and currentRank.isFinal():
                    state = RANKEDBATTLES_ALIASES.LEAGUE_UPDATE_STATE
            states = [StateBlock(state, currentRankID, currentRankID, None)]
            return states

    def __extendWithQualificationStatesSequence(self, statesSequence):
        if not statesSequence:
            _logger.error('There can not be empty statesSequence')
            return statesSequence
        firstBlock = statesSequence[0]
        if firstBlock.state in (RANKEDBATTLES_ALIASES.QUAL_IDLE_STATE, RANKEDBATTLES_ALIASES.QUAL_DIVISION_FINISHED_STATE):
            battlesInQualification = self.rankedController.getStatsComposer().divisionsStats.get(ZERO_DIVISION_ID, {}).get('battles', 0)
            totalQualificationBattles = self.rankedController.getTotalQualificationBattles()
            statesSequence[0] = StateBlock(firstBlock.state, firstBlock.lastID, firstBlock.currentID, getQualAddVOs(battlesInQualification, totalQualificationBattles))
        return statesSequence

    def __extendWithLeagueStatesSequence(self, statesSequence):
        if not statesSequence:
            _logger.error('There can not be empty statesSequence')
            return statesSequence
        lastBlock = statesSequence[-1]
        if lastBlock.state in (RANKEDBATTLES_ALIASES.LEAGUE_RECEIVE_STATE, RANKEDBATTLES_ALIASES.LEAGUE_UPDATE_STATE):
            statesSequence.pop()
            statsComposer = self.rankedController.getStatsComposer()
            prevEfficiency = self.rankedController.getClientEfficiency()
            currEfficiency = statsComposer.currentSeasonEfficiency.efficiency
            prevEfficiencyDiff = self.rankedController.getClientEfficiencyDiff()
            currEfficiencyDiff = statsComposer.currentSeasonEfficiencyDiff
            prevWebSeasonInfo = self.rankedController.getClientSeasonInfo()
            currWebSeasonInfo = self.rankedController.getWebSeasonProvider().seasonInfo
            if currWebSeasonInfo.league == UNDEFINED_LEAGUE_ID:
                currWebSeasonInfo = prevWebSeasonInfo
            additionalVOs = getLeagueAdditionalVOs(currEfficiency, currEfficiencyDiff, currWebSeasonInfo.position)
            prevLeagueID = prevWebSeasonInfo.league
            prevPosition = prevWebSeasonInfo.position
            currLeagueID = currWebSeasonInfo.league
            if lastBlock.state == RANKEDBATTLES_ALIASES.LEAGUE_RECEIVE_STATE:
                statesSequence.append(StateBlock(RANKEDBATTLES_ALIASES.LEAGUE_RECEIVE_STATE, lastBlock.lastID, currLeagueID, additionalVOs))
            else:
                state = RANKEDBATTLES_ALIASES.LEAGUE_IDLE_STATE
                if prevLeagueID != currLeagueID:
                    state = RANKEDBATTLES_ALIASES.LEAGUE_INCREASE_STATE
                    if prevLeagueID != UNDEFINED_LEAGUE_ID and prevLeagueID < currLeagueID:
                        state = RANKEDBATTLES_ALIASES.LEAGUE_DECREASE_STATE
                    additionalVOs = getLeagueAdditionalVOs(currEfficiency, currEfficiencyDiff, currWebSeasonInfo.position, prevEfficiency, prevEfficiencyDiff, prevPosition)
                statesSequence.append(StateBlock(state, prevLeagueID, currLeagueID, additionalVOs))
        return statesSequence

    @classmethod
    def _isAnimationEnabled(cls):
        return bool(AccountSettings.getSettings(ENABLE_RANKED_ANIMATIONS))

    @classmethod
    def _isHuge(cls):
        return True

    @classmethod
    def _hasAdditionalRankInfo(cls):
        return False


class RankedBattlesHangarWidget(RankedBattleResultsWidget):

    def __init__(self):
        super(RankedBattlesHangarWidget, self).__init__()
        self._soundCallerType = self._soundMgr.CALLER.HANGAR

    def onWidgetClick(self):
        showRankedProgressionWindow()

    def onAnimationFinished(self):
        if self.rankedController.getClientBonusBattlesCount() > 0:
            self.as_setBonusBattlesLabelS(str(self.rankedController.getStatsComposer().bonusBattlesCount))
        else:
            self.as_setBonusBattlesLabelS('')

    def _populate(self):
        super(RankedBattlesHangarWidget, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.rankedController.getWebSeasonProvider().onInfoUpdated += self._update
        self._update()

    def _update(self, lastRank=None, clientMaxRank=None, currentRank=None, ranksChain=None):
        if self.rankedController.getClientBonusBattlesCount() > 0:
            self.as_setBonusBattlesLabelS(str(self.rankedController.getClientBonusBattlesCount()))
        else:
            self.as_setBonusBattlesLabelS('')
        super(RankedBattlesHangarWidget, self)._update(lastRank, currentRank, ranksChain)

    def _dispose(self):
        self.rankedController.getWebSeasonProvider().onInfoUpdated -= self._update
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RankedBattlesHangarWidget, self)._dispose()

    @classmethod
    def _isAnimationEnabled(cls):
        return True

    @classmethod
    def _isHuge(cls):
        return False

    @classmethod
    def _hasAdditionalRankInfo(cls):
        return True

    def __dossierUpdateCallBack(self, *args):
        self._update()
