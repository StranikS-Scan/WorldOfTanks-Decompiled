# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/hints_common/battle/schemas/base.py
import typing
import logging
from dict2model import models
from dict2model import fields
from dict2model import validate
from dict2model import schemas
from dict2model import exceptions
from dict2model.extensions.battle_type import BattleTypeModel, BattleTypesModel, BattleTypesSchema
from hints_common.battle.schemas.const import DEFAULT_PRIORITY, DEFAULT_COMPONENT, DEFAULT_SCOPE, RESERVED_SCOPES, MAX_PRIORITY
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType
_logger = logging.getLogger(__name__)

class SchemaDependentModel(models.Model):
    __slots__ = ()

    def prepare(self, schema, **kwargs):
        try:
            return self._prepare(schema, **kwargs)
        except exceptions.ValidationError:
            raise
        except Exception as error:
            raise exceptions.ValidationError('Model preparation error: {}'.format(error))

    def _prepare(self, schema, **kwargs):
        pass


class CommonHintPropsModel(BattleTypesModel):
    __slots__ = ('name', 'scope', 'component', 'unique', 'priority', '_uniqueName')

    def __init__(self, name, scope, component, unique, priority, battleTypes):
        super(CommonHintPropsModel, self).__init__(battleTypes)
        self.name = name
        self.scope = scope
        self.component = component
        self.unique = unique
        self.priority = priority
        self._uniqueName = '{}.{}'.format(scope, name) if scope else name

    @property
    def uniqueName(self):
        return self._uniqueName

    def _reprArgs(self):
        return '{}, name={}, component={}, unique={}, priority={}'.format(super(CommonHintPropsModel, self)._reprArgs(), self.uniqueName, self.component, self.unique, self.priority)


class CommonHintContextModel(SchemaDependentModel):
    __slots__ = ('_ctx',)

    def __init__(self, *args, **kwargs):
        super(CommonHintContextModel, self).__init__(*args, **kwargs)
        self._ctx = {}

    def create(self, data):
        return dict(self._ctx)

    def _prepare(self, schema, **kwargs):
        self._ctx = schema.serialize(self, silent=False)

    def _reprArgs(self):
        return 'ctx={}'.format(self._ctx)


HMCPropsType = typing.TypeVar('HMCPropsType', bound=CommonHintPropsModel)
HMCContextType = typing.TypeVar('HMCContextType', bound=CommonHintContextModel)

class CommonHintModel(SchemaDependentModel, typing.Generic[HMCPropsType, HMCContextType]):
    __slots__ = ('props', 'context')

    def __init__(self, props, context):
        super(CommonHintModel, self).__init__()
        self.props = props
        self.context = context

    @property
    def uniqueName(self):
        return self.props.uniqueName

    def validate(self, arenaBonusType, gameplayName, *args, **kwargs):
        return self.props.isSuitableForBattleType(arenaBonusType, gameplayName)

    def _prepare(self, schema, **kwargs):
        if self.context:
            self.context.prepare(schema.contextSchema, **kwargs)

    def _reprArgs(self):
        return 'props={}, ctx={}'.format(self.props, self.context)


HMCType = typing.TypeVar('HMCType', bound=CommonHintModel)

def validateCommonHintPropsModel(model):
    arenaBonusTypes = {bt.arenaBonusType for bt in model.battleTypes}
    if len(model.battleTypes) != len(arenaBonusTypes):
        raise exceptions.ValidationError('Arena bonus types should be unique.')


class CommonHintPropsSchema(BattleTypesSchema[HMCPropsType]):
    __slots__ = ()

    def __init__(self, modelClass=CommonHintPropsModel, serializedValidators=None, deserializedValidators=None):
        super(CommonHintPropsSchema, self).__init__(fields={'name': fields.String(required=True, deserializedValidators=validate.Length(minValue=1, maxValue=50)),
         'scope': fields.String(required=False, default=DEFAULT_SCOPE, deserializedValidators=[validate.Length(minValue=1, maxValue=50), validate.NoneOf(RESERVED_SCOPES)]),
         'priority': fields.Integer(required=False, default=DEFAULT_PRIORITY, deserializedValidators=validate.Range(minValue=0, maxValue=MAX_PRIORITY)),
         'component': fields.String(required=False, default=DEFAULT_COMPONENT, deserializedValidators=validate.Length(minValue=1, maxValue=50)),
         'unique': fields.Boolean(required=False, default=False)}, checkUnknown=False, serializedValidators=serializedValidators, deserializedValidators=[validateCommonHintPropsModel] + validate.prepareValidators(deserializedValidators), modelClass=modelClass)


commonHintPropsSchema = CommonHintPropsSchema()
commonHintContextSchema = schemas.Schema[CommonHintContextModel](fields={}, checkUnknown=False, modelClass=CommonHintContextModel)

class CommonHintSchema(schemas.Schema[HMCType]):
    __slots__ = ('propsSchema', 'contextSchema')

    def __init__(self, modelClass=CommonHintModel, propsSchema=None, contextSchema=None, serializedValidators=None, deserializedValidators=None):
        self.propsSchema = propsSchema or commonHintPropsSchema
        self.contextSchema = contextSchema or commonHintContextSchema
        super(CommonHintSchema, self).__init__(fields={'props': fields.Nested(required=True, schema=self.propsSchema),
         'context': fields.Nested(required=False, schema=self.contextSchema, default=None)}, checkUnknown=False, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators, modelClass=modelClass)
        return
