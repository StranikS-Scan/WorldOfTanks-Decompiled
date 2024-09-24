# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/sounds_schema.py
import typing
from dict2model import models
from dict2model.schemas import Schema
from dict2model.fields import String
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType
    from dict2model.fields import Field

class SoundModel(models.Model):
    __slots__ = ('start', 'stop', 'group', 'state')

    def __init__(self, start, stop, group, state):
        super(SoundModel, self).__init__()
        self.start = start
        self.stop = stop
        self.group = group
        self.state = state

    def __repr__(self):
        return '<SoundModel(start={}, stop={}, group={}, state={})>'.format(self.start, self.stop, self.group, self.state)


_SoundModelType = typing.TypeVar('_SoundModelType', bound=SoundModel)

class SoundSchema(Schema[_SoundModelType]):

    def __init__(self, fields=None, modelClass=SoundModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        if not issubclass(modelClass, SoundModel):
            raise SoftException('modelClass should be a subclass of SoundModel')
        baseFields = {'start': String(required=False, default=''),
         'stop': String(required=False, default=''),
         'group': String(required=False, default=''),
         'state': String(required=False, default='')}
        if fields is not None:
            baseFields.update(fields)
        super(SoundSchema, self).__init__(fields=baseFields, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators, modelClass=modelClass)
        return


soundSchema = SoundSchema()
