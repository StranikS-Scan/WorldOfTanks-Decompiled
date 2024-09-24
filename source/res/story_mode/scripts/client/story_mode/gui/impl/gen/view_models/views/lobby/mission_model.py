# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MissionsDifficulty(Enum):
    UNDEFINED = ''
    NORMAL = 'normal'
    HARD = 'hard'


class MissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MissionModel, self).__init__(properties=properties, commands=commands)

    def getMissionId(self):
        return self._getNumber(0)

    def setMissionId(self, value):
        self._setNumber(0, value)

    def getDisplayName(self):
        return self._getString(1)

    def setDisplayName(self, value):
        self._setString(1, value)

    def getIsCompleted(self):
        return self._getBool(2)

    def setIsCompleted(self, value):
        self._setBool(2, value)

    def getLocked(self):
        return self._getBool(3)

    def setLocked(self, value):
        self._setBool(3, value)

    def getDifficulty(self):
        return MissionsDifficulty(self._getString(4))

    def setDifficulty(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(MissionModel, self)._initialize()
        self._addNumberProperty('missionId', 0)
        self._addStringProperty('displayName', '')
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('locked', False)
        self._addStringProperty('difficulty')
