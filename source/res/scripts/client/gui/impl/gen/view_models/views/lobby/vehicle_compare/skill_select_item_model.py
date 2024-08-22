# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/skill_select_item_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SkillState(Enum):
    DEFAULT = 'default'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class SkillType(Enum):
    MAJOR = 'major'
    COMMON = 'common'
    BONUS = 'bonus'


class SkillSelectItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SkillSelectItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getState(self):
        return SkillState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(SkillSelectItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('state')
