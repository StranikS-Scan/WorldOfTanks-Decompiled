# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/skeletons/story_mode_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from story_mode_common.configs.story_mode_missions import MissionsModel, MissionModel
    from story_mode_common.configs.story_mode_settings import SettingsModel
    from Event import Event

class IStoryModeController(IGameController):
    onSyncDataUpdated = None

    @property
    def isOnboarding(self):
        raise NotImplementedError

    @property
    def isQuittingBattle(self):
        raise NotImplementedError

    @property
    def selectedMissionId(self):
        raise NotImplementedError

    @selectedMissionId.setter
    def selectedMissionId(self, value):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isInPrb(self):
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

    def getFirstMission(self):
        raise NotImplementedError

    def isMissionCompleted(self, missionId):
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

    def skipOnboarding(self):
        raise NotImplementedError

    def awardShown(self):
        raise NotImplementedError

    def startOnboardingMusic(self, event=None):
        raise NotImplementedError

    def stopOnboardingMusic(self):
        raise NotImplementedError
