# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/game_params_common/schema.py
import typing
from constants import IS_CLIENT, IS_BASEAPP, IS_CELLAPP
from dict2model.fields import Field
from dict2model.schemas import Schema, SchemaModelType
from dict2model.types import SchemaModelClassesType, ValidatorsType
if typing.TYPE_CHECKING:
    from section2dict import TReaders

class GameParamsSchema(Schema[SchemaModelType]):
    __slots__ = ('readers', 'usedInReplay', '_gameParamsKey')

    def __init__(self, gameParamsKey, fields, modelClass=dict, checkUnknown=True, serializedValidators=None, deserializedValidators=None, readers=None, usedInReplay=False):
        super(GameParamsSchema, self).__init__(fields=fields, modelClass=modelClass, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self.readers = readers
        self.usedInReplay = usedInReplay
        self._gameParamsKey = gameParamsKey

    @property
    def gpKey(self):
        return self._gameParamsKey

    def getModel(self, **kwargs):
        if not IS_CLIENT and not IS_BASEAPP and not IS_CELLAPP:
            raise NotImplementedError
        from schema_manager import getSchemaManager
        return getSchemaManager().getModel(self, **kwargs)
