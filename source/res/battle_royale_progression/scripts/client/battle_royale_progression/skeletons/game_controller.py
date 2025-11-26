# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/skeletons/game_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Dict
    from Event import Event

class IBRProgressionOnTokensController(IGameController):
    progressionToken = ''
    PROGRESSION_COMPLETE_TOKEN = ''
    onProgressPointsUpdated = None
    onSettingsChanged = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isFinished(self):
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

    def getProgessionPointsData(self):
        raise NotImplementedError

    def getProgressionData(self):
        raise NotImplementedError
