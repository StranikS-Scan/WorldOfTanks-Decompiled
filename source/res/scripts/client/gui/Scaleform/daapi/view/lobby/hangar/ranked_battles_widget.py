# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ranked_battles_widget.py
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.meta.RankedBattlesWidgetMeta import RankedBattlesWidgetMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.ranked_battles.constants import SOUND, RANK_TYPES
from gui.ranked_battles.ranked_models import VehicleRank
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

    class CALLER:
        HANGAR = 'hangar'
        POST_BATTLE = 'post_battle'

    def __init__(self):
        self.__sound = None
        self.__isHangarBlocked = False
        g_playerEvents.onBattleResultsReceived += self.switchHangarLock
        self._eventSoundMap = {self.CALLER.POST_BATTLE: {RANKEDBATTLES_ALIASES.RANK_LOST_STATE: SOUND.RANK_LOST_POST_BATTLE,
                                   RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE: SOUND.STEP_EARNED_POST_BATTLE,
                                   RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE: SOUND.STEP_LOST_POST_BATTLE,
                                   RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE: SOUND.STEP_NOT_CHANGED_POST_BATTLE,
                                   RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE: SOUND.RANK_EARNED_POST_BATTLE},
         self.CALLER.HANGAR: {RANKEDBATTLES_ALIASES.RANK_LOST_STATE: SOUND.RANK_LOST,
                              RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE: SOUND.STEP_EARNED,
                              RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE: SOUND.STEP_LOST}}
        self.__initBlockingSounds()
        return

    def setSoundForEvent(self, eventType, rank=None, caller=None):
        if self.__callerBlocked(caller) or self.__eventShouldBeIgnored(eventType):
            return
        if eventType in self._STEP_CHANGED_EVENTS and self.__sound in self._RANK_CHANGED_SOUNDS:
            return
        if eventType == RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE and eventType not in self.__getSoundMap(caller):
            if rank.getType() == RANK_TYPES.VEHICLE:
                soundName = SOUND.VEH_RANK_EARNED
            else:
                soundName = SOUND.getRankEarnedEvent(rank.getID())
        else:
            soundName = self.__getSoundMap(caller).get(eventType)
        self.__sound = soundName

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

    def __getSoundMap(self, caller):
        return self._eventSoundMap.get(caller, {})

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
        self.as_setDataS(self._buildData(ranks, currentRank, lastRank))
        self._soundMgr.play()

    def onSoundTrigger(self, triggerName):
        self._soundMgr.playInstantSound(triggerName, self._soundCallerType)

    def onWidgetClick(self):
        self.fireEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_VIEW_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        if self._currentRank is not None and not self._currentRank.isRewardClaimed():
            showRankedAwardWindow(self._currentRank.getID(), showNext=False)
            self.rankedController.runQuest(self._currentRank.getQuest())
        return

    def onAnimationFinished(self):
        self.rankedController.setLastRank(g_currentVehicle.item)

    def _checkClaim(self):
        return True

    def _isHuge(self):
        return False

    def _hasAdditionalRankInfo(self):
        return True

    def _getCountLabel(self, rank):
        pass

    def _buildData(self, ranks, currentRank, lastRank):
        currentRankID = currentRank.getID()
        if currentRankID == 0:
            state = RANKEDBATTLES_ALIASES.RANK_INIT_STATE
            nextRank = ranks[currentRankID + 1]
            steps = self._buildProgress(nextRank)
            infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_INITTEXT, battles=str(len(steps))))
            countText = self._getCountLabel(nextRank)
            rankLeftVO = self._buildRankVO(nextRank)
            return self._buildVO(state, infoText=infoText, rankLeftVO=rankLeftVO, steps=steps, countText=countText)
        else:
            if currentRank.isNewForPlayer():
                if lastRank.isAcquired():
                    self._addSoundEvent(RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE, currentRank)
                    if currentRankID == 1 and not self._isHuge():
                        state = RANKEDBATTLES_ALIASES.FIRST_RANK_RECEIVE_STATE
                        steps = self._buildProgress(currentRank)
                        infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_INITTEXT, battles=str(len(steps))))
                        nextInfoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NEWRANKCONGRAT))
                        rankLeftVO = self._buildRankVO(currentRank, True)
                        return self._buildVO(state, infoText=infoText, rankLeftVO=rankLeftVO, steps=steps, nextInfoText=nextInfoText)
                    if not self._checkClaim() or currentRank.isRewardClaimed() or self._isHuge() and currentRankID == 1:
                        nextRank = ranks[currentRankID + 1]
                        if self._isHuge():
                            state = RANKEDBATTLES_ALIASES.RANK_RECEIVE_HUGE_STATE
                            steps = self._buildProgress(nextRank)
                            countText = ''
                            nextCountText = nextRank.getProgress().getNewUserStr()
                            rankLeftVO = self._buildRankVO(currentRank, True)
                            rankRightVO = self._buildRankVO(currentRank, True)
                        else:
                            state = RANKEDBATTLES_ALIASES.RANK_RECEIVE_STATE
                            steps = self._buildProgress(currentRank)
                            countText = currentRank.getProgress().getUserStr()
                            nextCountText = currentRank.getProgress().getNewUserStr()
                            rankLeftVO = self._buildRankVO(lastRank, True)
                            rankRightVO = self._buildRankVO(currentRank)
                        newSteps = self._buildProgress(nextRank)
                        newCountText = nextRank.getProgress().getUserStr()
                        newRankVO = self._buildRankVO(nextRank)
                        return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, countText=countText, nextCountText=nextCountText, newCountText=newCountText)
                    state = RANKEDBATTLES_ALIASES.RANK_RECEIVE_FOR_FIRST_TIME_STATE
                    infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NEWRANKCONGRAT))
                    steps = self._buildProgress(currentRank)
                    countText = currentRank.getProgress().getUserStr()
                    nextCountText = currentRank.getProgress().getNewUserStr()
                    rankLeftVO = self._buildRankVO(lastRank, True)
                    rankRightVO = self._buildRankVO(currentRank)
                    return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, infoText=infoText, steps=steps, countText=countText, nextCountText=nextCountText)
                if lastRank.isLost():
                    self._addSoundEvent(RANKEDBATTLES_ALIASES.RANK_LOST_STATE)
                    if lastRank.getType() == RANK_TYPES.VEHICLE and lastRank.isMax():
                        nextRank = ranks[lastRank.getID()]
                    else:
                        nextRank = ranks[lastRank.getID() + 1]
                    if self._isHuge():
                        state = RANKEDBATTLES_ALIASES.RANK_LOST_HUGE_STATE
                        steps = self._buildProgress(lastRank)
                        countText = ''
                        nextCountText = lastRank.getProgress().getNewUserStr()
                    else:
                        state = RANKEDBATTLES_ALIASES.RANK_LOST_STATE
                        steps = self._buildProgress(nextRank)
                        countText = nextRank.getProgress().getUserStr()
                        nextCountText = nextRank.getProgress().getNewUserStr()
                    newSteps = self._buildProgress(lastRank)
                    newCountText = lastRank.getProgress().getUserStr()
                    rankLeftVO = self._buildRankVO(lastRank, True)
                    rankRightVO = self._buildRankVO(nextRank)
                    newRankVO = self._buildRankVO(currentRank, True)
                    return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, newRankVO=newRankVO, steps=steps, newSteps=newSteps, countText=countText, nextCountText=nextCountText, newCountText=newCountText)
            if self._checkClaim() and not currentRank.isRewardClaimed():
                state = RANKEDBATTLES_ALIASES.NEW_RANK_CONGRAT_STATE
                infoText = text_styles.hightlight(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NEWRANKCONGRAT))
                rankLeftVO = self._buildRankVO(currentRank, True)
                return self._buildVO(state, infoText=infoText, rankLeftVO=rankLeftVO, steps=None)
            state = RANKEDBATTLES_ALIASES.RANK_IDLE_STATE
            nextRank = ranks[currentRankID + 1]
            steps = self._buildProgress(nextRank)
            showText = True
            for step in steps:
                if step['state'] in [RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE, RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE, RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE]:
                    showText = False

            countText = nextRank.getProgress().getUserStr()
            if self._isHuge():
                if not showText:
                    countText = ''
                else:
                    countText = text_styles.stats(_ms(RANKED_BATTLES.RANKEDBATTLESWIDGET_NOCHANGES))
            rankLeftVO = self._buildRankVO(currentRank, True)
            rankRightVO = self._buildRankVO(nextRank)
            return self._buildVO(state, rankLeftVO=rankLeftVO, rankRightVO=rankRightVO, steps=steps, countText=countText)

    def _buildVO(self, state, infoText='', nextInfoText='', rankLeftVO=None, rankRightVO=None, newRankVO=None, countText='', nextCountText='', steps=None, newCountText='', newSteps=None):
        return {'state': state,
         'infoText': infoText,
         'nextInfoText': nextInfoText,
         'rankLeftVO': rankLeftVO,
         'rankRightVO': rankRightVO,
         'newRankVO': newRankVO,
         'stepsContainerVO': {'countText': countText,
                              'nextCountText': nextCountText,
                              'steps': steps or ()},
         'newStepsContainerVO': {'countText': newCountText,
                                 'nextCountText': '',
                                 'steps': newSteps or ()},
         'isHuge': self._isHuge()}

    def _buildRankVO(self, rank, isEnabled=False):
        isMaster = False
        rankCount = ''
        if isinstance(rank, VehicleRank):
            isMaster = True
            if self._hasAdditionalRankInfo() and rank.isAcquired():
                rankCount = BigWorld.wg_getIntegralFormat(rank.getSerialID())
        imageSize = 'huge' if self._isHuge() else 'medium'
        return {'imageSrc': rank.getIcon(imageSize),
         'smallImageSrc': rank.getIcon('small'),
         'isEnabled': isEnabled,
         'isMaster': isMaster,
         'rankID': str(rank.getID()),
         'rankCount': rankCount,
         'hasTooltip': self._hasAdditionalRankInfo()}

    def _buildProgress(self, rank):
        result = []
        progress = rank.getProgress()
        if progress is None:
            return result
        else:
            for step in progress.getSteps():
                if step.isAcquired():
                    stepState = RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE
                    if step.isNewForPlayer():
                        stepState = RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_STATE
                        self._addSoundEvent(stepState)
                        if rank.isNewForPlayer():
                            stepState = RANKEDBATTLES_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE
                elif step.isLost():
                    stepState = RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE
                    if step.isNewForPlayer() and not rank.isLost():
                        stepState = RANKEDBATTLES_ALIASES.STEP_JUST_LOST_STATE
                        self._addSoundEvent(stepState)
                else:
                    stepState = RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE
                    self._addSoundEvent(stepState)
                result.append({'state': stepState})

            return result

    def _addSoundEvent(self, event, rank=None):
        if not self._isMuted():
            self._soundMgr.setSoundForEvent(event, rank, self._soundCallerType)

    def _isMuted(self):
        return False


class RankedBattleResultsFinalWidget(RankedBattlesWidget):

    def __init__(self):
        super(RankedBattleResultsFinalWidget, self).__init__()
        self._soundCallerType = self._soundMgr.CALLER.POST_BATTLE

    def onWidgetClick(self):
        pass

    def _getCountLabel(self, rank):
        return rank.getProgress().getUserStr() if rank.hasProgress() else ''

    def _dispose(self):
        self._soundMgr.switchHangarLock(isLocked=False)
        super(RankedBattleResultsFinalWidget, self)._dispose()

    def _checkClaim(self):
        return False

    def _hasAdditionalRankInfo(self):
        return False

    def _isMuted(self):
        return True

    def _buildVO(self, state, infoText='', nextInfoText='', rankLeftVO=None, rankRightVO=None, newRankVO=None, countText='', nextCountText='', steps=None, newCountText='', newSteps=None):
        vo = super(RankedBattleResultsFinalWidget, self)._buildVO(state, infoText, nextInfoText, rankLeftVO, rankRightVO, newRankVO, countText, nextCountText, steps, newCountText, newSteps)
        if vo['state'] == RANKEDBATTLES_ALIASES.RANK_INIT_STATE:
            vo['infoText'] = ''
        return vo


class RankedBattleResultsWidget(RankedBattleResultsFinalWidget):

    def _isHuge(self):
        return True

    def _getCountLabel(self, rank):
        pass

    def _buildVO(self, state, infoText='', nextInfoText='', rankLeftVO=None, rankRightVO=None, newRankVO=None, countText='', nextCountText='', steps=None, newCountText='', newSteps=None):
        vo = super(RankedBattleResultsWidget, self)._buildVO(state, infoText, nextInfoText, rankLeftVO, rankRightVO, newRankVO, countText, nextCountText, steps, newCountText, newSteps)
        if vo['state'] not in (RANKEDBATTLES_ALIASES.RANK_IDLE_STATE, RANKEDBATTLES_ALIASES.RANK_INIT_STATE):
            vo['newStepsContainerVO'] = vo['stepsContainerVO']
            vo['stepsContainerVO'] = {'countText': '',
             'nextCountText': '',
             'steps': ()}
        return vo

    def _isMuted(self):
        return False
