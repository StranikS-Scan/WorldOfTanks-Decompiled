# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/difficulty_level_controller.py
from skeletons.gui.game_control import IGameController
import typing
if typing.TYPE_CHECKING:
    from Event import Event
    from last_stand_common.last_stand_constants import QUEUE_TYPE
    from last_stand.gui.ls_gui_constants import DifficultyLevel
    from last_stand.gui.game_control.difficulty_level_controller import _Level

class IDifficultyLevelController(IGameController):
    onChangeDifficultyLevelStatus = None
    onChangeDifficultyLevel = None
    onLevelsInfoReady = None

    def selectLevel(self, level):
        raise NotImplementedError

    def getSelectedLevel(self):
        raise NotImplementedError

    def getCurrentQueueType(self):
        raise NotImplementedError

    def getLevelsInfo(self):
        raise NotImplementedError

    @staticmethod
    def getLastSelectedLevel():
        raise NotImplementedError
