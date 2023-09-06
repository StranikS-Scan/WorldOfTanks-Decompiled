# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/story_mode_settings.py
from base_schema_manager import GameParamsSchema
from dict2model import models, fields, validate, schemas

class SettingsModel(models.Model):
    __slots__ = ('enabled', 'waitTimeQueue', 'hideGameLoadingTimeout', 'joinToQueueFromLogin', 'quotums', 'afk')

    def __init__(self, enabled, waitTimeQueue, hideGameLoadingTimeout, joinToQueueFromLogin, quotums, afk):
        super(SettingsModel, self).__init__()
        self.enabled = enabled
        self.waitTimeQueue = waitTimeQueue
        self.hideGameLoadingTimeout = hideGameLoadingTimeout
        self.joinToQueueFromLogin = joinToQueueFromLogin
        self.quotums = quotums
        self.afk = afk

    def __repr__(self):
        return '<SettingsModel(enabled={}, waitTimeQueue={}, hideGameLoadingTimeout={}, joinToQueueFromLogin={}, quotums={}), afk={}>'.format(self.enabled, self.waitTimeQueue, self.hideGameLoadingTimeout, self.joinToQueueFromLogin, self.quotums, self.afk)


class AfkModel(models.Model):
    __slots__ = ('maxPlayerInactiveTime', 'arenaWaitPlayerTime')

    def __init__(self, maxPlayerInactiveTime, arenaWaitPlayerTime):
        super(AfkModel, self).__init__()
        self.maxPlayerInactiveTime = maxPlayerInactiveTime
        self.arenaWaitPlayerTime = arenaWaitPlayerTime

    def __repr__(self):
        return '<AfkModel(maxPlayerInactiveTime={}, arenaWaitPlayerTime={})>'.format(self.maxPlayerInactiveTime, self.arenaWaitPlayerTime)


afkSchema = schemas.Schema(fields={'maxPlayerInactiveTime': fields.Integer(public=False, required=True, serializedValidators=validate.Range(minValue=1), deserializedValidators=validate.Range(minValue=1)),
 'arenaWaitPlayerTime': fields.Integer(public=False, required=True, serializedValidators=validate.Range(minValue=1), deserializedValidators=validate.Range(minValue=1))}, modelClass=AfkModel, checkUnknown=True)
settingsSchema = GameParamsSchema(gameParamsKey='story_mode_settings', fields={'enabled': fields.Boolean(required=True),
 'waitTimeQueue': fields.Integer(required=True, serializedValidators=validate.Range(minValue=1), deserializedValidators=validate.Range(minValue=1)),
 'hideGameLoadingTimeout': fields.Integer(required=True, serializedValidators=validate.Range(minValue=1), deserializedValidators=validate.Range(minValue=1)),
 'joinToQueueFromLogin': fields.Boolean(required=True, public=False),
 'quotums': fields.List(fieldOrSchema=fields.Integer(serializedValidators=validate.Range(minValue=1), deserializedValidators=validate.Range(minValue=1)), required=True, serializedValidators=validate.Length(minValue=3), deserializedValidators=validate.Length(minValue=3)),
 'afk': fields.Nested(schema=afkSchema, required=True, public=False)}, modelClass=SettingsModel, checkUnknown=True)
