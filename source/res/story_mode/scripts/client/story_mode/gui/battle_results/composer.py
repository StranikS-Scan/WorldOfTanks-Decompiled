# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_results/composer.py
from logging import getLogger
from gui.battle_results.composer import IStatsComposer
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from helpers import dependency
from story_mode.gui.battle_results.templates import STORY_MODE_RESULTS_BLOCK
from story_mode.gui.shared.event_dispatcher import showEpilogueWindow, showOnboardingBattleResultWindow, showPrebattleAndGoToQueue, showBattleResultWindow
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)

class StoryModeStatsComposer(IStatsComposer):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, _):
        super(StoryModeStatsComposer, self).__init__()
        self._block = STORY_MODE_RESULTS_BLOCK.clone()

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)

    def getVO(self):
        return self._block.getVO()

    def popAnimation(self):
        return None

    @staticmethod
    def onShowResults(arenaUniqueID):
        pass

    def onResultsPosted(self, arenaUniqueID):
        resultVO = self._block.getVO()
        if resultVO['isForceOnboarding']:
            if not self._storyModeCtrl.isEnabled():
                self._storyModeCtrl.skipOnboarding()
                return
            missionId = resultVO['missionId']
            if resultVO['finishResult'] == PLAYER_TEAM_RESULT.WIN:
                nextMission = self._storyModeCtrl.getNextMission(missionId)
                if missionId == self._storyModeCtrl.missions.onboardingLastMissionId or nextMission is None:
                    showEpilogueWindow()
                else:
                    showPrebattleAndGoToQueue(missionId=nextMission.missionId)
            else:
                showOnboardingBattleResultWindow(finishReason=resultVO['finishReason'], missionId=missionId)
        else:
            showBattleResultWindow(arenaUniqueID)
        return
