# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/config_schemas/umg.py
from base_schema_manager import GameParamsSchema
from dict2model import fields, models, schemas, validate, exceptions
import typing

class WeightModel(models.Model):
    __slots__ = ('name', 'weight')

    def __init__(self, name, weight):
        super(WeightModel, self).__init__()
        self.name = name
        self.weight = weight

    def _reprArgs(self):
        return 'name={}, weight={}'.format(self.name, self.weight)


class WeightsModel(models.Model):
    __slots__ = ('weights', '_weightByName')

    def __init__(self, weights):
        super(WeightsModel, self).__init__()
        self.weights = weights
        self._weightByName = {p.name:p for p in self.weights}

    def getWeightByName(self, name):
        return self._weightByName.get(name, None)

    def _reprArgs(self):
        return 'weights={}'.format(self.weights)


def checkUniqNames(models):
    names = set()
    duplicates = set()
    for model in models:
        if model.name in names:
            duplicates.add(model.name)
        names.add(model.name)

    if duplicates:
        raise exceptions.ValidationError('Duplicate names: {}'.format(duplicates))


_weightSchema = schemas.Schema[WeightModel](modelClass=WeightModel, fields={'name': fields.String(deserializedValidators=validate.Length(minValue=2)),
 'weight': fields.Integer(deserializedValidators=validate.Range(0, 1000))})
umgMissionsConfigSchema = GameParamsSchema[WeightsModel](gameParamsKey='umgMissions', modelClass=WeightsModel, fields={'weights': fields.UniCapList(fieldOrSchema=_weightSchema, deserializedValidators=[validate.Length(minValue=1), checkUniqNames])})
umgEventsConfigSchema = GameParamsSchema[WeightsModel](gameParamsKey='umgEvents', modelClass=WeightsModel, fields={'weights': fields.UniCapList(fieldOrSchema=_weightSchema, deserializedValidators=[validate.Length(minValue=1), checkUniqNames])})
