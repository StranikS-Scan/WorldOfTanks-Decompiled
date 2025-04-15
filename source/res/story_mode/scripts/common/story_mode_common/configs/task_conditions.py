# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/task_conditions.py
import enum
from dict2model import fields
from visual_script.slot_types import SLOT_TYPE

@enum.unique
class TaskConditionType(str, enum.Enum):
    INT = 'int'
    FLOAT = 'float'

    def getSchemaFieldType(self):
        return _VALUE_FIELD_BY_TYPE[self]

    def getVseSlotType(self):
        return _VSE_SLOT_BY_TYPE[self]


_VALUE_FIELD_BY_TYPE = {TaskConditionType.INT: fields.Integer(required=True),
 TaskConditionType.FLOAT: fields.Float(required=True)}
_VSE_SLOT_BY_TYPE = {TaskConditionType.INT: SLOT_TYPE.INT,
 TaskConditionType.FLOAT: SLOT_TYPE.FLOAT}
