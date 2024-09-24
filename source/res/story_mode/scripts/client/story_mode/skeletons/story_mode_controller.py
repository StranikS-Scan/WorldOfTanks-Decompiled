# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/skeletons/story_mode_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from story_mode_common.configs.story_mode_missions import MissionsModel, MissionModel
    from story_mode_common.configs.story_mode_settings import SettingsModel
    from Event import Event
    from story_mode_common.story_mode_constants import MissionType

class IStoryModeController(IGameController):
    onSyncDataUpdated = None
    onMissionsConfigUpdated = None

    @property
    def isOnboarding(self):
        raise NotImplementedError

    @property
    def isQuittingBattle(self):
        raise NotImplementedError

    @property
    def selectedMissionId(self):
        raise NotImplementedError

    @property
    def isSelectedMissionOnboarding(self):
        raise NotImplementedError

    @selectedMissionId.setter
    def selectedMissionId(self, value):
        raise NotImplementedError

    def isEventEntryPointVisible(self):
        raise NotImplementedError

    def isShowActiveModeState(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isInPrb(self):
        raise NotImplementedError

    def switchPrb(self):
        raise NotImplementedError

    @property
    def settings(self):
        raise NotImplementedError

    @property
    def missions(self):
        raise NotImplementedError

    @property
    def needToShowAward(self):
        raise NotImplementedError

    def popMissionProgressDiff(self, missionId):
        raise NotImplementedError

    def getFirstMission(self):
        raise NotImplementedError

    def isMissionCompleted(self, missionId):
        raise NotImplementedError

    def isEventMissionSuitable(self, mission):
        raise NotImplementedError

    def isFirstTaskNotCompleted(self, mission):
        raise NotImplementedError

    def isAnyTaskNotCompleted(self, mission):
        raise NotImplementedError

    def isSelectedMissionLocked(self):
        raise NotImplementedError

    def getNextMission(self, missionId):
        raise NotImplementedError

    @staticmethod
    def goToQueue():
        raise NotImplementedError

    @staticmethod
    def exitQueue():
        raise NotImplementedError

    @staticmethod
    def goToBattle():
        raise NotImplementedError

    def goToHangar(self, guiCtx=None):
        raise NotImplementedError

    def quitBattle(self):
        raise NotImplementedError

    def popWaitingToBeShownAwardData(self):
        raise NotImplementedError

    def awardShown(self):
        raise NotImplementedError

    def startMusic(self):
        raise NotImplementedError

    def stopMusic(self):
        raise NotImplementedError

    def isMissionTaskCompleted(self, missionId, taskId):
        raise NotImplementedError

    def filterMissions(self, missionType=None):
        raise NotImplementedError

    def isNewbieGuidanceNeeded(self):
        raise NotImplementedError

    def isNewNeededForNewbies(self):
        raise NotImplementedError

    def setNewForNewbiesSeen(self):
        raise NotImplementedError

    def chooseSelectedMissionId(self, isEvent=False):
        raise NotImplementedError
