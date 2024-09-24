# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/story_mode_missions.py
import datetime
from functools import partial
import typing
import bonus_readers
from base_schema_manager import GameParamsSchema
from constants import ARENA_BONUS_TYPE_NAMES
from dict2model import models, schemas, fields, validate, exceptions
from story_mode_common.story_mode_constants import FIRST_MISSION_ID, STORY_MODE_BONUS_TYPES, FIRST_MISSION_TASK_ID, UNDEFINED_MISSION_ID, MissionsDifficulty, MissionType
from sounds_schema import soundSchema
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType
    from sounds_schema import SoundModel
EVENT_MISSION_MIN_ID = 1000

class VehicleModel(models.Model):
    __slots__ = ('name', 'styleId')

    def __init__(self, name, styleId):
        super(VehicleModel, self).__init__()
        self.name = name
        self.styleId = styleId

    def __repr__(self):
        return '<VehicleModel(name={}, styleId={})>'.format(self.name, self.styleId)


class AutoCompleteTaskModel(models.Model):
    __slots__ = ('missionId', 'taskId', 'giveReward')

    def __init__(self, missionId, taskId, giveReward):
        super(AutoCompleteTaskModel, self).__init__()
        self.missionId = missionId
        self.taskId = taskId
        self.giveReward = giveReward

    def __repr__(self):
        return '<AutoCompleteTaskModel(missionId={}, taskId={}, giveReward={})>'.format(self.missionId, self.taskId, self.giveReward)


class MissionTaskModel(models.Model):
    __slots__ = ('id', 'reward', 'autoCompleteTasks', 'unlockDate')

    def __init__(self, id, reward, autoCompleteTasks, unlockDate):
        super(MissionTaskModel, self).__init__()
        self.id = id
        self.reward = reward
        self.autoCompleteTasks = autoCompleteTasks
        self.unlockDate = unlockDate

    def __repr__(self):
        return '<MissionTaskModel(id={}, reward={}, autoCompleteTasks={}, unlockDate={})>'.format(self.id, self.reward, self.autoCompleteTasks, self.unlockDate)

    def isLocked(self):
        return self.unlockDate and self.unlockDate > datetime.datetime.utcnow()


class MissionDisabledTimerModel(models.Model):
    __slots__ = ('showAt', 'endAt')

    def __init__(self, showAt, endAt):
        super(MissionDisabledTimerModel, self).__init__()
        self.showAt = showAt
        self.endAt = endAt

    def __repr__(self):
        return '<MissionDisabledTimerModel(showAt={}, endAt={})>'.format(self.showAt, self.endAt)


class SoundsModel(models.Model):
    __slots__ = ('music', 'ambience')

    def __init__(self, music, ambience):
        super(SoundsModel, self).__init__()
        self.music = music
        self.ambience = ambience

    def __repr__(self):
        return '<SoundsModel(music={}, ambience={})>'.format(self.music, self.ambience)


class MissionModel(models.Model):
    __slots__ = ('missionId', 'vehicle', 'geometry', 'bonusType', 'displayName', 'missionType', 'difficulty', 'sounds', 'tasks', 'enabled', 'disabledTimer', 'reward', 'showRewardInBattleResults', 'unlockBattlesCount', 'newbieBattlesMin', 'newbieBattlesMax')

    def __init__(self, missionId, vehicle, geometry, bonusType, displayName, missionType, difficulty, sounds, tasks, enabled, disabledTimer, reward, showRewardInBattleResults, unlockBattlesCount, newbieBattlesMin, newbieBattlesMax):
        super(MissionModel, self).__init__()
        self.missionId = missionId
        self.vehicle = vehicle
        self.geometry = geometry
        self.bonusType = bonusType
        self.displayName = displayName
        self.missionType = missionType
        self.difficulty = difficulty
        self.sounds = sounds
        self.tasks = tasks
        self.enabled = enabled
        self.disabledTimer = disabledTimer
        self.reward = reward
        self.showRewardInBattleResults = showRewardInBattleResults
        self.unlockBattlesCount = unlockBattlesCount
        self.newbieBattlesMin = newbieBattlesMin
        self.newbieBattlesMax = newbieBattlesMax

    def getTask(self, taskId):
        return next((task for task in self.tasks if task.id == taskId), None)

    def getTasksReward(self, tasksIds=None, isBattlePassActive=True):
        rewards = []
        if tasksIds is None:
            tasksIds = [ task.id for task in self.tasks ]
        for taskId in tasksIds:
            task = self.getTask(taskId)
            if task is not None:
                reward = task.reward.copy()
                if not isBattlePassActive:
                    reward.pop('battlePassPoints', None)
                rewards.append(reward)

        return rewards

    def getMissionReward(self, forBattleResults=False):
        reward = {}
        if not forBattleResults or self.showRewardInBattleResults:
            reward = self.reward.copy()
        return reward

    def getUnlockedTasks(self):
        return [ task for task in self.tasks if not task.isLocked() ]

    @property
    def isEvent(self):
        return self.missionType == MissionType.EVENT

    def isMissionLocked(self, battlesCount):
        return battlesCount < self.unlockBattlesCount

    def __repr__(self):
        return '<MissionModel(id={}, vehicle={}, geometry={}, bonusType={}, displayName={}, missionType={}, difficulty={}, sounds={}, tasks={}, enabled={}, disabledTimer={}, bonus={}, showRewardInBattleResults={}, unlockBattlesCount={}, newbieBattlesMin={}, newbieBattlesMax={}>'.format(self.missionId, self.vehicle, self.geometry, self.bonusType, self.displayName, self.missionType, self.difficulty, self.sounds, self.tasks, self.enabled, self.disabledTimer, self.reward, self.showRewardInBattleResults, self.unlockBattlesCount, self.newbieBattlesMin, self.newbieBattlesMax)


class OnboardingModel(models.Model):
    __slots__ = ('reward',)

    def __init__(self, reward):
        super(OnboardingModel, self).__init__()
        self.reward = reward

    def __repr__(self):
        return '<OnboardingModel(reward={})>'.format(self.reward)


class MissionsModel(models.Model):
    __slots__ = ('missions', 'onboarding', '_missionsById', '_eventMissions', '_regularMissions', '_lastMissionId')

    def __init__(self, missions, onboarding):
        super(MissionsModel, self).__init__()
        self.missions = missions
        self.onboarding = onboarding
        self._missionsById = {}
        self._regularMissions = []
        self._eventMissions = []
        self._lastMissionId = None
        for mission in self.missions:
            self._missionsById[mission.missionId] = mission
            if mission.missionType == MissionType.EVENT:
                self._eventMissions.append(mission)
            self._regularMissions.append(mission)

        return

    @property
    def onboardingLastMissionId(self):
        if self._lastMissionId is None:
            self._lastMissionId = UNDEFINED_MISSION_ID
            for mission in self._regularMissions:
                if mission.missionType == MissionType.ONBOARDING and mission.missionId > self._lastMissionId:
                    self._lastMissionId = mission.missionId

        return self._lastMissionId

    def isOnboarding(self, missionId):
        mission = self.getMission(missionId)
        return bool(mission and mission.missionType == MissionType.ONBOARDING)

    def isEvent(self, missionId):
        mission = self.getMission(missionId)
        return bool(mission and mission.isEvent)

    def getMission(self, missionId):
        return self._missionsById.get(missionId)

    def filter(self, enabled=None, missionType=None):
        missions = self.missions if missionType is None else (self._eventMissions if missionType == MissionType.EVENT else self._regularMissions)
        for mission in missions:
            if enabled is None or mission.enabled == enabled:
                yield mission

        return

    @property
    def isEventEnabled(self):
        return any((mission.enabled for mission in self._eventMissions))

    def __repr__(self):
        return '<MissionsModel(missions={}, onboarding={})>'.format(self.missions, self.onboarding)


def validateMissionIds(model):
    sequencesIds, idDuplicates = set(), set()
    nextMissionId = FIRST_MISSION_ID
    for mission in model.missions:
        if mission.isEvent:
            if mission.missionId < EVENT_MISSION_MIN_ID:
                raise exceptions.ValidationError('Mission id={} is wrong. Event missions id must be >= {}'.format(mission.missionId, EVENT_MISSION_MIN_ID))
        else:
            if mission.missionId != nextMissionId:
                raise exceptions.ValidationError('Mission id={} has wrong order'.format(mission.missionId))
            nextMissionId += 1
        if mission.missionId not in sequencesIds:
            sequencesIds.add(mission.missionId)
        idDuplicates.add(mission.missionId)

    if idDuplicates:
        raise exceptions.ValidationError('Mission id duplicates: {}'.format(idDuplicates))


def validateBonusType(bonusType):
    if ARENA_BONUS_TYPE_NAMES.get(bonusType) not in STORY_MODE_BONUS_TYPES:
        raise exceptions.ValidationError('Invalid mission bonusType: {}'.format(bonusType))


def _validateMissionTasksIds(model):
    ids, duplicates = set(), set()
    nextId = FIRST_MISSION_TASK_ID
    for task in model.tasks:
        if task.id != nextId:
            raise exceptions.ValidationError('Mission(id={}) task(id={}) has id that is out of order'.format(model.missionId, task.id))
        nextId += 1
        if task.id not in ids:
            ids.add(task.id)
        duplicates.add(task.id)

    if duplicates:
        raise exceptions.ValidationError('Mission(id={}) tasks ids duplicates: {}'.format(model.missionId, duplicates))


def _validateShowRewardHasReward(model):
    if model.showRewardInBattleResults and not model.reward:
        raise exceptions.ValidationError('showRewardInBattleResults is set to true, but no reward is provided')


def _validateAutoCompleteMissionTasks(model):
    missionsTasks = set()
    autoCompleteTasks = set()
    for mission in model.missions:
        for task in mission.tasks:
            missionsTasks.add((mission.missionId, task.id))
            for completeTask in task.autoCompleteTasks:
                autoCompleteTasks.add((completeTask.missionId, completeTask.taskId))

    missing = autoCompleteTasks - missionsTasks
    if missing:
        raise exceptions.ValidationError('Bad auto complete tasks: {}'.format(', '.join(('(missionId={}, taskId={})'.format(*k) for k in missing))))


def _validateMissionDisabledTimer(model):
    if model.showAt >= model.endAt:
        raise exceptions.ValidationError('Bad mission disabled timer: showAt({}) should be less than endAt({})'.format(model.showAt, model.endAt))


def _validateMissionsEnabled(model):
    if all((not mission.enabled for mission in model.missions)):
        raise exceptions.ValidationError('At least one mission should be enabled')


vehicleSchema = schemas.Schema(fields={'name': fields.String(required=True, deserializedValidators=validate.Length(minValue=1)),
 'styleId': fields.Integer(required=False, public=False, deserializedValidators=validate.Range(minValue=0), default=0)}, modelClass=VehicleModel, checkUnknown=True)
_autoCompleteTaskSchema = schemas.Schema(fields={'missionId': fields.Integer(deserializedValidators=validate.Range(minValue=1)),
 'taskId': fields.Integer(deserializedValidators=validate.Range(minValue=1)),
 'giveReward': fields.Boolean()}, checkUnknown=True, modelClass=AutoCompleteTaskModel)

class _RewardField(fields.Field):

    def __init__(self, required=True, default=dict, public=True, serializedValidators=None, deserializedValidators=None):
        super(_RewardField, self).__init__(required=required, default=default, public=public, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)

    def _deserialize(self, incoming, **kwargs):
        if not isinstance(incoming, dict):
            raise exceptions.ValidationError("Dictionary expected, got '{}'".format(type(incoming)))
        return super(_RewardField, self)._deserialize(incoming, **kwargs)


_missionTaskSchema = schemas.Schema(fields={'id': fields.Integer(deserializedValidators=validate.Range(minValue=1)),
 'reward': _RewardField(required=False),
 'autoCompleteTasks': fields.UniCapList(fieldOrSchema=_autoCompleteTaskSchema, required=False, default=list),
 'unlockDate': fields.DateTime(required=False)}, checkUnknown=True, modelClass=MissionTaskModel)
_missionDisabledTimerSchema = schemas.Schema[MissionDisabledTimerModel](fields={'showAt': fields.DateTime(),
 'endAt': fields.DateTime()}, modelClass=MissionDisabledTimerModel, deserializedValidators=_validateMissionDisabledTimer)
_soundsSchema = schemas.Schema(fields={'music': fields.Nested(schema=soundSchema, required=True),
 'ambience': fields.Nested(schema=soundSchema, required=True)}, modelClass=SoundsModel, checkUnknown=True)
missionSchema = schemas.Schema[MissionModel](fields={'missionId': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'vehicle': fields.Nested(schema=vehicleSchema, required=True),
 'geometry': fields.String(required=True, public=False, deserializedValidators=validate.Length(minValue=1)),
 'bonusType': fields.String(required=True, public=False, deserializedValidators=[validate.Length(minValue=1), validateBonusType]),
 'displayName': fields.String(required=False, default=''),
 'missionType': fields.String(required=False, default=MissionType.REGULAR),
 'difficulty': fields.Enum(enumClass=MissionsDifficulty, required=False, default=MissionsDifficulty.UNDEFINED),
 'sounds': fields.Nested(schema=_soundsSchema, required=True),
 'tasks': fields.UniCapList(fieldOrSchema=_missionTaskSchema, required=True),
 'enabled': fields.Boolean(),
 'disabledTimer': fields.Nested(schema=_missionDisabledTimerSchema, required=False),
 'reward': _RewardField(required=False),
 'showRewardInBattleResults': fields.Boolean(required=False, default=False),
 'unlockBattlesCount': fields.Integer(required=False, deserializedValidators=validate.Range(minValue=1), default=0),
 'newbieBattlesMin': fields.Integer(required=False, deserializedValidators=validate.Range(minValue=1), default=0),
 'newbieBattlesMax': fields.Integer(required=False, deserializedValidators=validate.Range(minValue=1), default=0)}, modelClass=MissionModel, checkUnknown=True, deserializedValidators=[_validateMissionTasksIds, _validateShowRewardHasReward])
onboardingSchema = schemas.Schema[OnboardingModel](fields={'reward': _RewardField(required=False)}, modelClass=OnboardingModel)
missionsSchema = GameParamsSchema[MissionsModel](gameParamsKey='story_mode_missions', fields={'missions': fields.UniCapList(fieldOrSchema=missionSchema, required=True, deserializedValidators=validate.Length(minValue=1)),
 'onboarding': fields.Nested(schema=onboardingSchema, required=True)}, modelClass=MissionsModel, checkUnknown=True, deserializedValidators=[validateMissionIds, _validateAutoCompleteMissionTasks, _validateMissionsEnabled], readers={'reward': partial(bonus_readers.readBonusSection, bonus_readers.SUPPORTED_BONUSES)})
