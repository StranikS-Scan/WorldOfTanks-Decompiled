# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/progress_level_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class StatEnum(Enum):
    MISSIONS = 'missions'
    ASSIST = 'assist'
    KILLS = 'kills'
    DAMAGE = 'damage'
    ARMOR_USE = 'armorUse'


class ProgressLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ProgressLevelModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getResource(2)

    def setName(self, value):
        self._setResource(2, value)

    def getStat(self):
        return StatEnum(self._getString(3))

    def setStat(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(ProgressLevelModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addNumberProperty('value', 0)
        self._addResourceProperty('name', R.invalid())
        self._addStringProperty('stat')
