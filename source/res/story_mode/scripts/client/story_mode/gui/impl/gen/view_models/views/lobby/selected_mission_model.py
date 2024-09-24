# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/selected_mission_model.py
from story_mode.gui.impl.gen.view_models.views.lobby.mission_model import MissionModel

class SelectedMissionModel(MissionModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(SelectedMissionModel, self).__init__(properties=properties, commands=commands)

    def getIsCountdownVisible(self):
        return self._getBool(5)

    def setIsCountdownVisible(self, value):
        self._setBool(5, value)

    def getSecondsCountdown(self):
        return self._getNumber(6)

    def setSecondsCountdown(self, value):
        self._setNumber(6, value)

    def getBattlesToUnlock(self):
        return self._getNumber(7)

    def setBattlesToUnlock(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(SelectedMissionModel, self)._initialize()
        self._addBoolProperty('isCountdownVisible', False)
        self._addNumberProperty('secondsCountdown', 0)
        self._addNumberProperty('battlesToUnlock', 0)
