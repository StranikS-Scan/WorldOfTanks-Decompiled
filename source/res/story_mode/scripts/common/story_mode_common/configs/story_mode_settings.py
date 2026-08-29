# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/story_mode_settings.py
from __future__ import absolute_import
import typing
from game_params_common.base_manager import GameParamsSchema
from dict2model import models, fields, validate, schemas
from game_params_common.scope import GameParamsScopeFlags
if typing.TYPE_CHECKING:
    import datetime

class EntryPointSettingsModel(models.Model):
    __slots__ = ('eventStartAt', 'eventEndAt')

    def __init__(self, eventStartAt, eventEndAt):
        super(EntryPointSettingsModel, self).__init__()
        self.eventStartAt = eventStartAt
        self.eventEndAt = eventEndAt


class SettingsModel(models.Model):
    __slots__ = ('enabled', 'waitTimeQueue', 'hideGameLoadingTimeout', 'joinToQueueFromLogin', 'afk', 'entryPoint', 'modeSelectorCardColumn', 'modeSelectorCardPriority', 'newbieBannerEnabled', 'newbieAdvertisingEnabled', 'parallaxEnabled', 'eventName')

    def __init__(self, enabled, waitTimeQueue, hideGameLoadingTimeout, joinToQueueFromLogin, afk, entryPoint, modeSelectorCardColumn, modeSelectorCardPriority, newbieBannerEnabled, newbieAdvertisingEnabled, parallaxEnabled, eventName):
        super(SettingsModel, self).__init__()
        self.enabled = enabled
        self.waitTimeQueue = waitTimeQueue
        self.hideGameLoadingTimeout = hideGameLoadingTimeout
        self.joinToQueueFromLogin = joinToQueueFromLogin
        self.afk = afk
        self.entryPoint = entryPoint
        self.modeSelectorCardColumn = modeSelectorCardColumn
        self.modeSelectorCardPriority = modeSelectorCardPriority
        self.newbieBannerEnabled = newbieBannerEnabled
        self.newbieAdvertisingEnabled = newbieAdvertisingEnabled
        self.parallaxEnabled = parallaxEnabled
        self.eventName = eventName


class AfkModel(models.Model):
    __slots__ = ('maxPlayerInactiveTime', 'arenaWaitPlayerTime')

    def __init__(self, maxPlayerInactiveTime, arenaWaitPlayerTime):
        super(AfkModel, self).__init__()
        self.maxPlayerInactiveTime = maxPlayerInactiveTime
        self.arenaWaitPlayerTime = arenaWaitPlayerTime


class AfkModesModel(models.Model):
    __slots__ = ('onboarding', 'regular')

    def __init__(self, onboarding, regular):
        super(AfkModesModel, self).__init__()
        self.onboarding = onboarding
        self.regular = regular


_bannerSettingsSchema = schemas.Schema(fields={'eventStartAt': fields.DateTime(),
 'eventEndAt': fields.DateTime()}, modelClass=EntryPointSettingsModel)
afkSchema = schemas.Schema(fields={'maxPlayerInactiveTime': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'arenaWaitPlayerTime': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=AfkModel, checkUnknown=True)
afkModesSchema = schemas.Schema(fields={'onboarding': fields.Nested(schema=afkSchema, required=True),
 'regular': fields.Nested(schema=afkSchema, required=True)}, modelClass=AfkModesModel, checkUnknown=True)
settingsSchema = GameParamsSchema[SettingsModel](gameParamsKey='story_mode_settings', fields={'enabled': fields.Boolean(required=True),
 'waitTimeQueue': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'hideGameLoadingTimeout': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'joinToQueueFromLogin': fields.Boolean(required=True, filterParams=GameParamsScopeFlags.BASE),
 'modeSelectorCardColumn': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1, maxValue=3)),
 'modeSelectorCardPriority': fields.Integer(required=True),
 'afk': fields.Nested(schema=afkModesSchema, required=True, filterParams=GameParamsScopeFlags.BASE),
 'entryPoint': fields.Nested(schema=_bannerSettingsSchema),
 'newbieBannerEnabled': fields.Boolean(required=True),
 'newbieAdvertisingEnabled': fields.Boolean(required=True),
 'parallaxEnabled': fields.Boolean(required=True),
 'eventName': fields.NonEmptyString(required=True)}, modelClass=SettingsModel, checkUnknown=True, usedInReplay=True)
