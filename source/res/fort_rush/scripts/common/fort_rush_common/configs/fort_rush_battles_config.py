# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/configs/fort_rush_battles_config.py
from __future__ import absolute_import
import typing
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, VEHICLE_CLASS
from dict2model import models, schemas, fields, validate
from fort_rush_common.fort_rush_constants import EXT_GAME_PARAMS_KEY
from game_params_common.schema import GameParamsSchema
from game_params_common.scope import GameParamsScopeFlags
_VEHICLE_CLASSES = (VEHICLE_CLASS.LIGHT_TANK,
 VEHICLE_CLASS.MEDIUM_TANK,
 VEHICLE_CLASS.HEAVY_TANK,
 VEHICLE_CLASS.SPG,
 VEHICLE_CLASS.AT_SPG)
if typing.TYPE_CHECKING:
    from typing import List
    from Arena import Arena
_DEFAULT_MODE_SELECTOR_COLUMN = 1
_DEFAULT_MODE_SELECTOR_PRIORITY = 40

class StageModel(models.Model):
    __slots__ = ('quest', 'level')

    def __init__(self, quest, level):
        super(StageModel, self).__init__()
        self.quest = quest
        self.level = level


class ProgressionModel(models.Model):
    __slots__ = ('stage',)

    def __init__(self, stage):
        super(ProgressionModel, self).__init__()
        self.stage = stage


class DailyMissionsConfigModel(models.Model):
    __slots__ = ('dailyMissionQuestPrefix', 'hardDailyMissionQuestPrefix', 'dailyMissionTokenPrefix', 'dailyMissionTokenPostfix', 'dailyMissionTokenTtl', 'tokenLimit', 'dailyGroupsCount', 'dailyQuestMaxDays')

    def __init__(self, dailyMissionQuestPrefix, hardDailyMissionQuestPrefix, dailyMissionTokenPrefix, dailyMissionTokenPostfix, dailyMissionTokenTtl, tokenLimit, dailyGroupsCount, dailyQuestMaxDays):
        super(DailyMissionsConfigModel, self).__init__()
        self.dailyMissionQuestPrefix = dailyMissionQuestPrefix
        self.hardDailyMissionQuestPrefix = hardDailyMissionQuestPrefix
        self.dailyMissionTokenPrefix = dailyMissionTokenPrefix
        self.dailyMissionTokenPostfix = dailyMissionTokenPostfix
        self.dailyMissionTokenTtl = dailyMissionTokenTtl
        self.tokenLimit = tokenLimit
        self.dailyGroupsCount = dailyGroupsCount
        self.dailyQuestMaxDays = dailyQuestMaxDays


class _AwardsByPlace(models.Model):
    __slots__ = ('win', 'loss', 'draw')

    def __init__(self, win, loss, draw):
        super(_AwardsByPlace, self).__init__()
        self.win = win
        self.loss = loss
        self.draw = draw

    def getAwardForWin(self, place):
        return self._getPointsByPlace(place, self.win)

    def getAwardForLoss(self, place):
        return self._getPointsByPlace(place, self.loss)

    def getAwardForDraw(self, place):
        return self._getPointsByPlace(place, self.draw)

    @classmethod
    def _getPointsByPlace(cls, place, pointsList):
        return pointsList[place] if 0 <= place < len(pointsList) else 0


class _BattleEconomyModel(models.Model):
    __slots__ = ('creditsByPlace', 'progressionPointsByPlace')

    def __init__(self, creditsByPlace, progressionPointsByPlace):
        super(_BattleEconomyModel, self).__init__()
        self.creditsByPlace = creditsByPlace
        self.progressionPointsByPlace = progressionPointsByPlace


class ControllableZonesModel(models.Model):
    __slots__ = ('autoSpotDelaySeconds', 'owned2NeutralTime', 'neutral2OwnedTime', 'progressResetFactor', 'maxHealthHealPercentage')

    def __init__(self, owned2NeutralTime, neutral2OwnedTime, progressResetFactor, maxHealthHealPercentage, autoSpotDelaySeconds):
        super(ControllableZonesModel, self).__init__()
        self.owned2NeutralTime = owned2NeutralTime
        self.neutral2OwnedTime = neutral2OwnedTime
        self.progressResetFactor = progressResetFactor
        self.maxHealthHealPercentage = maxHealthHealPercentage
        self.autoSpotDelaySeconds = autoSpotDelaySeconds


class BattleModel(models.Model):
    __slots__ = ('controllableZones',)

    def __init__(self, controllableZones):
        super(BattleModel, self).__init__()
        self.controllableZones = controllableZones


class SquadTagRestrictionModel(models.Model):
    __slots__ = ('maxCount', 'levels')

    def __init__(self, maxCount, levels):
        super(SquadTagRestrictionModel, self).__init__()
        self.maxCount = maxCount
        self.levels = levels


class SquadRestrictionsModel(models.Model):
    __slots__ = ('tags',)

    def __init__(self, tags):
        super(SquadRestrictionsModel, self).__init__()
        self.tags = tags

    def toPlatoonRestrictionsDict(self):
        return {'tags': {tag:[restriction.toDict()] for tag, restriction in self.tags.items()}}


class FortRushBattlesConfigModel(models.Model):
    __slots__ = ('modeSelectorCardColumn', 'modeSelectorCardPriority', 'isEnabled', 'technicalPause', 'startDatetime', 'endDatetime', 'isInfoPageEnabled', 'baseProgressionToken', 'completedProgressionToken', 'progressionQuestPrefix', 'maxRewardsAmountPerStage', 'progression', 'dailyMissionsConfig', 'battleEconomy', 'eligibleVehicleTiers', 'forbiddenVehClasses', 'squadRestrictions', 'battle')

    def __init__(self, modeSelectorCardColumn, modeSelectorCardPriority, isEnabled, technicalPause, startDatetime, endDatetime, isInfoPageEnabled, baseProgressionToken, completedProgressionToken, progressionQuestPrefix, maxRewardsAmountPerStage, progression, dailyMissionsConfig, battleEconomy, eligibleVehicleTiers, forbiddenVehClasses, squadRestrictions, battle):
        super(FortRushBattlesConfigModel, self).__init__()
        self.modeSelectorCardColumn = modeSelectorCardColumn
        self.modeSelectorCardPriority = modeSelectorCardPriority
        self.isEnabled = isEnabled
        self.technicalPause = technicalPause
        self.startDatetime = startDatetime
        self.endDatetime = endDatetime
        self.isInfoPageEnabled = isInfoPageEnabled
        self.baseProgressionToken = baseProgressionToken.strip()
        self.completedProgressionToken = completedProgressionToken.strip()
        self.progressionQuestPrefix = progressionQuestPrefix
        self.maxRewardsAmountPerStage = maxRewardsAmountPerStage
        self.progression = progression
        self.dailyMissionsConfig = dailyMissionsConfig
        self.battleEconomy = battleEconomy
        self.eligibleVehicleTiers = eligibleVehicleTiers
        self.forbiddenVehClasses = forbiddenVehClasses
        self.squadRestrictions = squadRestrictions
        self.battle = battle


_stageSchema = schemas.Schema(fields={'quest': fields.NonEmptyString(required=True),
 'level': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=StageModel, checkUnknown=True)
_progressionSchema = schemas.Schema(fields={'stage': fields.UniCapList(fieldOrSchema=_stageSchema, required=True, deserializedValidators=validate.Length(minValue=1))}, modelClass=ProgressionModel, checkUnknown=True)
_dailyMissionsConfigSchema = schemas.Schema(fields={'dailyMissionQuestPrefix': fields.NonEmptyString(required=True),
 'hardDailyMissionQuestPrefix': fields.NonEmptyString(required=True),
 'dailyMissionTokenPrefix': fields.NonEmptyString(required=True),
 'dailyMissionTokenPostfix': fields.NonEmptyString(required=True),
 'dailyMissionTokenTtl': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'tokenLimit': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'dailyGroupsCount': fields.Integer(required=True),
 'dailyQuestMaxDays': fields.Integer(required=True)}, modelClass=DailyMissionsConfigModel, checkUnknown=True)

def _createAwardsForPlaceList():
    return fields.ListFromString(field=fields.Integer(deserializedValidators=validate.Range(minValue=0)))


_awardsByPlaceSchema = schemas.Schema(fields={'win': _createAwardsForPlaceList(),
 'loss': _createAwardsForPlaceList(),
 'draw': _createAwardsForPlaceList()}, modelClass=_AwardsByPlace, checkUnknown=True)
_battleEconomySchema = schemas.Schema(fields={'creditsByPlace': fields.Nested(schema=_awardsByPlaceSchema, required=True),
 'progressionPointsByPlace': fields.Nested(schema=_awardsByPlaceSchema, required=True)}, modelClass=_BattleEconomyModel, checkUnknown=True)
_controllableZonesSchema = schemas.Schema[ControllableZonesModel](fields={'autoSpotDelaySeconds': fields.Float(required=False, default=2, filterParams=GameParamsScopeFlags.CELL_ARENA),
 'owned2NeutralTime': fields.Integer(required=True, filterParams=GameParamsScopeFlags.CELL_ARENA),
 'neutral2OwnedTime': fields.Integer(required=True, filterParams=GameParamsScopeFlags.CELL_ARENA),
 'progressResetFactor': fields.Float(required=True, filterParams=GameParamsScopeFlags.CELL_ARENA),
 'maxHealthHealPercentage': fields.Float(required=True, filterParams=GameParamsScopeFlags.CELL_ARENA, deserializedValidators=validate.Range(minValue=0, maxValue=1))}, modelClass=ControllableZonesModel, checkUnknown=False)
_squadTagRestrictionSchema = schemas.Schema[SquadTagRestrictionModel](fields={'maxCount': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'levels': fields.ListFromString(field=fields.Integer(deserializedValidators=validate.Range(minValue=MIN_VEHICLE_LEVEL, maxValue=MAX_VEHICLE_LEVEL)), required=True)}, modelClass=SquadTagRestrictionModel, checkUnknown=True)
_squadRestrictionsSchema = schemas.Schema[SquadRestrictionsModel](fields={'tags': fields.Dict(keyFieldOrSchema=fields.NonEmptyString(), valueFieldOrSchema=fields.Nested(schema=_squadTagRestrictionSchema), required=False)}, modelClass=SquadRestrictionsModel, checkUnknown=False)
_battleSchema = schemas.Schema[BattleModel](fields={'controllableZones': fields.Nested(schema=_controllableZonesSchema, required=False, filterParams=GameParamsScopeFlags.CELL_ARENA)}, modelClass=BattleModel, checkUnknown=False)
fortRushBattlesConfigGameParamsSchema = GameParamsSchema[FortRushBattlesConfigModel](gameParamsKey=EXT_GAME_PARAMS_KEY, fields={'modeSelectorCardColumn': fields.Integer(required=False, default=_DEFAULT_MODE_SELECTOR_COLUMN, deserializedValidators=validate.Range(minValue=0, maxValue=3)),
 'modeSelectorCardPriority': fields.Integer(required=False, default=_DEFAULT_MODE_SELECTOR_PRIORITY),
 'isEnabled': fields.Boolean(required=True),
 'technicalPause': fields.Boolean(required=True),
 'startDatetime': fields.DateTime(required=True),
 'endDatetime': fields.DateTime(required=True),
 'isInfoPageEnabled': fields.Boolean(required=True),
 'baseProgressionToken': fields.String(required=True),
 'completedProgressionToken': fields.String(required=True),
 'progressionQuestPrefix': fields.NonEmptyString(required=True),
 'maxRewardsAmountPerStage': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'progression': fields.Nested(schema=_progressionSchema, required=True),
 'dailyMissionsConfig': fields.Nested(schema=_dailyMissionsConfigSchema, required=True),
 'battleEconomy': fields.Nested(schema=_battleEconomySchema, required=True),
 'eligibleVehicleTiers': fields.ListFromString(field=fields.Integer(deserializedValidators=validate.Range(minValue=MIN_VEHICLE_LEVEL, maxValue=MAX_VEHICLE_LEVEL)), required=True),
 'forbiddenVehClasses': fields.ListFromString(field=fields.String(deserializedValidators=validate.OneOf(_VEHICLE_CLASSES)), required=False, default=list),
 'squadRestrictions': fields.Nested(schema=_squadRestrictionsSchema, required=False, filterParams=GameParamsScopeFlags.CLIENT),
 'battle': fields.Nested(schema=_battleSchema, required=False, filterParams=GameParamsScopeFlags.CELL_ARENA)}, modelClass=FortRushBattlesConfigModel, checkUnknown=False, usedInReplay=True)

def getControllableZonesConfig(arena):
    config = fortRushBattlesConfigGameParamsSchema.getModel(arena=arena)
    return None if config is None or config.battle is None else config.battle.controllableZones
