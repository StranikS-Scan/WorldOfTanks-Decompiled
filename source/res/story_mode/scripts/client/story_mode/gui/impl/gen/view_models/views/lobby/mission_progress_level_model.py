# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_progress_level_model.py
from story_mode.gui.impl.gen.view_models.views.lobby.progress_level_model import ProgressLevelModel

class MissionProgressLevelModel(ProgressLevelModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MissionProgressLevelModel, self).__init__(properties=properties, commands=commands)

    def getTotal(self):
        return self._getNumber(3)

    def setTotal(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(MissionProgressLevelModel, self)._initialize()
        self._addNumberProperty('total', 0)
