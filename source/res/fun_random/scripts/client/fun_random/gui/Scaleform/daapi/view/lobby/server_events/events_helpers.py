# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/server_events/events_helpers.py
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import QuestPostBattleInfo
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.server_events import formatters
from shared_utils import findFirst

class FunProgressionQuestPostBattleInfo(QuestPostBattleInfo, FunProgressionWatcher):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        isCompleted = self.event.isCompleted(progress=pCur)
        return super(FunProgressionQuestPostBattleInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)

    @hasActiveProgression(defReturn=[])
    def _getBonuses(self, svrEvents, pCur=None, bonuses=None):
        currCounter = self.event.getBonusCount(progress=pCur)
        stage = findFirst(lambda s: s.requiredCounter == currCounter, self.getActiveProgression().stages)
        bonuses = stage.bonuses if stage is not None else []
        return super(FunProgressionQuestPostBattleInfo, self)._getBonuses(svrEvents, pCur, bonuses)

    def _getBonusCount(self, pCur=None):
        return self.NO_BONUS_COUNT

    @hasActiveProgression(defReturn=[])
    def _getProgresses(self, pCur, pPrev):
        descriptionRes = R.strings.fun_random.battleResult.progressDescription
        prevCounter, currCounter = self.event.getBonusCount(progress=pPrev), self.event.getBonusCount(progress=pCur)
        stage = findFirst(lambda s: prevCounter < s.requiredCounter, self.getActiveProgression().stages)
        return [{'progrTooltip': None,
          'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
          'currentProgrVal': currCounter - stage.prevRequiredCounter,
          'maxProgrVal': stage.requiredCounter - stage.prevRequiredCounter,
          'description': backport.text(descriptionRes(), triggerDescription=self.event.getDescription()),
          'progressDiff': '+ %s' % backport.getIntegralFormat(currCounter - prevCounter),
          'progressDiffTooltip': TOOLTIPS.QUESTS_PROGRESS_EARNEDINBATTLE}] if stage is not None and prevCounter < currCounter else []

    def _getProgressValues(self, svrEvents=None, pCur=None, pPrev=None):
        return (0,
         0,
         formatters.PROGRESS_BAR_TYPE.NONE,
         None)

    def _getStatus(self, pCur=None):
        return (MISSIONS_STATES.COMPLETED, backport.text(R.strings.quests.details.status.completed())) if self.event.isCompleted(progress=pCur) else (MISSIONS_STATES.NONE, '')
