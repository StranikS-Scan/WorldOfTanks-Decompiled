# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/configs/sm_client_settings.py
import os
import typing
import ResMgr
import section2dict
from dict2model import models, schemas, fields, validate, exceptions
from soft_exception import SoftException
from story_mode_common.story_mode_constants import EventMissionSelector, MissionsDifficulty, EXTENSION_NAME
_CLIENT_SETTINGS_PATH = os.path.join(EXTENSION_NAME, 'gui/sm_client_settings.xml')

class BattlesCountSelectorModel(models.Model):
    __slots__ = ('normal', 'hard')

    def __init__(self, normal=0, hard=0):
        super(BattlesCountSelectorModel, self).__init__()
        self.normal = normal
        self.hard = hard

    def getDifficulty(self, playerBattles):
        currentDifficulty, currentDifficultyBattles = MissionsDifficulty.UNDEFINED, -1
        for difficulty in MissionsDifficulty:
            difficultyBattles = getattr(self, difficulty, None)
            if difficultyBattles is not None:
                currentDifficultyBattles = playerBattles >= difficultyBattles > currentDifficultyBattles and difficultyBattles
                currentDifficulty = difficulty

        return currentDifficulty


battlesCountSelectorSchema = schemas.Schema[BattlesCountSelectorModel](fields={MissionsDifficulty.NORMAL.value: fields.Integer(required=False, deserializedValidators=validate.Range(minValue=0)),
 MissionsDifficulty.HARD.value: fields.Integer(required=False, deserializedValidators=validate.Range(minValue=0))}, modelClass=BattlesCountSelectorModel)

class MissionSelectorsModel(models.Model):
    __slots__ = ('active', 'default', 'withUnlockMission', 'battlesCount')

    def __init__(self, active=EventMissionSelector.DEFAULT, default=None, withUnlockMission=None, battlesCount=None):
        super(MissionSelectorsModel, self).__init__()
        self.active = active
        self.default = default
        self.withUnlockMission = withUnlockMission
        self.battlesCount = battlesCount or BattlesCountSelectorModel()


def _validateMissionSelectors(selectorsModel):
    if not hasattr(selectorsModel, selectorsModel.active.value):
        exceptions.ValidationError('Active mission selector "{}" is not defined.'.format(selectorsModel.active))


missionSelectorsSchema = schemas.Schema[MissionSelectorsModel](fields={'active': fields.StrEnum(enumClass=EventMissionSelector),
 EventMissionSelector.DEFAULT.value: fields.Field(),
 EventMissionSelector.WITH_UNLOCK_MISSION.value: fields.Field(),
 EventMissionSelector.BATTLES_COUNT.value: fields.Nested(schema=battlesCountSelectorSchema)}, modelClass=MissionSelectorsModel, deserializedValidators=[_validateMissionSelectors])

class EventModel(models.Model):
    __slots__ = ('missionSelectors',)

    def __init__(self, missionSelectors=None):
        super(EventModel, self).__init__()
        self.missionSelectors = missionSelectors or MissionSelectorsModel()


eventSchema = schemas.Schema[EventModel](fields={'missionSelectors': fields.Nested(schema=missionSelectorsSchema)}, modelClass=EventModel)

class ClientSettingsModel(models.Model):
    __slots__ = ('event',)

    def __init__(self, event=None):
        super(ClientSettingsModel, self).__init__()
        self.event = event or EventModel()


clientSettingsSchema = schemas.Schema[ClientSettingsModel](fields={'event': fields.Nested(schema=eventSchema)}, modelClass=ClientSettingsModel)
_g_clientSettings = None

def initialize():
    global _g_clientSettings
    root = ResMgr.openSection(_CLIENT_SETTINGS_PATH)
    rawData = section2dict.parse(root)
    _g_clientSettings = clientSettingsSchema.deserialize(rawData, silent=True) or ClientSettingsModel()


def getClientSettings():
    if _g_clientSettings is None:
        raise SoftException('Story mode client settings must be initialized before use.')
    return _g_clientSettings
