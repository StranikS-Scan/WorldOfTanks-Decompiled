# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/skeletons/gui/game_control.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event

class IComp7LightProgressionController(IGameController):
    onProgressPointsUpdated = None
    onSettingsChanged = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isFinished(self):
        raise NotImplementedError

    @property
    def progressionToken(self):
        raise NotImplementedError

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
