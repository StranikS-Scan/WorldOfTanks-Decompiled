# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/skill_select_item_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_simple_model import SkillSimpleModel

class SkillState(Enum):
    DEFAULT = 'default'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class SkillType(Enum):
    MAJOR = 'major'
    COMMON = 'common'
    BONUS = 'bonus'


class SkillSelectItemModel(SkillSimpleModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SkillSelectItemModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return SkillState(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(SkillSelectItemModel, self)._initialize()
        self._addStringProperty('state')
