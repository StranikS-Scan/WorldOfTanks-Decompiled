# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/skeletons/progression_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    import Event
    from typing import Dict, Tuple, List, Union
    from gui.server_events.event_items import Quest
    from gui.server_events.bonuses import SimpleBonus

class ICosmicEventProgressionController(IGameController):
    onProgressPointsUpdated = None

    def getQuests(self):
        raise NotImplementedError

    def getDailyQuests(self):
        raise NotImplementedError

    def getAchievementsQuests(self):
        raise NotImplementedError

    def getCurrentPoints(self):
        raise NotImplementedError

    def getMaxProgressionPoints(self):
        raise NotImplementedError

    def getProgression(self):
        raise NotImplementedError

    def isCosmicProgressionQuest(self, questID):
        raise NotImplementedError

    def getBonuses(self):
        raise NotImplementedError

    def getCurrentStage(self):
        raise NotImplementedError

    def setQuestProgressAsViewed(self, quest):
        raise NotImplementedError

    def getQuestCompletionChanged(self, quest):
        raise NotImplementedError

    def getLastSeenPoints(self):
        raise NotImplementedError

    def updateLastSeenPoints(self, points=None):
        raise NotImplementedError

    def isProgressionFinished(self):
        raise NotImplementedError

    def collectSortedDailyQuests(self):
        raise NotImplementedError
