# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/hints_common/prebattle/newbie/schemas.py
from operator import attrgetter
import typing
from dict2model.exceptions import ValidationErrorMessage, ValidationError
from hints_common.prebattle.newbie.consts import BATTLES_TYPES, HINT_TYPE_PREFIX
from hints_common.prebattle.schemas import BaseHintModel, BaseHintSchema
from base_schema_manager import GameParamsSchema
from dict2model import models, fields, validate

class NewbieHintModel(BaseHintModel):
    __slots__ = ('displayOrder',)

    def __init__(self, hintType, viewClass, displayOrder):
        super(NewbieHintModel, self).__init__(hintType, viewClass)
        self.displayOrder = displayOrder

    def isEnabledFor(self, arenaBonusType):
        return arenaBonusType in BATTLES_TYPES

    def _reprArgs(self):
        return '{}, displayOrder={}'.format(super(NewbieHintModel, self)._reprArgs(), self.displayOrder)


class NewbieHintSchema(BaseHintSchema[NewbieHintModel]):
    __slots__ = ('hints',)

    def __init__(self):
        super(NewbieHintSchema, self).__init__(fields={'displayOrder': fields.Integer(required=True)}, modelClass=NewbieHintModel)
        self.hints = []

    def validateRegistered(self, hints):
        self.hints = []
        displayOrder = set()
        hintTypes = set()
        for hint in hints:
            if isinstance(hint, NewbieHintModel):
                if hint.displayOrder in displayOrder:
                    raise ValidationError(ValidationErrorMessage(data='Duplicate displayOrder: {}'.format(hint)))
                if hint.hintType in hintTypes:
                    raise ValidationError(ValidationErrorMessage(data='Duplicate hintType: {}'.format(hint)))
                try:
                    prefix, number = hint.hintType.split(HINT_TYPE_PREFIX)
                    number = int(number)
                except:
                    raise ValidationError(ValidationErrorMessage(data='Invalid hintType: {}'.format(hint)))

                if number < 1 or prefix:
                    raise ValidationError(ValidationErrorMessage(data='Invalid hintType: {}'.format(hint)))
                displayOrder.add(hint.displayOrder)
                hintTypes.add(hint.hintType)
                self.hints.append(hint)

        self.hints.sort(key=attrgetter('displayOrder'))


hintSchema = NewbieHintSchema()

class NewbiePrebattleHintsConfigModel(models.Model):
    __slots__ = ('enabled', 'hintDisplayCount')

    def __init__(self, enabled, hintDisplayCount):
        super(NewbiePrebattleHintsConfigModel, self).__init__()
        self.enabled = enabled
        self.hintDisplayCount = hintDisplayCount

    def _reprArgs(self):
        return 'enabled={}, hintDisplayCount={}'.format(self.enabled, self.hintDisplayCount)


configSchema = GameParamsSchema[NewbiePrebattleHintsConfigModel](gameParamsKey='newbie_prebattle_hints_config', fields={'enabled': fields.Boolean(required=True),
 'hintDisplayCount': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=NewbiePrebattleHintsConfigModel)
