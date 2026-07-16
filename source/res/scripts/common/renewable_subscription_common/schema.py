# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/renewable_subscription_common/schema.py
from __future__ import absolute_import
import logging
import typing
import constants
from account_shared import validateCustomizationItem
from battle_pass_integration import getAllIntergatedGameModes
from constants import ARENA_BONUS_TYPE_NAMES, IS_CLIENT, VEHICLE_CLASSES, MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from dict2model import fields as d2m_fields, models, schemas, validate, exceptions
from game_params_common.schema import GameParamsSchema
from game_params_common.scope import GameParamsScopeFlags, clientFilter
from items import vehicles
_logger = logging.getLogger(__name__)

class Features(object):
    BATTLE_BONUSES = 1
    BADGES = 2
    EXCLUDED_MAP = 3
    GOLD_RESERVE = 4
    PRO_BOOST = 5
    FREE_EQUIPMENT_DEMOUNTING = 6
    PASSIVE_CREW_XP = 7
    DAILY_ATTENDANCE = 8
    ADDITIONAL_XP = 9
    EXCLUSIVE_VEHICLE = 10
    OPTIONAL_DEVICES_ASSISTANT = 11
    CREW_ASSISTANT = 12
    BATTLE_PASS = 13
    SERVICE_RECORD_CUSTOMIZATION = 14
    ALL = (BATTLE_BONUSES,
     BADGES,
     EXCLUDED_MAP,
     GOLD_RESERVE,
     PRO_BOOST,
     FREE_EQUIPMENT_DEMOUNTING,
     PASSIVE_CREW_XP,
     DAILY_ATTENDANCE,
     ADDITIONAL_XP,
     EXCLUSIVE_VEHICLE,
     OPTIONAL_DEVICES_ASSISTANT,
     CREW_ASSISTANT,
     BATTLE_PASS,
     SERVICE_RECORD_CUSTOMIZATION)


def _checkUniqListItems(modelsList, fieldGetter):
    keys = set()
    duplicates = set()
    for m in modelsList:
        arenaBonusType = fieldGetter(m)
        if arenaBonusType in keys:
            duplicates.add(arenaBonusType)
        keys.add(arenaBonusType)

    if duplicates:
        raise exceptions.ValidationError('Duplicate names: {}'.format(duplicates))


def _validateVehicle(strDescriptor):
    vehCD = vehicles.makeVehicleTypeCompDescrByName(strDescriptor)
    if not vehCD:
        raise exceptions.ValidationError('Unknown vehicle: {}'.format(strDescriptor))


def _validateStyle(styleId):
    customizationData = {'value': 1,
     'custType': 'style',
     'id': styleId}
    isValid, item = validateCustomizationItem(customizationData)
    if not isValid:
        raise exceptions.ValidationError('Unknown style: {}'.format(item))


class _CustomCompensation(models.Model):
    __slots__ = ('credits', 'gold')

    def __init__(self, credits, gold):
        super(_CustomCompensation, self).__init__()
        self.credits = credits
        self.gold = gold


_customCompensationSchema = schemas.Schema(fields={'credits': d2m_fields.Integer(required=True, default=0, deserializedValidators=validate.Range(minValue=0, maxValue=100000)),
 'gold': d2m_fields.Integer(required=True, default=0, deserializedValidators=validate.Range(minValue=0, maxValue=4000))}, modelClass=_CustomCompensation, checkUnknown=True)

class _Customization(models.Model):
    __slots__ = ('styleId', 'customCompensation')

    def __init__(self, styleId, customCompensation):
        super(_Customization, self).__init__()
        self.styleId = styleId
        self.customCompensation = customCompensation


_customizationSchema = schemas.Schema(fields={'styleId': d2m_fields.Integer(required=True, default=0, deserializedValidators=_validateStyle),
 'customCompensation': d2m_fields.Nested(_customCompensationSchema, required=True)}, modelClass=_Customization, checkUnknown=True)

class _ExclusiveVehicle(models.Model):
    __slots__ = ('vehicleName', 'noCrew', 'customization', '_vehicleIntCD')

    def __init__(self, vehicleName, noCrew, customization):
        super(_ExclusiveVehicle, self).__init__()
        self.vehicleName = vehicleName
        self.noCrew = noCrew
        self.customization = customization
        self._vehicleIntCD = vehicles.makeVehicleTypeCompDescrByName(vehicleName)

    def getVehicleIntCD(self):
        return self._vehicleIntCD


_exclusiveVehicleSchema = schemas.Schema(fields={'vehicleName': d2m_fields.String(required=True, deserializedValidators=[_validateVehicle]),
 'noCrew': d2m_fields.Boolean(required=False, default=True),
 'customization': d2m_fields.Nested(_customizationSchema, required=False)}, modelClass=_ExclusiveVehicle, checkUnknown=True)

class _FeatureModel(models.Model):
    __slots__ = ('enabled', '_available')

    def __init__(self, enabled, *args, **kwargs):
        super(_FeatureModel, self).__init__(*args, **kwargs)
        self.enabled = enabled
        self._available = False

    @property
    def available(self):
        return self._available

    def setAvailable(self, value):
        self._available = value

    def getFeatureID(self):
        raise NotImplementedError


class _TierFeatureModel(models.Model):
    __slots__ = ('name', 'overriddenParams')
    _FORBIDDEN_PARAMS = ('enabled',)

    def __init__(self, name, overriddenParams):
        super(_TierFeatureModel, self).__init__()
        self.name = name
        self.overriddenParams = overriddenParams

    @classmethod
    def validateOverrideFields(cls, oParams):
        intersected = set()
        for paramName in oParams:
            if paramName in cls._FORBIDDEN_PARAMS:
                intersected.add(paramName)

        if intersected:
            raise exceptions.ValidationError('Parameters forbidden for overriding are detected:"{}"'.format(intersected))


_tierFeatureSchema = schemas.Schema(fields={'name': d2m_fields.String(required=True),
 'overriddenParams': d2m_fields.Field(required=False, default={}, deserializedValidators=[_TierFeatureModel.validateOverrideFields])}, modelClass=_TierFeatureModel, checkUnknown=True)

class _TierModel(models.Model):
    __slots__ = ('id', 'productCodes', 'productEnabledForSteam', 'features')

    def __init__(self, id, productCodes, productEnabledForSteam, features):
        super(_TierModel, self).__init__()
        self.id = id
        self.productCodes = productCodes
        self.productEnabledForSteam = productEnabledForSteam
        self.features = features

    @classmethod
    def checkUniqFeatures(cls, modelsList):
        _checkUniqListItems(modelsList, lambda model: model.name)


_tierSchema = schemas.Schema(fields={'id': d2m_fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'productCodes': d2m_fields.UniCapList(fieldOrSchema=d2m_fields.String(required=True, deserializedValidators=[validate.Regexp('^(?!\\s*$).+'), validate.Length(minValue=1)]), required=False),
 'productEnabledForSteam': d2m_fields.Boolean(required=False, default=False),
 'features': d2m_fields.UniCapList(_tierFeatureSchema, required=True, deserializedValidators=[validate.Length(minValue=1), _TierModel.checkUniqFeatures])}, modelClass=_TierModel, checkUnknown=True)

class _BonusFactors(models.Model):
    __slots__ = ('xpFactor', 'creditsFactor', 'crewXPFactor', 'freeXPFactor')

    def __init__(self, xpFactor, creditsFactor, crewXPFactor, freeXPFactor):
        super(_BonusFactors, self).__init__()
        self.xpFactor = xpFactor
        self.creditsFactor = creditsFactor
        self.crewXPFactor = crewXPFactor
        self.freeXPFactor = freeXPFactor


_bonusFactorsSchema = schemas.Schema(fields={'xpFactor': d2m_fields.Float(required=False, default=0.0, deserializedValidators=validate.Range(minValue=0.0, maxValue=1.0)),
 'creditsFactor': d2m_fields.Float(required=False, default=0.0, deserializedValidators=validate.Range(minValue=0.0, maxValue=1.0)),
 'crewXPFactor': d2m_fields.Float(required=False, default=0.0, deserializedValidators=validate.Range(minValue=0.0, maxValue=1.0)),
 'freeXPFactor': d2m_fields.Float(required=False, default=0.0, deserializedValidators=validate.Range(minValue=0.0, maxValue=1.0))}, modelClass=_BonusFactors, checkUnknown=True)

class _BattleBonusesFeatureModel(_FeatureModel):
    __slots__ = ('bonusFactors',)

    def __init__(self, enabled, bonusFactors):
        super(_BattleBonusesFeatureModel, self).__init__(enabled)
        self.bonusFactors = bonusFactors

    def getFeatureID(self):
        return Features.BATTLE_BONUSES


_battleBonusesFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(required=True),
 'bonusFactors': d2m_fields.Nested(_bonusFactorsSchema, required=False)}, modelClass=_BattleBonusesFeatureModel, checkUnknown=True)

class _BadgesFeatureModel(_FeatureModel):
    __slots__ = ('badgeIDs',)

    def __init__(self, enabled, badgeIDs):
        super(_BadgesFeatureModel, self).__init__(enabled)
        self.badgeIDs = badgeIDs

    def getFeatureID(self):
        return Features.BADGES


_badgesFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(required=True),
 'badgeIDs': d2m_fields.UniCapList(fieldOrSchema=d2m_fields.Integer(required=True), required=False, default=list)}, modelClass=_BadgesFeatureModel, checkUnknown=True)

class _ExcludedMapFeatureModel(_FeatureModel):
    __slots__ = ('count',)

    def __init__(self, enabled, count):
        super(_ExcludedMapFeatureModel, self).__init__(enabled)
        self.count = count

    def getFeatureID(self):
        return Features.EXCLUDED_MAP


_excludedMapFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(required=True),
 'count': d2m_fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=_ExcludedMapFeatureModel, checkUnknown=True)

class _ReserveGainsPerBattle(models.Model):
    __slots__ = ('arenaBonusType', 'win', 'loss', 'draw', 'minLevel', 'minTop', 'topType')

    def __init__(self, arenaBonusType, win, loss, draw, minLevel, minTop, topType):
        super(_ReserveGainsPerBattle, self).__init__()
        self.arenaBonusType = arenaBonusType
        self.win = win
        self.loss = loss
        self.draw = draw
        self.minLevel = minLevel
        self.minTop = minTop
        self.topType = topType


_reserveGainsPerBattleTypeSchema = schemas.Schema(fields={'arenaBonusType': d2m_fields.String(required=True, deserializedValidators=[validate.OneOf(ARENA_BONUS_TYPE_NAMES.keys())]),
 'win': d2m_fields.Integer(required=False, filterParams=GameParamsScopeFlags.BASE),
 'loss': d2m_fields.Integer(required=False, filterParams=GameParamsScopeFlags.BASE),
 'draw': d2m_fields.Integer(required=False, filterParams=GameParamsScopeFlags.BASE),
 'minLevel': d2m_fields.Integer(required=False, default=0, filterParams=GameParamsScopeFlags.BASE),
 'minTop': d2m_fields.Integer(required=False, default=-1, filterParams=GameParamsScopeFlags.BASE),
 'topType': d2m_fields.String(required=False, default='fareTeamXPPosition', filterParams=GameParamsScopeFlags.BASE)}, modelClass=_ReserveGainsPerBattle, checkUnknown=True)

class _GoldReserveFeatureModel(_FeatureModel):
    __slots__ = ('maxCapacity', 'reserveGainsPerBattleType')

    def __init__(self, enabled, maxCapacity, reserveGainsPerBattleType):
        super(_GoldReserveFeatureModel, self).__init__(enabled)
        self.maxCapacity = maxCapacity
        self.reserveGainsPerBattleType = reserveGainsPerBattleType

    def getArenaTypeToGain(self):
        dataAsDict = {}
        for r in self.reserveGainsPerBattleType:
            rDict = r.toDict()
            arenaBonusType = rDict.pop('arenaBonusType')
            dataAsDict[arenaBonusType] = rDict

        return dataAsDict

    @classmethod
    def checkUniqArenaBonusTypes(cls, modelsList):
        _checkUniqListItems(modelsList, lambda model: model.arenaBonusType)

    def getFeatureID(self):
        return Features.GOLD_RESERVE


_goldReserveFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(required=True),
 'maxCapacity': d2m_fields.Integer(required=True),
 'reserveGainsPerBattleType': d2m_fields.UniCapList(required=False, default=list, fieldOrSchema=_reserveGainsPerBattleTypeSchema, deserializedValidators=[_GoldReserveFeatureModel.checkUniqArenaBonusTypes])}, modelClass=_GoldReserveFeatureModel, checkUnknown=True)

class _CompatibleVehicles(models.Model):
    __slots__ = ('tankClass', 'excludedLevels')

    def __init__(self, tankClass, excludedLevels):
        super(_CompatibleVehicles, self).__init__()
        self.tankClass = tankClass
        self.excludedLevels = excludedLevels


_compatibleVehiclesSchema = schemas.Schema(fields={'tankClass': d2m_fields.String(required=True, deserializedValidators=[validate.OneOf(VEHICLE_CLASSES)]),
 'excludedLevels': d2m_fields.UniCapList(fieldOrSchema=d2m_fields.Integer(required=True, deserializedValidators=validate.Range(minValue=MIN_VEHICLE_LEVEL, maxValue=MAX_VEHICLE_LEVEL)), required=True, default=list)}, modelClass=_CompatibleVehicles, checkUnknown=True)

class _ProBoostFeatureModel(_FeatureModel):
    __slots__ = ('applicableVehiclesLimit', 'cooldown', 'bonusFactors', 'excludedTags', 'compatibleVehicles')

    def __init__(self, enabled, applicableVehiclesLimit, cooldown, bonusFactors, excludedTags, compatibleVehicles):
        super(_ProBoostFeatureModel, self).__init__(enabled)
        self.applicableVehiclesLimit = applicableVehiclesLimit
        self.cooldown = cooldown
        self.bonusFactors = bonusFactors
        self.excludedTags = excludedTags
        self.compatibleVehicles = compatibleVehicles

    @classmethod
    def checkUniqueTankClasses(cls, modelsList):
        _checkUniqListItems(modelsList, lambda model: model.tankClass)

    def getFeatureID(self):
        return Features.PRO_BOOST


_proBoostFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(required=True),
 'applicableVehiclesLimit': d2m_fields.Integer(required=True, default=1),
 'cooldown': d2m_fields.Integer(required=True, default=0),
 'bonusFactors': d2m_fields.Nested(_bonusFactorsSchema, required=False),
 'excludedTags': d2m_fields.UniCapList(fieldOrSchema=d2m_fields.String(required=True), required=True, default=list),
 'compatibleVehicles': d2m_fields.UniCapList(required=False, default=list, fieldOrSchema=_compatibleVehiclesSchema, deserializedValidators=[_ProBoostFeatureModel.checkUniqueTankClasses])}, modelClass=_ProBoostFeatureModel, checkUnknown=True)

class _FreeEquipmentDemountingFeatureModel(_FeatureModel):
    __slots__ = ('deluxeEnabled',)

    def __init__(self, enabled, deluxeEnabled):
        super(_FreeEquipmentDemountingFeatureModel, self).__init__(enabled)
        self.deluxeEnabled = deluxeEnabled

    def getFeatureID(self):
        return Features.FREE_EQUIPMENT_DEMOUNTING


_freeEquipmentDemountingFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(),
 'deluxeEnabled': d2m_fields.Boolean()}, modelClass=_FreeEquipmentDemountingFeatureModel, checkUnknown=True)

class _PassiveCrewXPFeatureModel(_FeatureModel):
    __slots__ = ('xpPerMinute',)

    def __init__(self, enabled, xpPerMinute):
        super(_PassiveCrewXPFeatureModel, self).__init__(enabled)
        self.xpPerMinute = xpPerMinute

    def getFeatureID(self):
        return Features.PASSIVE_CREW_XP


_passiveCrewXPFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(),
 'xpPerMinute': d2m_fields.Float()}, modelClass=_PassiveCrewXPFeatureModel, checkUnknown=True)

class _DailyAttendanceFeatureModel(_FeatureModel):
    __slots__ = ('questPrefix',)

    def __init__(self, enabled, questPrefix):
        super(_DailyAttendanceFeatureModel, self).__init__(enabled)
        self.questPrefix = questPrefix

    def getFeatureID(self):
        return Features.DAILY_ATTENDANCE


_dailyAttendanceFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(required=True),
 'questPrefix': d2m_fields.String(required=True, deserializedValidators=[validate.Length(minValue=1)])}, modelClass=_DailyAttendanceFeatureModel, checkUnknown=True)

class _AdditionalXPBonusFeatureModel(_FeatureModel):
    __slots__ = ('applyCount',)

    def __init__(self, enabled, applyCount):
        super(_AdditionalXPBonusFeatureModel, self).__init__(enabled)
        self.applyCount = applyCount

    def getFeatureID(self):
        return Features.ADDITIONAL_XP


_additionalXPBonusFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(),
 'applyCount': d2m_fields.Integer()}, modelClass=_AdditionalXPBonusFeatureModel, checkUnknown=True)

class _ExclusiveVehicleFeatureModel(_FeatureModel):
    __slots__ = ('enabled', 'exclusiveVehicles')

    def __init__(self, enabled, exclusiveVehicles):
        super(_ExclusiveVehicleFeatureModel, self).__init__(enabled)
        self.exclusiveVehicles = exclusiveVehicles

    def getFeatureID(self):
        return Features.EXCLUSIVE_VEHICLE


_exclusiveVehicleFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(),
 'exclusiveVehicles': d2m_fields.UniCapList(required=False, default=list, fieldOrSchema=_exclusiveVehicleSchema)}, modelClass=_ExclusiveVehicleFeatureModel, checkUnknown=True)

class _OptionalDevicesAssistantFeature(_FeatureModel):

    def getFeatureID(self):
        return Features.OPTIONAL_DEVICES_ASSISTANT


_optionalDevicesAssistantFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean()}, modelClass=_OptionalDevicesAssistantFeature, checkUnknown=True)

class _CrewAssistantFeature(_FeatureModel):

    def getFeatureID(self):
        return Features.CREW_ASSISTANT


_crewAssistantFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean()}, modelClass=_CrewAssistantFeature, checkUnknown=True)

class _BattlePassFeature(_FeatureModel):
    __slots__ = ('points', '_bonusTypeToPoints')

    def __init__(self, enabled, points):
        super(_BattlePassFeature, self).__init__(enabled)
        self.points = points
        self._bonusTypeToPoints = {self._getArenaBonusTypeIdByName(p):p for p in points}

    def getFeatureID(self):
        return Features.BATTLE_PASS

    def getVehiclePointListsForMode(self, bonusType, vehTypeCompDescr):
        bonusTypePoints = self._bonusTypeToPoints.get(bonusType)
        if not bonusTypePoints:
            empty = tuple()
            return (empty, empty)
        return bonusTypePoints.getPointsForVehicle(vehTypeCompDescr)

    @classmethod
    def checkUniqArenaBonusTypes(cls, modelsList):
        _checkUniqListItems(modelsList, lambda model: model.arenaBonusType)

    @classmethod
    def checkBPIntegratedModes(cls, modelsList):
        incommingModes = {cls._getArenaBonusTypeIdByName(model) for model in modelsList}
        allowedIntegrations = set(getAllIntergatedGameModes())
        diff = incommingModes.difference(allowedIntegrations)
        if diff:
            raise exceptions.ValidationError('[BattlePass] Integrations must be defined for the following game modes: "{}".'.format(diff))

    @classmethod
    def _getArenaBonusTypeIdByName(cls, model):
        return ARENA_BONUS_TYPE_NAMES[model.arenaBonusType]


def _createBPpointsListField():
    return d2m_fields.ListFromString(field=d2m_fields.Integer(deserializedValidators=validate.Range(minValue=0, maxValue=9999)))


class _BPpointsOverride(models.Model):
    __slots__ = ('vehicle', 'win', 'loss')

    def __init__(self, vehicle, win, loss):
        super(_BPpointsOverride, self).__init__()
        self.vehicle, self.win, self.loss = vehicle, win, loss


_bpPointsOverrideSchema = schemas.Schema(fields={'vehicle': d2m_fields.String(required=True, deserializedValidators=[_validateVehicle]),
 'win': _createBPpointsListField(),
 'loss': _createBPpointsListField()}, modelClass=_BPpointsOverride, checkUnknown=True)

class _BPpoints(models.Model):
    __slots__ = ('arenaBonusType', 'win', 'loss', 'overrides', '_vehicleIntCDtoPoints')

    def __init__(self, arenaBonusType, win, loss, overrides):
        super(_BPpoints, self).__init__()
        self.arenaBonusType, self.win, self.loss = arenaBonusType, win, loss
        self.overrides = overrides
        self._vehicleIntCDtoPoints = {vehicles.makeVehicleTypeCompDescrByName(ovr.vehicle):ovr for ovr in overrides}

    def getPointsForVehicle(self, vehTypeCompDescr):
        pointsOverride = self._vehicleIntCDtoPoints.get(vehTypeCompDescr)
        return (pointsOverride.win, pointsOverride.loss) if pointsOverride else (self.win, self.loss)


_bpPointsSchema = schemas.Schema(fields={'arenaBonusType': d2m_fields.String(required=True, deserializedValidators=[validate.OneOf(ARENA_BONUS_TYPE_NAMES.keys())]),
 'win': _createBPpointsListField(),
 'loss': _createBPpointsListField(),
 'overrides': d2m_fields.UniCapList(required=False, default=list, fieldOrSchema=_bpPointsOverrideSchema)}, modelClass=_BPpoints, checkUnknown=True)
_battlePassFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean(),
 'points': d2m_fields.UniCapList(required=False, default=list, fieldOrSchema=_bpPointsSchema, deserializedValidators=[_BattlePassFeature.checkUniqArenaBonusTypes, _BattlePassFeature.checkBPIntegratedModes])}, modelClass=_BattlePassFeature, checkUnknown=True)

class _ServiceRecordCustomizationFeature(_FeatureModel):

    def getFeatureID(self):
        return Features.SERVICE_RECORD_CUSTOMIZATION


_serviceRecordCustomizationFeatureSchema = schemas.Schema(fields={'enabled': d2m_fields.Boolean()}, modelClass=_ServiceRecordCustomizationFeature, checkUnknown=True)

class _SubscriptionFeaturesModel(models.Model):
    __slots__ = ('goldReserveFeature', 'excludedMapFeature', 'badgesFeature', 'battleBonusesFeature', 'freeEquipmentDemountingFeature', 'passiveCrewXPFeature', 'dailyAttendanceFeature', 'additionalXPBonusFeature', 'exclusiveVehicleFeature', 'proBoostFeature', 'optionalDevicesAssistantFeature', 'crewAssistantFeature', 'battlePassFeature', 'serviceRecordCustomizationFeature', '_availableFeatures')

    def __init__(self, goldReserveFeature, excludedMapFeature, badgesFeature, battleBonusesFeature, freeEquipmentDemountingFeature, passiveCrewXPFeature, dailyAttendanceFeature, additionalXPBonusFeature, exclusiveVehicleFeature, proBoostFeature, optionalDevicesAssistantFeature, crewAssistantFeature, battlePassFeature, serviceRecordCustomizationFeature):
        super(_SubscriptionFeaturesModel, self).__init__()
        self.goldReserveFeature = goldReserveFeature
        self.excludedMapFeature = excludedMapFeature
        self.badgesFeature = badgesFeature
        self.battleBonusesFeature = battleBonusesFeature
        self.freeEquipmentDemountingFeature = freeEquipmentDemountingFeature
        self.passiveCrewXPFeature = passiveCrewXPFeature
        self.dailyAttendanceFeature = dailyAttendanceFeature
        self.additionalXPBonusFeature = additionalXPBonusFeature
        self.exclusiveVehicleFeature = exclusiveVehicleFeature
        self.proBoostFeature = proBoostFeature
        self.optionalDevicesAssistantFeature = optionalDevicesAssistantFeature
        self.crewAssistantFeature = crewAssistantFeature
        self.battlePassFeature = battlePassFeature
        self.serviceRecordCustomizationFeature = serviceRecordCustomizationFeature
        self._availableFeatures = None
        return

    def getAvailableFeatures(self):
        if not self._availableFeatures:
            featuresList = []
            for aName in dir(self):
                attr = getattr(self, aName)
                if isinstance(attr, _FeatureModel):
                    if attr.enabled and attr.available:
                        featuresList.append(attr.getFeatureID())

            self._availableFeatures = frozenset(featuresList)
        return self._availableFeatures


_SubscriptionFeaturesModelType = typing.TypeVar('_SubscriptionFeaturesModelType', bound=_SubscriptionFeaturesModel)

class _SubscriptionFeaturesSchema(GameParamsSchema[_SubscriptionFeaturesModelType]):

    def __init__(self, fields=None, modelClass=_SubscriptionFeaturesModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None, readers=None):
        defaultFields = {'goldReserveFeature': d2m_fields.Nested(_goldReserveFeatureSchema),
         'excludedMapFeature': d2m_fields.Nested(_excludedMapFeatureSchema),
         'badgesFeature': d2m_fields.Nested(_badgesFeatureSchema),
         'battleBonusesFeature': d2m_fields.Nested(_battleBonusesFeatureSchema),
         'freeEquipmentDemountingFeature': d2m_fields.Nested(_freeEquipmentDemountingFeatureSchema),
         'dailyAttendanceFeature': d2m_fields.Nested(_dailyAttendanceFeatureSchema),
         'passiveCrewXPFeature': d2m_fields.Nested(_passiveCrewXPFeatureSchema),
         'additionalXPBonusFeature': d2m_fields.Nested(_additionalXPBonusFeatureSchema),
         'exclusiveVehicleFeature': d2m_fields.Nested(_exclusiveVehicleFeatureSchema),
         'proBoostFeature': d2m_fields.Nested(_proBoostFeatureSchema),
         'optionalDevicesAssistantFeature': d2m_fields.Nested(_optionalDevicesAssistantFeatureSchema),
         'crewAssistantFeature': d2m_fields.Nested(_crewAssistantFeatureSchema),
         'battlePassFeature': d2m_fields.Nested(_battlePassFeatureSchema),
         'serviceRecordCustomizationFeature': d2m_fields.Nested(_serviceRecordCustomizationFeatureSchema)}
        if fields:
            defaultFields.update(fields)
        if not readers:
            readers = {}
        super(_SubscriptionFeaturesSchema, self).__init__(constants.Configs.RENEWABLE_SUBSCRIPTION_CONFIG.value, defaultFields, modelClass, checkUnknown, serializedValidators, deserializedValidators, readers)


_subscriptionFeaturesSchema = _SubscriptionFeaturesSchema(checkUnknown=False)

class _SubscriptionFullModel(_SubscriptionFeaturesModel):
    __slots__ = ('enabled', 'enabledForSteam', 'tiers', '_overriddenTiers', '_tierProductCodes')

    def __init__(self, enabled, enabledForSteam, goldReserveFeature, excludedMapFeature, badgesFeature, battleBonusesFeature, freeEquipmentDemountingFeature, passiveCrewXPFeature, dailyAttendanceFeature, additionalXPBonusFeature, exclusiveVehicleFeature, proBoostFeature, optionalDevicesAssistantFeature, crewAssistantFeature, tiers, battlePassFeature, serviceRecordCustomizationFeature):
        super(_SubscriptionFullModel, self).__init__(goldReserveFeature, excludedMapFeature, badgesFeature, battleBonusesFeature, freeEquipmentDemountingFeature, passiveCrewXPFeature, dailyAttendanceFeature, additionalXPBonusFeature, exclusiveVehicleFeature, proBoostFeature, optionalDevicesAssistantFeature, crewAssistantFeature, battlePassFeature, serviceRecordCustomizationFeature)
        self.enabled = enabled
        self.enabledForSteam = enabledForSteam
        self.tiers = tiers
        self._overriddenTiers = self._initOverriddenTiers()
        self._tierProductCodes = self._initTierSubscriptionCodes()

    def getAllProductCodes(self):
        return [ productCode for tier in self.tiers for productCode in tier.productCodes ]

    def getTierProductCodes(self, tierID):
        return self._tierProductCodes.get(tierID, [])

    def getTierSettingsById(self, tierID):
        return self._overriddenTiers.get(tierID)

    def _initOverriddenTiers(self):
        overriddenTiers = {}
        errors = None
        for tier in self.tiers:
            try:
                filter = clientFilter if IS_CLIENT else None
                dataAsDict = renewableSubscriptionsConfigSchema.serialize(self, filter_=filter)
                for feature in tier.features:
                    featureModelAsDict = dataAsDict.get(feature.name)
                    if not featureModelAsDict:
                        raise exceptions.ValidationError('Tier id={} contains undeclared feature {}'.format(tier.id, feature.name))
                    dataAsDict[feature.name].update(feature.overriddenParams)

                overriddenTierModel = _subscriptionFeaturesSchema.deserialize(dataAsDict)
                for feature in tier.features:
                    getattr(overriddenTierModel, feature.name).setAvailable(True)

                overriddenTiers[tier.id] = overriddenTierModel
            except exceptions.ValidationError as ve:
                error = exceptions.ValidationErrorMessage(ve.error.data, title='Tier({})'.format(tier.id))
                errors = errors + error if errors else error

        if errors:
            raise exceptions.ValidationError(errors)
        return overriddenTiers

    def _initTierSubscriptionCodes(self):
        return {tier.id:tier.productCodes for tier in self.tiers}


renewableSubscriptionsConfigSchema = _SubscriptionFeaturesSchema[_SubscriptionFullModel](fields={'enabled': d2m_fields.Boolean(required=True),
 'enabledForSteam': d2m_fields.Boolean(required=True),
 'tiers': d2m_fields.UniCapList(_tierSchema, required=True)}, modelClass=_SubscriptionFullModel, checkUnknown=True, deserializedValidators=None)
