# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/skeletons/game_controller.py
from skeletons.gui.game_control import IGameController

class IHBProgressionOnTokensController(IGameController):
    progressionToken = ''
    PROGRESSION_COMPLETE_TOKEN = ''
    onProgressPointsUpdated = None
    onSettingsChanged = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def setSettings(self, settings):
        raise NotImplementedError

    def saveCurPoints(self):
        raise NotImplementedError

    def getPrevPoints(self):
        raise NotImplementedError

    def getCurPoints(self):
        raise NotImplementedError

    def getCurrentStageData(self):
        raise NotImplementedError

    def getProgressionLevelsData(self):
        raise NotImplementedError

    def getProgessionPointsData(self):
        raise NotImplementedError

    def getProgressionData(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isFinished(self):
        raise NotImplementedError
