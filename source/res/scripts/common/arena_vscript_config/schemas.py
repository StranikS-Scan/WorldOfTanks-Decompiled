# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/arena_vscript_config/schemas.py
import typing
from constants import IS_CLIENT
from dict2model import fields, models, validate
from dict2model.extensions.battle_type import BattleTypesModel, BattleTypesSchema
from dict2model.schemas import Schema
from visual_script.misc import ASPECT
if typing.TYPE_CHECKING:
    from dict2model.extensions.battle_type import BattleTypeModel

def _getCurrentAspect():
    return ASPECT.CLIENT if IS_CLIENT else ASPECT.SERVER


class VScriptParamModel(models.Model):
    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        super(VScriptParamModel, self).__init__()
        self.name = name
        self.value = value

    def _reprArgs(self):
        return 'name={}, value={}'.format(self.name, self.value)


_vscriptParamSchema = Schema[VScriptParamModel](fields={'name': fields.NonEmptyString(required=True),
 'value': fields.UniCapList(fields.NonEmptyString(), required=True)}, modelClass=VScriptParamModel, checkUnknown=True)

class VScriptModel(models.Model):
    __slots__ = ('name', 'planId', 'param')

    def __init__(self, name, planId, param):
        super(VScriptModel, self).__init__()
        self.name = name
        self.planId = planId
        self.param = param

    def _reprArgs(self):
        return 'name={}, param={}, planId={}'.format(self.name, self.param, self.planId)


_vscriptSchema = Schema[VScriptModel](fields={'name': fields.NonEmptyString(required=True),
 'planId': fields.String(required=False, default=''),
 'param': fields.UniCapList(_vscriptParamSchema, required=False, default=list)}, modelClass=VScriptModel, checkUnknown=True)

class AspectVScriptsModel(models.Model):
    __slots__ = ('plan',)

    def __init__(self, plan):
        super(AspectVScriptsModel, self).__init__()
        self.plan = plan

    def _reprArgs(self):
        return 'plan={}'.format(self.plan)


_aspectVScriptSchema = Schema[AspectVScriptsModel](fields={'plan': fields.UniCapList(_vscriptSchema, required=True)}, modelClass=AspectVScriptsModel, checkUnknown=True)

class ArenaVScriptsModel(BattleTypesModel):
    __slots__ = ('client', 'server', '_plans')

    def __init__(self, client, server, battleTypes):
        super(ArenaVScriptsModel, self).__init__(battleTypes)
        self.client = client
        self.server = server
        self._plans = {}
        self._preparePlansForLoader()

    def getPlansForLoader(self, aspect):
        return self._plans.get(aspect, [])

    def _preparePlansForLoader(self):
        aspect = _getCurrentAspect()
        self._plans[aspect] = [ {'name': vscript.name,
         'params': {param.name:(param.value[0] if len(param.value) == 1 else list(param.value)) for param in vscript.param},
         'plan_id': vscript.planId} for vscript in (self.client if aspect == ASPECT.CLIENT else self.server).plan ]

    def _reprArgs(self):
        return '{}, client={}, server={}'.format(super(ArenaVScriptsModel, self)._reprArgs(), self.client, self.server)


def _validateAnyPlanGiven(model):
    if not model.server.plan and not model.client.plan:
        raise validate.ValidationError('At least one plan(client or server) must be defined.')


def _defaultAspectVScriptModel():
    return AspectVScriptsModel([])


_arenaVScriptSchema = BattleTypesSchema[ArenaVScriptsModel](fields={'client': fields.Nested(_aspectVScriptSchema, required=False, default=_defaultAspectVScriptModel),
 'server': fields.Nested(_aspectVScriptSchema, required=False, default=_defaultAspectVScriptModel)}, modelClass=ArenaVScriptsModel, checkUnknown=True, deserializedValidators=_validateAnyPlanGiven)

class ConfigModel(models.Model):
    __slots__ = ('visualScript',)

    def __init__(self, visualScript):
        super(ConfigModel, self).__init__()
        self.visualScript = visualScript

    def getPlansForLoader(self, aspect, arenaBonusType, gameplayName):
        plans = []
        for vscript in self.visualScript:
            if vscript.isSuitableForBattleType(arenaBonusType, gameplayName):
                plans.extend(vscript.getPlansForLoader(aspect))

        return plans


configSchema = Schema[ConfigModel](fields={'visualScript': fields.UniCapList(_arenaVScriptSchema, required=False, default=list)}, modelClass=ConfigModel, checkUnknown=True)
