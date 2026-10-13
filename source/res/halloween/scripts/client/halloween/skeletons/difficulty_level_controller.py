# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/difficulty_level_controller.py
from __future__ import absolute_import
from skeletons.gui.game_control import IGameController
import typing
if typing.TYPE_CHECKING:
    from Event import Event
    from halloween_common.halloween_constants import QUEUE_TYPE
    from halloween.gui.halloween_gui_constants import DifficultyLevel
    from halloween.gui.game_control.difficulty_level_controller import _Level

class IDifficultyLevelController(IGameController):
    onChangeDifficultyLevelStatus = None
    onChangeDifficultyLevel = None

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
