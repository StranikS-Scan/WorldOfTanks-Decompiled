# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/collective_goal_marathon.py
from adisp import adisp_async
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.impl.gen import R
from gui.marathon.marathon_constants import MarathonState
from gui.marathon.marathon_event import MarathonEvent
from gui.marathon.marathon_event_container import MarathonEventContainer
from gui.marathon.marathon_event_controller import marathonCreator
from gui.marathon.marathon_resource_manager import MarathonResourceManager
from helpers import time_utils
COLLECTIVE_GOAL_MARATHON_PREFIX = 'collective_goal'

class CollectiveGoalEvent(MarathonEvent):

    @adisp_async
    def getUrl(self, callback):
        config = self._getConfig()
        callback(config.url)

    def setState(self):
        config = self._getConfig()
        currentTime = time_utils.getServerUTCTime()
        if config.isEnabled:
            config.startTime <= currentTime <= config.finishTime and self._data.setState(MarathonState.IN_PROGRESS)
        else:
            self._data.setState(MarathonState.DISABLED)

    def getClosestStatusUpdateTime(self):
        pass

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.marathon()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_MARATHONS

    @property
    def isNeedHandlingEscape(self):
        return True

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createCollectiveGoalMarathonWebHandlers
        return createCollectiveGoalMarathonWebHandlers()

    def getMarathonProgress(self):
        pass

    def getMarathonFlagState(self, vehicle):
        return {'enable': False,
         'visible': False}

    def _getConfig(self):
        return self._lobbyContext.getServerSettings().collectiveGoalMarathonsConfig


class CollectiveGoalResourceManager(MarathonResourceManager):

    def _initialize(self):
        pass


@marathonCreator(CollectiveGoalEvent, CollectiveGoalResourceManager)
class CollectiveGoalMarathon(MarathonEventContainer):

    def _override(self):
        self.prefix = COLLECTIVE_GOAL_MARATHON_PREFIX
        self.tokenPrefix = ''
        self.styleTokenPostfix = ''
        self.doesShowRewardScreen = False
        self.doesShowRewardVideo = False
        self.doesShowInPostBattle = False
        self.questsPerStep = 0
        self.vehicleName = ''
        self.suspendPrefix = ''
        self.completedTokenPostfix = ''
        self.hangarFlagName = ''
        self.awardTokensPostfix = tuple()
        self.awardPostTokensPostfix = tuple()
        self.showFlagTooltipBottom = False
        self.flagTooltip = ''
        self.disabledFlagTooltip = ''
        self.marathonTooltipHeader = ''
        self.bodyAddInfo = R.invalid()
