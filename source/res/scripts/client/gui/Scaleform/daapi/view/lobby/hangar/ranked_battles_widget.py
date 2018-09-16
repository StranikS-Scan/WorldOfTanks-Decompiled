# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ranked_battles_widget.py
import SoundGroups
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ENABLE_RANKED_ANIMATIONS
from gui.Scaleform.daapi.view.meta.RankedBattlesWidgetMeta import RankedBattlesWidgetMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.ranked_battles.awards_formatters import getRankedQuestsOrderedAwards
from gui.ranked_battles.constants import SOUND, RANK_TYPES
from gui.ranked_battles.ranked_helpers import buildRankVO
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showRankedAwardWindow
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRankedBattlesController

class _RankedWidgetSoundManager(object):
    _RANK_CHANGED_SOUNDS = (SOUND.RANK_LOST,
     SOUND.RANK_1_EARNED,
     SOUND.RANK_2_EARNED,
     SOUND.RANK_3_EARNED,
     SOUND.RANK_4_EARNED,
     SOUND.RANK_5_EARNED,
     SOUND.VEH_RANK_EARNED,
     SOUND.RANK_EARNED_POST_BATTLE,
     SOUND.RANK_LOST_POST_BATTLE)
    _STEP_CHANGED_SOUNDS = (SOUND.STEP_EARNED,
     SOUND.STEP_LOST,
     SOUND.STEP_EARNED_POST_BATTLE,
     SOUND.STEP_LOST_POST_BATTLE)
    _STEP_CHANGED_EVENTS = (RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE, RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE, RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE)

    class CALLER(object):
        HANGAR = 'hangar'
        POST_BATTLE = 'post_battle'

    def __init__(self):
        self.__sound = None
        self.__isHangarBlocked = False
        g_playerEvents.onBattleResultsReceived += self.switchHangarLock
        self.__initBlockingSounds()
        return

    def switchHangarLock(self, *args, **kwargs):
        self.__isHangarBlocked = kwargs.get('isLocked', True)

    def play(self):
        if self.__sound:
            SoundGroups.g_instance.playSound2D(self.__sound)
        self.__sound = None
        return

    def playInstantSound(self, eventName, caller):
        if not self.__callerBlocked(caller):
            SoundGroups.g_instance.playSound2D(eventName)

    def __initBlockingSounds(self):
        self.__blockingSounds = {k:self._STEP_CHANGED_EVENTS for k in self._RANK_CHANGED_SOUNDS}
        stepUnchangedStates = (RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE,)
        self.__blockingSounds.update({k:stepUnchangedStates for k in self._STEP_CHANGED_SOUNDS})

    def __callerBlocked(self, caller):
        return self.__isHangarBlocked and caller == self.CALLER.HANGAR

    def __eventShouldBeIgnored(self, eventType):
        return eventType in self.__blockingSounds.get(self.__sound, [])


class RankedBattlesWidget(RankedBattlesWidgetMeta):
    rankedController = dependency.descriptor(IRankedBattlesController)
    _soundMgr = _RankedWidgetSoundManager()

    def __init__(self):
        super(RankedBattlesWidget, self).__init__()
        self._currentRank = None
        self._soundCallerType = self._soundMgr.CALLER.HANGAR
        return

    def update(self, ranks, currentRank, lastRank):
        self._currentRank = currentRank
        result = self._buildData(ranks, currentRank, lastRank)
        self.as_setDataS(result)

    def onSoundTrigger(self, triggerName):
        self._soundMgr.playInstantSound(triggerName, self._soundCallerType)

    def onWidgetClick(self):
        self.fireEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_VIEW_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        if self._currentRank is not None:
            completedQuests = []
            receivedRanks = 0
            rankID = self._currentRank.getID()
            vehicle = g_currentVehicle.item
            while rankID > 0:
                rank = self.rankedController.getRank(rankID, vehicle=vehicle)
                haveNotClaimedAward = not rank.isRewardClaimed()
                if haveNotClaimedAward:
                    rankQuest = rank.getQuest()
                    if rankQuest is not None:
                        completedQuests.append(rankQuest)
                    rankID -= 1
                    receivedRanks += 1
                break

            if completedQuests:
                self.rankedController.runQuests(completedQuests)
            if receivedRanks > 0:
                showRankedAwardWindow(self._currentRank.getID(), awards=getRankedQuestsOrderedAwards(completedQuests, size=AWARDS_SIZES.BIG))
        return

    def onAnimationFinished(self):
        self.rankedController.setLastRank(g_currentVehicle.item)
        self.rankedController.setLastShields()

    def _checkClaim(self):
        return True

    def _isHuge(self):
        return False

    def _isAutoPlay(self):
        return True

    def _hasAdditionalRankInfo(self):
        return True

    def _getFirstRankReceiveStateData(self, currentRank):
        state = RANKEDBATTLES_ALIASES.FIRST_RANK_RECEIVE_STATE
        steps = self._buildProgress(currentRank)
        infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_INITTEXT, battles=str(len(steps))))
        nextInfoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NEWRANKCONGRAT))
        rankLeftVO = self._buildRankVO(currentRank, True)
        return self._buildVO(state, infoText=infoText, rankLeftVO=rankLeftVO, steps=steps, nextInfoText=nextInfoText, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(currentRank, True), steps=self._buildProgress(currentRank)))

    def _getFirstRankReachiveStateData(self, currentRank, nextRank, newStepsState=None, changeAcquired=False):
        state = RANKEDBATTLES_ALIASES.FIRST_RANK_REACHIVE_STATE
        steps = self._buildProgress(currentRank)
        infoText = ''
        if not self._isHuge():
            infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_INITTEXT, battles=str(len(steps))))
        nextInfoText = ''
        rankRightVO = self._buildRankVO(currentRank, True)
        newRankVO = self._buildRankVO(nextRank)
        newSteps = self._buildProgress(nextRank, newStepsState=newStepsState, changeAcquired=changeAcquired)
        return self._buildVO(state, infoText=infoText, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, nextInfoText=nextInfoText, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(currentRank, True), rankRightVO=self._buildRankVO(nextRank), steps=self._buildProgress(nextRank, newStepsState=newStepsState, changeAcquired=changeAcquired)))

    def _getRankReceiveForFirstTimeData(self, lastRank, currentRank):
        state = RANKEDBATTLES_ALIASES.RANK_RECEIVE_FOR_FIRST_TIME_STATE
        infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NEWRANKCONGRAT))
        steps = self._buildProgress(currentRank)
        rankLeftVO = self._buildRankVO(lastRank, True)
        rankRightVO = self._buildRankVO(currentRank)
        return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, infoText=infoText, steps=steps, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(lastRank, True), rankRightVO=self._buildRankVO(currentRank), steps=self._buildProgress(currentRank)))

    def _getReachievedReceiveStateData(self, lastRank, currentRank, nextRank, stepsState=None, newStepsState=None, changeAcquired=False):
        state = RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE
        steps = self._buildProgress(currentRank, newStepsState=stepsState)
        rankLeftVO = self._buildRankVO(lastRank, True)
        rankRightVO = self._buildRankVO(currentRank)
        newSteps = self._buildProgress(nextRank, newStepsState=newStepsState, changeAcquired=changeAcquired)
        newRankVO = self._buildRankVO(nextRank)
        return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(currentRank), rankRightVO=self._buildRankVO(nextRank), steps=self._buildProgress(nextRank, newStepsState=newStepsState, changeAcquired=changeAcquired)))

    def _getLadderPointReceiveData(self, maxRank, vehRank, currentRank):
        state = RANKEDBATTLES_ALIASES.ANIM_ACHIEVE_LADDER_POINT
        points = self.rankedController.getLadderPoints()
        rankLeftVO = self._buildRankVO(maxRank, True, ladderPoints=(points - 1, points), showLadderPoints=True)
        rankRightVO = self._buildRankVO(vehRank, isEnabled=True)
        steps = self._buildProgress(currentRank)
        newSteps = self._buildProgress(vehRank)
        return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps, newSteps=newSteps, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(maxRank, True, ladderPoints=(points - 1, points), showLadderPoints=True), rankRightVO=self._buildRankVO(vehRank, isEnabled=True), steps=self._buildProgress(vehRank)))

    def _buildData(self, ranks, currentRank, lastRank):
        currentRankID = currentRank.getID()
        lastRankID = lastRank.getID()
        if currentRankID == 0:
            state = RANKEDBATTLES_ALIASES.RANK_INIT_STATE
            nextRank = ranks[currentRankID + 1]
            steps = self._buildProgress(nextRank)
            infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_INITTEXT, battles=str(len(steps))))
            rankLeftVO = self._buildRankVO(nextRank)
            return [self._buildVO(state, infoText=infoText, rankLeftVO=rankLeftVO, steps=steps, finalState=self._buildFinalState(state, self._buildRankVO(nextRank), steps=self._buildProgress(nextRank)))]
        else:
            maxAccRankID = self.rankedController.getAccRanksTotal()
            skipNewRankCheck = currentRankID == 1 and self.rankedController.wasAwardWindowShown() and not self._isHuge()
            if currentRank.isNewForPlayer() and not skipNewRankCheck:
                if lastRank.isAcquired():
                    isJumpOverRank = currentRankID - lastRankID > 1
                    if currentRankID > maxAccRankID:
                        return [self._getLadderPointReceiveData(maxRank=ranks[maxAccRankID], vehRank=ranks[currentRankID + 1], currentRank=currentRank)]
                    if currentRankID == 1:
                        if self._isHuge() or currentRank.isRewardClaimed():
                            return [self._getFirstRankReachiveStateData(currentRank=ranks[1], nextRank=ranks[2])]
                        return [self._getFirstRankReceiveStateData(currentRank=currentRank)]
                    if not self._checkClaim() or currentRank.isRewardClaimed():
                        states = []
                        if isJumpOverRank:
                            tmpRankID = lastRankID + 1
                            while tmpRankID <= currentRankID:
                                if tmpRankID == 1:
                                    states.append(self._getFirstRankReachiveStateData(currentRank=ranks[1], nextRank=ranks[2], newStepsState=RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE, changeAcquired=True))
                                else:
                                    states.append(self._getReachievedReceiveStateData(lastRank=ranks[tmpRankID - 1], currentRank=ranks[tmpRankID], nextRank=ranks[tmpRankID + 1], stepsState=RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE, newStepsState=RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE, changeAcquired=tmpRankID == currentRankID))
                                tmpRankID += 1

                            return states
                        return [self._getReachievedReceiveStateData(lastRank=lastRank, currentRank=currentRank, nextRank=ranks[currentRankID + 1])]
                    if isJumpOverRank:
                        states = []
                        tmpRankID = lastRankID + 1
                        while tmpRankID <= currentRankID:
                            if tmpRankID == currentRankID:
                                states.append(self._getRankReceiveForFirstTimeData(lastRank=ranks[tmpRankID - 1], currentRank=ranks[tmpRankID]))
                            elif tmpRankID == 1:
                                states.append(self._getFirstRankReachiveStateData(currentRank=ranks[1], nextRank=ranks[2], newStepsState=RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE, changeAcquired=True))
                            else:
                                states.append(self._getReachievedReceiveStateData(lastRank=ranks[tmpRankID - 1], currentRank=ranks[tmpRankID], nextRank=ranks[tmpRankID + 1], stepsState=RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE, newStepsState=RANKEDBATTLES_ALIASES.STEP_RECEIVED_BLINK_STATE))
                            tmpRankID += 1

                        return states
                    return [self._getRankReceiveForFirstTimeData(lastRank=lastRank, currentRank=currentRank)]
                if lastRank.isLost():
                    if lastRank.getType() == RANK_TYPES.VEHICLE and lastRank.isMax():
                        nextRank = ranks[lastRank.getID()]
                    else:
                        nextRank = ranks[lastRank.getID() + 1]
                    state = RANKEDBATTLES_ALIASES.RANK_LOST_STATE
                    steps = self._buildProgress(nextRank)
                    newSteps = self._buildProgress(lastRank)
                    rankLeftVO = self._buildRankVO(lastRank, True)
                    rankRightVO = self._buildRankVO(nextRank)
                    newRankVO = self._buildRankVO(currentRank, True)
                    return [self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(currentRank, True), rankRightVO=self._buildRankVO(lastRank), steps=self._buildProgress(lastRank)))]
            if self._checkClaim() and not currentRank.isRewardClaimed():
                state = RANKEDBATTLES_ALIASES.NEW_RANK_CONGRAT_STATE
                infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NEWRANKCONGRAT))
                rankLeftVO = self._buildRankVO(currentRank, True)
                return [self._buildVO(state, infoText=infoText, rankLeftVO=rankLeftVO, finalState=self._buildFinalState(state, rankLeftVO=self._buildRankVO(currentRank, True)))]
            nextRank = ranks[currentRankID + 1]
            steps = self._buildProgress(nextRank)
            shieldStatus = self.rankedController.getShieldStatus(currentRank)
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
            if RANKEDBATTLES_ALIASES.RANK_IDLE_STATE and currentRankID >= maxAccRankID:
                ladderPoints = (self.rankedController.getLadderPoints(), None)
                rankLeftVO = self._buildRankVO(ranks[maxAccRankID], True, showLadderPoints=True, ladderPoints=ladderPoints)
                finalLeftVO = self._buildRankVO(ranks[maxAccRankID], True, showLadderPoints=True, ladderPoints=ladderPoints)
                rankRightVO = self._buildRankVO(ranks[maxAccRankID + 1])
                finalRightVO = self._buildRankVO(ranks[maxAccRankID + 1])
            else:
                rankLeftVO = self._buildRankVO(currentRank, True)
                finalLeftVO = self._buildRankVO(currentRank, True)
                rankRightVO = self._buildRankVO(nextRank)
                finalRightVO = self._buildRankVO(nextRank)
            isShieldOneRankState = state in RANKEDBATTLES_ALIASES.ANIM_SHIELD_ONE_RANK_STATES
            return [self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps, finalState=self._buildFinalState(state, rankLeftVO=finalLeftVO, rankRightVO=None if isShieldOneRankState else finalRightVO, steps=None if isShieldOneRankState else self._buildProgress(nextRank)))]

    def _buildVO(self, state, infoText='', nextInfoText='', rankLeftVO=None, rankRightVO=None, newRankVO=None, steps=None, newSteps=None, finalState=None):
        return {'state': state,
         'infoText': infoText,
         'nextInfoText': nextInfoText,
         'rankLeftVO': rankLeftVO,
         'rankRightVO': rankRightVO,
         'newRankVO': newRankVO,
         'stepsContainerVO': {'steps': steps or ()},
         'newStepsContainerVO': {'steps': newSteps or ()},
         'isHuge': self._isHuge(),
         'autoPlay': self._isAutoPlay(),
         'finalState': finalState,
         'animationEnabled': self._isAnimationEnabled()}

    def _buildRankVO(self, rank, isEnabled=False, ladderPoints=None, showLadderPoints=False):
        return buildRankVO(rank=rank, isEnabled=isEnabled, imageSize=RANKEDBATTLES_ALIASES.WIDGET_HUGE if self._isHuge() else RANKEDBATTLES_ALIASES.WIDGET_MEDIUM, hasTooltip=self._hasAdditionalRankInfo(), shieldStatus=self.rankedController.getShieldStatus(rank), shieldAnimated=True, showLadderPoints=showLadderPoints, ladderPoints=ladderPoints)

    def _buildProgress(self, rank, newStepsState=None, changeAcquired=False):
        result = []
        progress = rank.getProgress()
        if progress is None:
            return result
        else:
            for step in progress.getSteps():
                if not changeAcquired and newStepsState is not None:
                    stepState = newStepsState
                elif step.isAcquired():
                    if changeAcquired and newStepsState is not None:
                        stepState = newStepsState
                    else:
                        stepState = RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE
                        if step.isNewForPlayer():
                            stepState = RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE
                            if rank.isNewForPlayer():
                                stepState = RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE
                elif step.isLost():
                    stepState = RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE
                    if step.isNewForPlayer() and not rank.isLost():
                        stepState = RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE
                else:
                    stepState = RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE
                result.append({'state': stepState})

            return result

    def _buildFinalState(self, state, rankLeftVO, rankRightVO=None, steps=None):
        return None

    def _isAnimationEnabled(self):
        return True


class RankedBattleResultsWidget(RankedBattlesWidget):

    def __init__(self):
        super(RankedBattleResultsWidget, self).__init__()
        self._soundCallerType = self._soundMgr.CALLER.POST_BATTLE

    def _dispose(self):
        self._soundMgr.switchHangarLock(isLocked=False)
        super(RankedBattleResultsWidget, self)._dispose()

    def onWidgetClick(self):
        pass

    def _checkClaim(self):
        return False

    def _isHuge(self):
        return True

    def _buildVO(self, state, infoText='', nextInfoText='', rankLeftVO=None, rankRightVO=None, newRankVO=None, steps=None, newSteps=None, finalState=None):
        vo = super(RankedBattleResultsWidget, self)._buildVO(state, infoText=infoText, nextInfoText=nextInfoText, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, finalState=finalState)
        return vo

    def _isAutoPlay(self):
        return False

    def _hasAdditionalRankInfo(self):
        return False

    def _buildFinalState(self, state, rankLeftVO, rankRightVO=None, steps=None):
        rankLeftVO = self.__setFinalState(rankLeftVO)
        rankLeftVO['isEnabled'] = state != RANKEDBATTLES_ALIASES.RANK_INIT_STATE
        if rankRightVO is not None:
            rankRightVO = self.__setFinalState(rankRightVO)
        if steps is not None:
            for step in steps:
                stepState = step['state']
                if stepState in RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATES:
                    step['state'] = RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE
                step['state'] = RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE

        return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps)

    def _isAnimationEnabled(self):
        return bool(AccountSettings.getSettings(ENABLE_RANKED_ANIMATIONS))

    def __setFinalState(self, rank):
        shield = rank.get('shield', None)
        if shield is not None:
            if shield['newState'] is not None:
                shield['state'] = shield['newState']
                shield['newState'] = None
                rank['shield'] = shield
        scoreData = rank.get('scoreData', None)
        if scoreData is not None:
            if scoreData['newLabel'] != '':
                scoreData['label'] = scoreData['newLabel']
                scoreData['newLabel'] = ''
                rank['scoreData'] = scoreData
        return rank
