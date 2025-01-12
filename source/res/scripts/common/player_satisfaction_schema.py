# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/player_satisfaction_schema.py
from base_schema_manager import GameParamsSchema
from constants import Configs
from dict2model import fields, models
from dict2model.schemas import Schema

class _InterfacesModel(models.Model):
    __slots__ = ('postbattle', 'spectatorMode')

    def __init__(self, postbattle, spectatorMode):
        super(_InterfacesModel, self).__init__()
        self.postbattle = postbattle
        self.spectatorMode = spectatorMode

    def _reprArgs(self):
        return 'postbattle={}, spectatorMode={}'.format(self.postbattle, self.spectatorMode)


_interfacesSchema = Schema[_InterfacesModel](fields={'postbattle': fields.Boolean(required=False, default=False),
 'spectatorMode': fields.Boolean(required=False, default=False)}, modelClass=_InterfacesModel, checkUnknown=True)

class PlayerSatisfactionConfigModel(models.Model):
    __slots__ = ('enabled', 'enabledInterfaces', 'randomizedFeedbackText')

    def __init__(self, enabled, enabledInterfaces, randomizedFeedbackText):
        super(PlayerSatisfactionConfigModel, self).__init__()
        self.enabled = enabled
        self.enabledInterfaces = enabledInterfaces
        self.randomizedFeedbackText = randomizedFeedbackText

    def _reprArgs(self):
        return 'enabled={}, enabledInterfaces={}, randomizedFeedbackText={}'.format(self.enabled, self.enabledInterfaces, self.randomizedFeedbackText)


playerSatisfactionSchema = GameParamsSchema[PlayerSatisfactionConfigModel](gameParamsKey=Configs.PLAYER_SATISFACTION_CONFIG.value, fields={'enabled': fields.Boolean(required=True),
 'enabledInterfaces': fields.Nested(_interfacesSchema, required=True),
 'randomizedFeedbackText': fields.Boolean(required=True)}, modelClass=PlayerSatisfactionConfigModel, checkUnknown=True)
