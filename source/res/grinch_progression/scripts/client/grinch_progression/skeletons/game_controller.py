# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/skeletons/game_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from grinch_progression_common.grinch_progression_constants import ProgressionStates

class IGrinchProgressionController(IGameController):
    onDataUpdated = None

    def getGrinchVehicles(self):
        raise NotImplementedError

    def getProgressionState(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def token(self):
        raise NotImplementedError

    @property
    def enoughForClaimReward(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getPoints(self):
        raise NotImplementedError

    def getTimeTillSeasonStart(self):
        raise NotImplementedError

    def getCurrentChapter(self):
        raise NotImplementedError

    def getNextChapter(self):
        raise NotImplementedError

    def getTimeTillNextChapterStart(self):
        raise NotImplementedError

    def getStartEventDate(self):
        raise NotImplementedError

    def getEndEventDate(self):
        raise NotImplementedError

    def getCurrentSeasonChapters(self):
        raise NotImplementedError

    def getPreviousPointsCount(self):
        raise NotImplementedError

    def setPreviousPointsCount(self, value):
        raise NotImplementedError

    def getChapterDates(self, chapterId):
        raise NotImplementedError

    def getMaxChapterStep(self):
        raise NotImplementedError

    def getIsFirstEntry(self):
        raise NotImplementedError

    def setIsFirstEntry(self, value):
        raise NotImplementedError

    def getCurrentChapterStep(self):
        raise NotImplementedError
