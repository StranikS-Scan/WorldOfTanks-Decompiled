# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/configs/halloween_anomalies.py
from __future__ import absolute_import
from game_params_common.base_manager import GameParamsSchema
from dict2model import models, fields, schemas, exceptions
from halloween_common.halloween_constants import HALLOWEEN_ANOMALIES_PARAMS_KEY, AnomalyType, ALL_LOOT_ANOMALY_TYPES
from game_params_common.scope import GameParamsScopeFlags

class AnomalyModel(models.Model):
    __slots__ = ('id', 'type', 'weight', 'components')

    def __init__(self, id, type, weight, components):
        super(AnomalyModel, self).__init__()
        self.id = id
        self.type = type
        self.weight = weight
        self.components = components


class RecipeModel(models.Model):
    __slots__ = ('id', 'ingredients', 'weightInc')

    def __init__(self, id, ingredients, weightInc):
        super(RecipeModel, self).__init__()
        self.id = id
        self.ingredients = ingredients
        self.weightInc = weightInc


class ComponentModel(models.Model):
    __slots__ = ('id', 'amount', 'spec')

    def __init__(self, id, amount, spec):
        super(ComponentModel, self).__init__()
        self.id = id
        self.amount = amount
        self.spec = spec


class AnomaliesModel(models.Model):
    __slots__ = ('anomaly',)

    def __init__(self, anomaly):
        super(AnomaliesModel, self).__init__()
        self.anomaly = anomaly


class RecipesModel(models.Model):
    __slots__ = ('recipe',)

    def __init__(self, recipe):
        super(RecipesModel, self).__init__()
        self.recipe = recipe


class ComponentsModel(models.Model):
    __slots__ = ('component',)

    def __init__(self, component):
        super(ComponentsModel, self).__init__()
        self.component = component


class AnomaliesConfigModel(models.Model):
    __slots__ = ('reduceFactor', 'anomalies', 'recipes')

    def __init__(self, reduceFactor, anomalies, recipes):
        super(AnomaliesConfigModel, self).__init__()
        self.reduceFactor = reduceFactor
        self.anomalies = anomalies
        self.recipes = recipes


componentSchema = schemas.Schema(fields={'id': fields.String(required=True),
 'amount': fields.Integer(required=False),
 'spec': fields.String(required=False)}, modelClass=ComponentModel, checkUnknown=True)
componentsSchema = schemas.Schema(fields={'component': fields.UniCapList(fieldOrSchema=componentSchema, required=True)}, modelClass=ComponentsModel, checkUnknown=True)
anomalySchema = schemas.Schema(fields={'id': fields.String(required=True),
 'type': fields.String(required=True),
 'weight': fields.Integer(required=True, filterParams=GameParamsScopeFlags.CELL_ARENA),
 'components': fields.Nested(schema=componentsSchema, filterParams=GameParamsScopeFlags.CELL_ARENA, required=True)}, modelClass=AnomalyModel, checkUnknown=True)
anomaliesSchema = schemas.Schema(fields={'anomaly': fields.UniCapList(fieldOrSchema=anomalySchema, required=True)}, modelClass=AnomaliesModel, checkUnknown=True)
recipeSchema = schemas.Schema(fields={'id': fields.String(required=True),
 'ingredients': fields.ListFromString(field=fields.String(), required=True),
 'weightInc': fields.ListFromString(field=fields.Integer(), required=True)}, modelClass=RecipeModel, checkUnknown=True)
recipesSchema = schemas.Schema(fields={'recipe': fields.UniCapList(fieldOrSchema=recipeSchema, required=True)}, modelClass=RecipesModel, checkUnknown=True)
_INGREDIENT_TYPES = (AnomalyType.REGULAR, AnomalyType.EPIC)
_KNOWN_TYPES = ALL_LOOT_ANOMALY_TYPES + _INGREDIENT_TYPES

def _validateAnomaliesConfig(config):
    anomalyProblems = []
    factorProblems = []
    recipeProblems = []
    typeByID = {}
    for anomaly in config.anomalies.anomaly:
        if anomaly.id in typeByID:
            anomalyProblems.append('"%s": declared more than once - the last declaration wins, remove the duplicates' % (anomaly.id,))
        if anomaly.type not in _KNOWN_TYPES:
            anomalyProblems.append('"%s": unknown type "%s" - expected %s' % (anomaly.id, anomaly.type, '/'.join(_KNOWN_TYPES)))
        if anomaly.weight <= 0:
            anomalyProblems.append('"%s": weight is %s, it can never be picked - set it above 0 or remove it' % (anomaly.id, anomaly.weight))
        typeByID[anomaly.id] = anomaly.type

    if not 0 < config.reduceFactor <= 1:
        factorProblems.append('must be above 0 and not above 1, got %s' % (config.reduceFactor,))
    fromRecipes = set()
    for recipe in config.recipes.recipe:
        fromRecipes.add(recipe.id)
        fromRecipes.update(recipe.ingredients)
        if recipe.id not in typeByID:
            recipeProblems.append('"%s": no anomaly with this id - completing the recipe silently gives no buff' % (recipe.id,))
        if not recipe.weightInc:
            recipeProblems.append('"%s": weightInc is empty - picking up an ingredient of this recipe breaks the battle' % (recipe.id,))
        for ingredient in recipe.ingredients:
            if ingredient not in typeByID:
                recipeProblems.append('"%s": ingredient "%s" has no anomaly with this id - offering this recipe breaks the battle' % (recipe.id, ingredient))
            if typeByID[ingredient] not in _INGREDIENT_TYPES:
                recipeProblems.append('"%s": ingredient "%s" is "%s", must be %s - offering this recipe breaks the battle' % (recipe.id,
                 ingredient,
                 typeByID[ingredient],
                 '/'.join(_INGREDIENT_TYPES)))

    for anomaly in config.anomalies.anomaly:
        if anomaly.type not in ALL_LOOT_ANOMALY_TYPES and anomaly.id not in fromRecipes:
            anomalyProblems.append('"%s": nothing gives it to a player (not individual/secret loot, no recipe uses it), so reduceFactor never applies' % (anomaly.id,))

    error = None
    for section, found in (('anomalies', anomalyProblems), ('reduceFactor', factorProblems), ('recipes', recipeProblems)):
        if found:
            msg = exceptions.ValidationErrorMessage(found, title=section)
            error = error + msg if error else msg

    if error:
        raise exceptions.ValidationError(exceptions.ValidationErrorMessage(error.data, title=HALLOWEEN_ANOMALIES_PARAMS_KEY))
    return


anomaliesConfigSchema = GameParamsSchema[AnomaliesConfigModel](gameParamsKey=HALLOWEEN_ANOMALIES_PARAMS_KEY, deserializedValidators=_validateAnomaliesConfig, fields={'reduceFactor': fields.Float(required=True, filterParams=GameParamsScopeFlags.CELL_ARENA),
 'anomalies': fields.Nested(schema=anomaliesSchema, required=True),
 'recipes': fields.Nested(schema=recipesSchema, required=True)}, modelClass=AnomaliesConfigModel, checkUnknown=True, usedInReplay=True)
