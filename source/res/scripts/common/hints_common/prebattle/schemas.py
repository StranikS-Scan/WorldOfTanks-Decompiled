# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/hints_common/prebattle/schemas.py
import typing
from base_schema_manager import GameParamsSchema
from constants import ARENA_BONUS_TYPE_IDS
from dict2model import fields, models, validate
from dict2model.fields import String
from dict2model.schemas import Schema
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType
    from dict2model.fields import Field

class BaseHintModel(models.Model):
    __slots__ = ('hintType', 'viewClass')
    _VIEW_CLASS_DELIMITER = ':'

    def __init__(self, hintType, viewClass):
        super(BaseHintModel, self).__init__()
        self.hintType = hintType
        self.viewClass = viewClass

    def isEnabledFor(self, arenaBonusType):
        raise NotImplementedError

    def splitViewClass(self):
        return self.viewClass.split(self._VIEW_CLASS_DELIMITER)

    def _reprArgs(self):
        return 'hintType={}, viewClass={}'.format(self.hintType, self.viewClass)


_BHMType = typing.TypeVar('_BHMType', bound=BaseHintModel)

class BaseHintSchema(Schema[_BHMType]):

    def __init__(self, fields, modelClass, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        if not issubclass(modelClass, BaseHintModel):
            raise SoftException('modelClass should be a subclass of BaseHintModel')
        baseFields = {'hintType': String(required=True, default='', deserializedValidators=[validate.Length(minValue=1, maxValue=100)]),
         'viewClass': String(required=False, default='')}
        baseFields.update(fields)
        super(BaseHintSchema, self).__init__(fields=baseFields, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators, modelClass=modelClass)

    def validateRegistered(self, hints):
        pass


class HintModel(BaseHintModel):
    __slots__ = ('arenaBonusTypes',)

    def __init__(self, arenaBonusTypes, hintType, viewClass):
        super(HintModel, self).__init__(hintType, viewClass)
        self.arenaBonusTypes = arenaBonusTypes

    def isEnabledFor(self, arenaBonusType):
        return arenaBonusType in self.arenaBonusTypes


class HintSchema(BaseHintSchema[HintModel]):

    def __init__(self):
        super(HintSchema, self).__init__(fields={'arenaBonusTypes': fields.List(required=True, fieldOrSchema=fields.Integer(deserializedValidators=[validate.OneOf(ARENA_BONUS_TYPE_IDS.keys())]))}, checkUnknown=True, modelClass=HintModel)


hintSchema = HintSchema()

class PrebattleHintsConfigModel(models.Model):
    __slots__ = ('enabled', 'battleTimerThreshold')

    def __init__(self, enabled, battleTimerThreshold):
        super(PrebattleHintsConfigModel, self).__init__()
        self.enabled = enabled
        self.battleTimerThreshold = battleTimerThreshold

    def _reprArgs(self):
        return 'enabled={}, battleTimerThreshold={}'.format(self.enabled, self.battleTimerThreshold)


configSchema = GameParamsSchema[PrebattleHintsConfigModel](gameParamsKey='prebattle_hints_config', fields={'enabled': fields.Boolean(required=True),
 'battleTimerThreshold': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=0))}, modelClass=PrebattleHintsConfigModel)
