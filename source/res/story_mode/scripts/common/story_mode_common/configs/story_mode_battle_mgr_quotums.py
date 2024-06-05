# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/story_mode_battle_mgr_quotums.py
from base_schema_manager import GameParamsSchema
from dict2model import models, fields, validate, schemas, exceptions
from story_mode_common.story_mode_constants import PRIORITY

class QuotumsModel(models.Model):
    __slots__ = ('quotums',)

    def __init__(self, quotums):
        super(QuotumsModel, self).__init__()
        self.quotums = quotums

    def __repr__(self):
        return '<QuotumsModel(quotums={})>'.format(self.quotums)


class QuotumModel(models.Model):
    __slots__ = ('priority', 'quotum')

    def __init__(self, priority, quotum):
        super(QuotumModel, self).__init__()
        self.priority = priority
        self.quotum = quotum

    def __repr__(self):
        return '<QuotumModel(priority={}, quotum={})>'.format(self.priority, self.quotum)


def validatePriorityies(model):
    priorities, duplicates = set(), set()
    for q in model.quotums:
        if q.priority not in priorities:
            priorities.add(q.priority)
        duplicates.add(q.priority)

    if duplicates:
        raise exceptions.ValidationError('Priority duplicates: {}'.format(duplicates))


quotumSchema = schemas.Schema[QuotumModel](fields={'priority': fields.Enum(PRIORITY, required=True, deserializedValidators=validate.Range(minValue=0)),
 'quotum': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=0))}, modelClass=QuotumModel, checkUnknown=True)
quotumsSchema = GameParamsSchema(gameParamsKey='story_mode_battle_mgr_quotums', fields={'quotums': fields.UniCapList(fieldOrSchema=quotumSchema, required=True, deserializedValidators=validate.Length(minValue=3))}, modelClass=QuotumsModel, checkUnknown=True, deserializedValidators=[validatePriorityies])
