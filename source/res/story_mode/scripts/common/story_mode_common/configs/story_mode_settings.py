# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/story_mode_settings.py
import typing
from base_schema_manager import GameParamsSchema
from dict2model import models, fields, validate, schemas
if typing.TYPE_CHECKING:
    import datetime

class EntryPointSettingsModel(models.Model):
    __slots__ = ('eventStartAt', 'eventEndAt')

    def __init__(self, eventStartAt, eventEndAt):
        super(EntryPointSettingsModel, self).__init__()
        self.eventStartAt = eventStartAt
        self.eventEndAt = eventEndAt

    def __repr__(self):
        return '<EntryPointSettingsModel(eventStartAt={}, eventEndAt={})>'.format(self.eventStartAt, self.eventEndAt)


class SettingsModel(models.Model):
    __slots__ = ('enabled', 'waitTimeQueue', 'hideGameLoadingTimeout', 'joinToQueueFromLogin', 'afk', 'entryPoint', 'isModeSelectorCardBig', 'newbieBannerEnabled')

    def __init__(self, enabled, waitTimeQueue, hideGameLoadingTimeout, joinToQueueFromLogin, afk, entryPoint, isModeSelectorCardBig, newbieBannerEnabled):
        super(SettingsModel, self).__init__()
        self.enabled = enabled
        self.waitTimeQueue = waitTimeQueue
        self.hideGameLoadingTimeout = hideGameLoadingTimeout
        self.joinToQueueFromLogin = joinToQueueFromLogin
        self.afk = afk
        self.entryPoint = entryPoint
        self.isModeSelectorCardBig = isModeSelectorCardBig
        self.newbieBannerEnabled = newbieBannerEnabled

    def __repr__(self):
        return '<SettingsModel(enabled={}, waitTimeQueue={}, hideGameLoadingTimeout={}, joinToQueueFromLogin={}, afk={}, entryPoint={}, isModeSelectorCardBig={}, newbieBannerEnabled={}>'.format(self.enabled, self.waitTimeQueue, self.hideGameLoadingTimeout, self.joinToQueueFromLogin, self.afk, self.entryPoint, self.isModeSelectorCardBig, self.newbieBannerEnabled)


class AfkModel(models.Model):
    __slots__ = ('maxPlayerInactiveTime', 'arenaWaitPlayerTime')

    def __init__(self, maxPlayerInactiveTime, arenaWaitPlayerTime):
        super(AfkModel, self).__init__()
        self.maxPlayerInactiveTime = maxPlayerInactiveTime
        self.arenaWaitPlayerTime = arenaWaitPlayerTime

    def __repr__(self):
        return '<AfkModel(maxPlayerInactiveTime={}, arenaWaitPlayerTime={})>'.format(self.maxPlayerInactiveTime, self.arenaWaitPlayerTime)


class AfkModesModel(models.Model):
    __slots__ = ('onboarding', 'regular')

    def __init__(self, onboarding, regular):
        super(AfkModesModel, self).__init__()
        self.onboarding = onboarding
        self.regular = regular

    def __repr__(self):
        return '<AfkModesModel(onboarding={}, regular={})>'.format(self.onboarding, self.regular)


_bannerSettingsSchema = schemas.Schema(fields={'eventStartAt': fields.DateTime(),
 'eventEndAt': fields.DateTime()}, modelClass=EntryPointSettingsModel)
afkSchema = schemas.Schema(fields={'maxPlayerInactiveTime': fields.Integer(public=False, required=True, deserializedValidators=validate.Range(minValue=1)),
 'arenaWaitPlayerTime': fields.Integer(public=False, required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=AfkModel, checkUnknown=True)
afkModesSchema = schemas.Schema(fields={'onboarding': fields.Nested(schema=afkSchema, required=True, public=False),
 'regular': fields.Nested(schema=afkSchema, required=True, public=False)}, modelClass=AfkModesModel, checkUnknown=True)
settingsSchema = GameParamsSchema[SettingsModel](gameParamsKey='story_mode_settings', fields={'enabled': fields.Boolean(required=True),
 'waitTimeQueue': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'hideGameLoadingTimeout': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'joinToQueueFromLogin': fields.Boolean(required=True, public=False),
 'isModeSelectorCardBig': fields.Boolean(required=True),
 'afk': fields.Nested(schema=afkModesSchema, required=True, public=False),
 'entryPoint': fields.Nested(schema=_bannerSettingsSchema),
 'newbieBannerEnabled': fields.Boolean(required=True)}, modelClass=SettingsModel, checkUnknown=True)
