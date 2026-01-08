# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/configs/story_mode_missions.py
import logging
import datetime
import typing
from game_params_common.base_manager import GameParamsSchema
from constants import ARENA_BONUS_TYPE_NAMES
from dict2model import models, schemas, fields, validate, exceptions
from game_params_common.scope import GameParamsScopeFlags
from items import vehicles
from story_mode_common.configs.task_conditions import TaskConditionType
from story_mode_common.helpers import isMissionCompleted
from story_mode_common.story_mode_constants import STORY_MODE_BONUS_TYPES, TaskId, MissionId, MissionsDifficulty, MissionType, MissionLockCondition
from sounds_schema import SoundSchema
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType, TFilterParams, TFilter
    from dict2model.schemas import SchemaModelType, TRawData
    from sounds_schema import SoundModel
_logger = logging.getLogger(__name__)
EVENT_MISSION_MIN_ID = 1000

class VehicleModel(models.Model):
    __slots__ = ('name', 'styleId', 'equipments')

    def __init__(self, name, styleId, equipments):
        super(VehicleModel, self).__init__()
        self.name = name
        self.styleId = styleId
        self.equipments = equipments

    def getEquipmentsSetup(self):
        equipmentsSetup = []
        for equipmentName in self.equipments:
            equipmentId = vehicles.g_cache.equipmentIDs().get(equipmentName)
            if equipmentId is None:
                _logger.error('Wrong equipment name: %s', equipmentName)
                continue
            equipmentsSetup.append(vehicles.g_cache.equipments()[equipmentId].compactDescr)

        return equipmentsSetup


class AutoCompleteTaskModel(models.Model):
    __slots__ = ('missionId', 'taskId', 'giveReward')

    def __init__(self, missionId, taskId, giveReward):
        super(AutoCompleteTaskModel, self).__init__()
        self.missionId = missionId
        self.taskId = taskId
        self.giveReward = giveReward


class MissionTaskModel(models.Model):
    __slots__ = ('id', 'reward', 'autoCompleteTasks', 'unlockDate', 'conditions')

    def __init__(self, id, reward, autoCompleteTasks, unlockDate, conditions):
        super(MissionTaskModel, self).__init__()
        self.id = id
        self.reward = reward
        self.autoCompleteTasks = autoCompleteTasks
        self.unlockDate = unlockDate
        self.conditions = conditions

    def getCondition(self, name):
        return next((condition for condition in self.conditions if condition.name == name), None)

    def isLocked(self):
        return self.unlockDate and self.unlockDate > datetime.datetime.utcnow()


class MissionDisabledTimerModel(models.Model):
    __slots__ = ('showAt', 'endAt')

    def __init__(self, showAt, endAt):
        super(MissionDisabledTimerModel, self).__init__()
        self.showAt = showAt
        self.endAt = endAt


class SoundsModel(models.Model):
    __slots__ = ('music', 'ambience', 'battleMusic')

    def __init__(self, music, ambience, battleMusic):
        super(SoundsModel, self).__init__()
        self.music = music
        self.ambience = ambience
        self.battleMusic = battleMusic


class LockByMissionModel(models.Model):
    __slots__ = ('missionId',)

    def __init__(self, missionId):
        super(LockByMissionModel, self).__init__()
        self.missionId = missionId

    def getLockReason(self, progress):
        missions = missionsSchema.getModel()
        if missions is None or missions.getMission(self.missionId) is None:
            return ''
        else:
            lockingMission = missions.getMission(self.missionId)
            return 'Mission is locked by another mission' if not isMissionCompleted(progress, lockingMission) else ''


lockByMissionSchema = schemas.Schema[LockByMissionModel](fields={'missionId': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=LockByMissionModel)

class BattlesCountLockModel(models.Model):
    __slots__ = ('battlesCount',)

    def __init__(self, battlesCount):
        super(BattlesCountLockModel, self).__init__()
        self.battlesCount = battlesCount

    def getLockReason(self, battlesCount):
        return 'Not enough battles to join the mission' if battlesCount < self.battlesCount else ''


battlesCountLockSchema = schemas.Schema[BattlesCountLockModel](fields={'battlesCount': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=BattlesCountLockModel)

class MissionLockerModel(models.Model):
    __slots__ = ('active', 'byMission', 'battlesCount')

    def __init__(self, active, byMission=None, battlesCount=None):
        super(MissionLockerModel, self).__init__()
        self.active = active
        self.byMission = byMission
        self.battlesCount = battlesCount

    def getLockReason(self, progress, battlesCount):
        if self.active == MissionLockCondition.BY_MISSION and self.byMission is not None:
            return self.byMission.getLockReason(progress)
        else:
            return self.battlesCount.getLockReason(battlesCount) if self.active == MissionLockCondition.BATTLES_COUNT and self.battlesCount is not None else None


class MissionModel(models.Model):
    __slots__ = ('missionId', 'vehicle', 'geometry', 'bonusType', 'displayName', 'missionType', 'difficulty', 'sounds', 'tasks', 'enabled', 'disabledTimer', 'reward', 'showRewardInBattleResults', 'newbieBattlesMin', 'newbieBattlesMax', 'spawnGroup', 'unlockMission', 'hasOutroVideo', 'switchVehicles', 'missionLocker')

    def __init__(self, missionId, vehicle, geometry, bonusType, displayName, missionType, difficulty, sounds, tasks, enabled, disabledTimer, reward, showRewardInBattleResults, newbieBattlesMin, newbieBattlesMax, spawnGroup, hasOutroVideo, switchVehicles, missionLocker):
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
        self.newbieBattlesMin = newbieBattlesMin
        self.newbieBattlesMax = newbieBattlesMax
        self.spawnGroup = spawnGroup
        self.hasOutroVideo = hasOutroVideo
        self.switchVehicles = switchVehicles
        self.missionLocker = missionLocker

    def getSwitchVehicles(self, withDefaultVehicle=True):
        switchVehicles = [self.vehicle] if withDefaultVehicle else []
        return [ (vehModel.name, vehModel.styleId) for vehModel in switchVehicles + self.switchVehicles ]

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

    def getTaskConditionValues(self):
        return {task.id:{c.name:c.value for c in task.conditions} for task in self.tasks}

    def getLockReason(self, progress, battlesCount):
        return '' if self.missionLocker is None else self.missionLocker.getLockReason(progress, battlesCount)

    def getBattlesToUnlock(self, battlesCount):
        return None if self.missionLocker is None or self.missionLocker.battlesCount is None or not self.getLockReason({}, battlesCount) else self.missionLocker.battlesCount.battlesCount - battlesCount


class OnboardingModel(models.Model):
    __slots__ = ('reward',)

    def __init__(self, reward):
        super(OnboardingModel, self).__init__()
        self.reward = reward


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
            self._lastMissionId = MissionId.UNDEFINED
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


class ValidateMissionIds(validate.IterableOfSequential):
    __slots__ = ()

    def __init__(self):
        super(ValidateMissionIds, self).__init__('missionId', MissionId.ONE)

    def __call__(self, mission, *args, **kwargs):
        if mission.isEvent:
            if mission.missionId < EVENT_MISSION_MIN_ID:
                raise exceptions.ValidationError('Mission id={} is wrong. Event missions id must be >= {}'.format(mission.missionId, EVENT_MISSION_MIN_ID))
        else:
            super(ValidateMissionIds, self).__call__(mission, *args, **kwargs)


class ValidateLockingMission(validate.IterableValidator):
    __slots__ = ()

    def __call__(self, mission, storage, *args, **kwargs):
        storage.add(mission.missionId)
        if mission.missionLocker is not None and mission.missionLocker.byMission is not None:
            lockingMissionId = mission.missionLocker.byMission.missionId
            if lockingMissionId not in storage:
                raise exceptions.ValidationError('Locking mission with id={} is not defined.'.format(lockingMissionId))
        return

    def createStorage(self):
        return set()


class ValidateAutoCompleteTasks(validate.IterableValidator):
    __slots__ = ()

    def __call__(self, mission, storage, lastIteration, *args, **kwargs):
        missionsTasks, autoCompleteTasks = storage
        for task in mission.tasks:
            missionsTasks.add((mission.missionId, task.id))
            for completeTask in task.autoCompleteTasks:
                autoCompleteTasks.add((completeTask.missionId, completeTask.taskId))

        if lastIteration:
            missingTaskIds = autoCompleteTasks - missionsTasks
            if missingTaskIds:
                raise exceptions.CumulativeIterableValidationError('Bad auto complete tasks: {}'.format(', '.join(('(missionId={}, taskId={})'.format(*k) for k in missingTaskIds))))

    def createStorage(self):
        return [set(), set()]


def validateBonusType(bonusType):
    if ARENA_BONUS_TYPE_NAMES.get(bonusType) not in STORY_MODE_BONUS_TYPES:
        raise exceptions.ValidationError('Invalid mission bonusType: {}'.format(bonusType))


def _validateShowRewardHasReward(model):
    if model.showRewardInBattleResults and not model.reward:
        raise exceptions.ValidationError('showRewardInBattleResults is set to true, but no reward is provided')


def _validateMissionDisabledTimer(model):
    if model.showAt >= model.endAt:
        raise exceptions.ValidationError('Bad mission disabled timer: showAt({}) should be less than endAt({})'.format(model.showAt, model.endAt))


vehicleSchema = schemas.Schema(fields={'name': fields.String(required=True, deserializedValidators=validate.Length(minValue=1)),
 'styleId': fields.Integer(required=False, filterParams=GameParamsScopeFlags.CELL_ARENA, deserializedValidators=validate.Range(minValue=0), default=0),
 'equipments': fields.ListFromString(field=fields.String(), required=False, filterParams=GameParamsScopeFlags.CELL_ARENA)}, modelClass=VehicleModel, checkUnknown=True)
_autoCompleteTaskSchema = schemas.Schema(fields={'missionId': fields.Integer(deserializedValidators=validate.Range(minValue=1)),
 'taskId': fields.Integer(deserializedValidators=validate.Range(minValue=1)),
 'giveReward': fields.Boolean()}, checkUnknown=True, modelClass=AutoCompleteTaskModel)

class _RewardField(fields.Field):

    def __init__(self, required=True, default=dict, filterParams=None, serializedValidators=None, deserializedValidators=None):
        super(_RewardField, self).__init__(required=required, default=default, filterParams=filterParams, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)

    def _deserialize(self, incoming, **kwargs):
        if not isinstance(incoming, dict):
            raise exceptions.ValidationError("Dictionary expected, got '{}'".format(type(incoming)))
        return super(_RewardField, self)._deserialize(incoming, **kwargs)


class ConditionModel(models.Model):
    __slots__ = ('name', 'value', 'type')

    def __init__(self, name, value, type):
        super(ConditionModel, self).__init__()
        self.name = name
        self.value = value
        self.type = type


class TaskConditionSchema(schemas.Schema):

    def __init__(self):
        super(TaskConditionSchema, self).__init__(fields={'name': fields.String(required=True),
         'value': fields.Field(required=True),
         'type': fields.StrEnum(enumClass=TaskConditionType, required=True)}, modelClass=ConditionModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None)
        return

    def _deserialize(self, incoming, filter_=None, skipValidation=False, **kwargs):
        self._fields['value'] = TaskConditionType(incoming['type']).getSchemaFieldType()
        return super(TaskConditionSchema, self)._deserialize(incoming, filter_=filter_, skipValidation=skipValidation, **kwargs)

    def serialize(self, incoming, filter_=None, silent=False, logError=True, skipValidation=False, **kwargs):
        self._fields['value'] = incoming.type.getSchemaFieldType()
        return super(TaskConditionSchema, self).serialize(incoming, filter_, silent, logError, skipValidation, **kwargs)


_missionTaskSchema = schemas.Schema(fields={'id': fields.Integer(deserializedValidators=validate.Range(minValue=1)),
 'reward': _RewardField(required=False, filterParams=GameParamsScopeFlags.CLIENT),
 'autoCompleteTasks': fields.UniCapList(fieldOrSchema=_autoCompleteTaskSchema, required=False, default=list, filterParams=GameParamsScopeFlags.CLIENT),
 'unlockDate': fields.DateTime(required=False, filterParams=GameParamsScopeFlags.CLIENT),
 'conditions': fields.UniCapList(fieldOrSchema=TaskConditionSchema(), required=False, default=list, deserializedValidators=validate.ValidateIterable([validate.IterableOfUnique('name')]))}, checkUnknown=True, modelClass=MissionTaskModel)
_missionDisabledTimerSchema = schemas.Schema[MissionDisabledTimerModel](fields={'showAt': fields.DateTime(),
 'endAt': fields.DateTime()}, modelClass=MissionDisabledTimerModel, deserializedValidators=_validateMissionDisabledTimer)
missionSoundSchema = SoundSchema(fields={'start': fields.String(required=True),
 'stop': fields.String(required=True)})

def _validateMissionLockers(lockerModel):
    if getattr(lockerModel, lockerModel.active.value, None) is None:
        raise exceptions.ValidationError('Locker "{}" is not defined.'.format(lockerModel.active))
    return


missionLockerSchema = schemas.Schema[MissionLockerModel](fields={'active': fields.StrEnum(enumClass=MissionLockCondition, required=True),
 MissionLockCondition.BATTLES_COUNT.value: fields.Nested(schema=battlesCountLockSchema, required=False),
 MissionLockCondition.BY_MISSION.value: fields.Nested(schema=lockByMissionSchema, required=False)}, modelClass=MissionLockerModel, deserializedValidators=[_validateMissionLockers])
_soundsSchema = schemas.Schema(fields={'music': fields.Nested(schema=missionSoundSchema, required=True),
 'ambience': fields.Nested(schema=missionSoundSchema, required=True),
 'battleMusic': fields.Nested(schema=missionSoundSchema, required=False)}, modelClass=SoundsModel, checkUnknown=True)
missionSchema = schemas.Schema[MissionModel](fields={'missionId': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'vehicle': fields.Nested(schema=vehicleSchema, required=True),
 'switchVehicles': fields.UniCapList(fieldOrSchema=vehicleSchema, required=False, filterParams=GameParamsScopeFlags.CELL_ARENA, default=list, deserializedValidators=validate.ValidateIterable([validate.IterableOfUnique('name')])),
 'geometry': fields.String(required=True, filterParams=GameParamsScopeFlags.BASE, deserializedValidators=validate.Length(minValue=1)),
 'bonusType': fields.String(required=True, filterParams=GameParamsScopeFlags.BASE, deserializedValidators=[validate.Length(minValue=1), validateBonusType]),
 'displayName': fields.String(required=False, default='', filterParams=GameParamsScopeFlags.CLIENT),
 'missionType': fields.StrEnum(enumClass=MissionType, required=False, default=MissionType.REGULAR),
 'difficulty': fields.StrEnum(enumClass=MissionsDifficulty, required=False, default=MissionsDifficulty.UNDEFINED),
 'sounds': fields.Nested(schema=_soundsSchema, required=True, filterParams=GameParamsScopeFlags.CLIENT),
 'tasks': fields.UniCapList(fieldOrSchema=_missionTaskSchema, required=True, deserializedValidators=validate.ValidateIterable([validate.IterableOfSequential('id', TaskId.ONE)])),
 'enabled': fields.Boolean(filterParams=GameParamsScopeFlags.CLIENT),
 'disabledTimer': fields.Nested(schema=_missionDisabledTimerSchema, required=False, filterParams=GameParamsScopeFlags.CLIENT),
 'reward': _RewardField(required=False, filterParams=GameParamsScopeFlags.CLIENT),
 'showRewardInBattleResults': fields.Boolean(required=False, default=False, filterParams=GameParamsScopeFlags.CLIENT),
 'newbieBattlesMin': fields.Integer(required=False, deserializedValidators=validate.Range(minValue=1), default=0, filterParams=GameParamsScopeFlags.CLIENT),
 'newbieBattlesMax': fields.Integer(required=False, deserializedValidators=validate.Range(minValue=1), default=0, filterParams=GameParamsScopeFlags.CLIENT),
 'spawnGroup': fields.Integer(required=False, deserializedValidators=validate.Range(minValue=0), default=0, filterParams=GameParamsScopeFlags.CLIENT),
 'hasOutroVideo': fields.Boolean(required=False, default=False, filterParams=GameParamsScopeFlags.CLIENT),
 'missionLocker': fields.Nested(schema=missionLockerSchema, required=False, filterParams=GameParamsScopeFlags.CLIENT)}, modelClass=MissionModel, checkUnknown=True, deserializedValidators=_validateShowRewardHasReward)
onboardingSchema = schemas.Schema[OnboardingModel](fields={'reward': _RewardField(required=False)}, modelClass=OnboardingModel)

def _getRewardReaders(*args, **kwargs):
    import bonus_readers
    return bonus_readers.readBonusSection(bonus_readers.SUPPORTED_BONUSES, *args, **kwargs)


missionsSchema = GameParamsSchema[MissionsModel](gameParamsKey='story_mode_missions', fields={'missions': fields.UniCapList(fieldOrSchema=missionSchema, required=True, deserializedValidators=[validate.Length(minValue=1), validate.ValidateIterable([ValidateMissionIds(),
               ValidateLockingMission(),
               ValidateAutoCompleteTasks(),
               validate.IterableAnyTrue('enabled')])]),
 'onboarding': fields.Nested(schema=onboardingSchema, required=True, filterParams=GameParamsScopeFlags.CLIENT)}, modelClass=MissionsModel, checkUnknown=True, readers={'reward': _getRewardReaders}, usedInReplay=True)
