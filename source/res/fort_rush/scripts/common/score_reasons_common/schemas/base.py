# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/score_reasons_common/schemas/base.py
from __future__ import absolute_import
from typing import List
from dict2model import fields, models, schemas, validate

class ScoreReasonModel(models.Model):
    __slots__ = ('name',)

    def __init__(self, name):
        super(ScoreReasonModel, self).__init__()
        self.name = name

    def _reprArgs(self):
        return 'name={}'.format(self.name)


scoreReasonSchema = schemas.Schema[ScoreReasonModel](fields={'name': fields.String(required=True, deserializedValidators=validate.Length(minValue=1, maxValue=50))}, checkUnknown=False, modelClass=ScoreReasonModel)

class ScopeType(object):
    TEAM = 'team'
    VEHICLE = 'vehicle'


class ScopeModel(models.Model):
    __slots__ = ('scopeType', 'reason')

    def __init__(self, scopeType, reason):
        super(ScopeModel, self).__init__()
        self.scopeType = scopeType
        self.reason = reason

    def _reprArgs(self):
        return 'scopeType={}, reason={}'.format(self.scopeType, self.reason)


ScopeSchema = schemas.Schema[ScopeModel](fields={'scopeType': fields.String(required=True, deserializedValidators=validate.OneOf([ScopeType.TEAM, ScopeType.VEHICLE])),
 'reason': fields.UniCapList(fields.Nested(schema=scoreReasonSchema), required=False, default=[])}, checkUnknown=False, modelClass=ScopeModel)

class ExtensionModel(models.Model):
    __slots__ = ('name', 'scope')

    def __init__(self, name, scope):
        super(ExtensionModel, self).__init__()
        self.name = name
        self.scope = scope

    def _reprArgs(self):
        return 'name={}, scope={}'.format(self.name, self.scope)


ExtensionSchema = schemas.Schema[ExtensionModel](fields={'name': fields.String(required=True, deserializedValidators=validate.Length(minValue=1, maxValue=50)),
 'scope': fields.UniCapList(fields.Nested(schema=ScopeSchema), required=False, default=[])}, checkUnknown=False, modelClass=ExtensionModel)
