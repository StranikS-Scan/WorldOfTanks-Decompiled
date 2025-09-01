# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/armor_flashlight/config.py
import typing
import BattleReplay
import ResMgr
import section2dict
from armor_flashlight_common.server_config import serverConfigSchema
from debug_utils import LOG_ERROR
from dict2model import models, schemas, fields, validate
from dict2model.exceptions import ValidationError
from dict2model.extensions.color import ColorModel, colorSchema
if typing.TYPE_CHECKING:
    from typing import Tuple
    from Math import Vector4
_CONFIG_PATH = 'gui/armor_flashlight_config.xml'
_DEFAULT_RESOLUTION_INDEX = 0
_config = None

class ArmorPiercingColorsSchemaModel(models.Model):
    __slots__ = ('notPierced', 'littlePierced', 'greatPierced')

    def __init__(self, notPierced, littlePierced, greatPierced):
        super(ArmorPiercingColorsSchemaModel, self).__init__()
        self.notPierced = notPierced
        self.littlePierced = littlePierced
        self.greatPierced = greatPierced

    def toFloats(self):
        return (self.notPierced.toFloats(), self.littlePierced.toFloats(), self.greatPierced.toFloats())

    def _reprArgs(self):
        return 'notPierced={}, littlePierced={}, greatPierced={}'.format(self.notPierced, self.littlePierced, self.greatPierced)


_armorPiercingColorsSchema = schemas.Schema(fields={'notPierced': fields.Nested(colorSchema),
 'littlePierced': fields.Nested(colorSchema),
 'greatPierced': fields.Nested(colorSchema)}, modelClass=ArmorPiercingColorsSchemaModel)

class ColorSchemaModel(models.Model):
    __slots__ = ('name', 'normal', 'colorBlindness')

    def __init__(self, name, normal, colorBlindness):
        super(ColorSchemaModel, self).__init__()
        self.name = name
        self.normal = normal
        self.colorBlindness = colorBlindness

    def _reprArgs(self):
        return 'name={}, normal={}, colorBlindness={}'.format(self.name, self.normal, self.colorBlindness)


_colorSchemaSchema = schemas.Schema(fields={'name': fields.NonEmptyString(),
 'normal': fields.Nested(_armorPiercingColorsSchema),
 'colorBlindness': fields.Nested(_armorPiercingColorsSchema)}, modelClass=ColorSchemaModel)

class PatternModel(models.Model):
    __slots__ = ('name', 'texturePath')

    def __init__(self, name, texturePath):
        super(PatternModel, self).__init__()
        self.name = name
        self.texturePath = texturePath

    def _reprArgs(self):
        return 'name={}, texturePath={}'.format(self.name, self.texturePath)


_patternSchema = schemas.Schema(fields={'name': fields.NonEmptyString(),
 'texturePath': fields.NonEmptyString()}, modelClass=PatternModel)

class DistanceConfigModel(models.Model):
    __slots__ = ('distance', 'value')

    def __init__(self, distance, value):
        super(DistanceConfigModel, self).__init__()
        self.distance = distance
        self.value = value

    def _reprArgs(self):
        return 'distance={}, value={}'.format(self.distance, self.value)

    def getTuple(self):
        return (self.distance, self.value)

    @staticmethod
    def sortedByDist(config):
        return sorted(config, key=lambda x: x.distance)


_distanceConfigSchema = schemas.Schema(fields={'distance': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=0)),
 'value': fields.Float(required=True)}, modelClass=DistanceConfigModel)

class ResolutionModel(models.Model):
    __slots__ = ('name', 'downscale')

    def __init__(self, name, downscale):
        super(ResolutionModel, self).__init__()
        self.name = name
        self.downscale = downscale

    def _reprArgs(self):
        return 'name={}, downscale={}'.format(self.name, self.downscale)


_resolutionSchema = schemas.Schema(fields={'name': fields.NonEmptyString(required=True),
 'downscale': fields.Float(required=True, deserializedValidators=validate.Range(minValue=1.0))}, modelClass=ResolutionModel)

class DefaultResolutionByPostProcessingModel(models.Model):
    __slots__ = ('postProcessingLevel', 'maxResolutionName')

    def __init__(self, postProcessingLevel, maxResolutionName):
        super(DefaultResolutionByPostProcessingModel, self).__init__()
        self.postProcessingLevel = postProcessingLevel
        self.maxResolutionName = maxResolutionName

    def _reprArgs(self):
        return 'postProcessingLevel={}, maxResolutionName={}'.format(self.postProcessingLevel, self.maxResolutionName)


_defaultResolutionByPostProcessingSchema = schemas.Schema(fields={'postProcessingLevel': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=0, maxValue=4)),
 'maxResolutionName': fields.NonEmptyString(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=DefaultResolutionByPostProcessingModel)

class ConfigModel(models.Model):
    __slots__ = ('colorSchemas', 'patterns', 'textureTilingFactor', 'alphaByDist', 'radiusByDist', 'appearanceDurationByDist', 'resolutions', 'defaultResolutionByPostProcessing', 'noiseIntensityMultiplier', 'maxSizePercentOfWindow', 'fadeoffFactorWhenNotAimed', 'borderSmoothness', 'aimingCircleAdjustment', 'smoothnessInAimingCircleAdjustment')

    def __init__(self, colorSchemas, patterns, textureTilingFactor, alphaByDist, radiusByDist, appearanceDurationByDist, resolutions, defaultResolutionByPostProcessing, noiseIntensityMultiplier, maxSizePercentOfWindow, fadeoffFactorWhenNotAimed, borderSmoothness, aimingCircleAdjustment, smoothnessInAimingCircleAdjustment):
        super(ConfigModel, self).__init__()
        self.colorSchemas = colorSchemas
        self.patterns = patterns
        self.textureTilingFactor = textureTilingFactor
        self.alphaByDist = DistanceConfigModel.sortedByDist(alphaByDist)
        self.radiusByDist = DistanceConfigModel.sortedByDist(radiusByDist)
        self.appearanceDurationByDist = DistanceConfigModel.sortedByDist(appearanceDurationByDist)
        self.resolutions = resolutions
        self.defaultResolutionByPostProcessing = defaultResolutionByPostProcessing
        self.noiseIntensityMultiplier = noiseIntensityMultiplier
        self.maxSizePercentOfWindow = maxSizePercentOfWindow
        self.fadeoffFactorWhenNotAimed = fadeoffFactorWhenNotAimed
        self.borderSmoothness = borderSmoothness
        self.aimingCircleAdjustment = aimingCircleAdjustment
        self.smoothnessInAimingCircleAdjustment = smoothnessInAimingCircleAdjustment

    def getSchemaColorFloatsByIndex(self, index, isColorBlind):
        schema = self.colorSchemas[index].colorBlindness if isColorBlind else self.colorSchemas[index].normal
        return schema.toFloats()

    def getPatternByIndex(self, index):
        return self.patterns[index].texturePath

    @staticmethod
    def getDistanceConfigTupleList(config):
        return [ item.getTuple() for item in config ]

    def getResolutionDownscaleByIndex(self, index):
        return self.resolutions[index].downscale

    def getResolutionIndexByPostProcessing(self, postProcessingLevel):
        resolution = self._getDefaultResolutionByPostProcessing(postProcessingLevel)
        return self._getResolutionIndexByName(resolution.maxResolutionName)

    def _getDefaultResolutionByPostProcessing(self, postProcessingLevel):
        for resByPostProc in self.defaultResolutionByPostProcessing:
            if resByPostProc.postProcessingLevel == postProcessingLevel:
                return resByPostProc

        LOG_ERROR('No flashlight resolution provided for post processing level {}'.format(postProcessingLevel))
        return self.defaultResolutionByPostProcessing[_DEFAULT_RESOLUTION_INDEX]

    def _getResolutionIndexByName(self, name):
        for index, resolution in enumerate(self.resolutions):
            if resolution.name == name:
                return index

        LOG_ERROR('{} resolution does not exist'.format(name))
        return _DEFAULT_RESOLUTION_INDEX

    def _reprArgs(self):
        return 'colorSchemas={}, patterns={}, textureTilingFactor={}, alphaByDist={}, radiusByDist={}, appearanceDurationByDist={}, resolutions={}, defaultResolutionByPostProcessing={}, noiseIntensityMultiplier={}, maxSizePercentOfWindow={}, fadeoffFactorWhenNotAimed={}, borderSmoothness={}, aimingCircleAdjustment={}, smoothnessInAimingCircleAdjustment={}'.format(self.colorSchemas, self.patterns, self.textureTilingFactor, self.alphaByDist, self.radiusByDist, self.appearanceDurationByDist, self.resolutions, self.defaultResolutionByPostProcessing, self.noiseIntensityMultiplier, self.maxSizePercentOfWindow, self.fadeoffFactorWhenNotAimed, self.borderSmoothness, self.aimingCircleAdjustment, self.smoothnessInAimingCircleAdjustment)


def _validateUniqueNames(items, itemType):
    names = set()
    for item in items:
        if item.name in names:
            raise ValidationError('{} name is not unique: {}.'.format(itemType, item.name))
        names.add(item.name)


def _validateColorSchemasNames(config):
    _validateUniqueNames(config.colorSchemas, 'Color Schema')


def _validatePatternsNames(config):
    _validateUniqueNames(config.patterns, 'Pattern')


def _validateResolutionNames(config):
    _validateUniqueNames(config.resolutions, 'Resolution')


def _validateMaxResolutionNames(config):
    validNames = set((resolution.name for resolution in config.resolutions))
    for resolutionByPostProcessing in config.defaultResolutionByPostProcessing:
        name = resolutionByPostProcessing.maxResolutionName
        if name not in validNames:
            raise ValidationError('maxResolutionName {} is not present is resolutions list.'.format(name))


_configSchema = schemas.Schema(fields={'colorSchemas': fields.UniCapList(_colorSchemaSchema, deserializedValidators=validate.Length(minValue=1)),
 'patterns': fields.UniCapList(_patternSchema, deserializedValidators=validate.Length(minValue=1)),
 'textureTilingFactor': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0.01)),
 'alphaByDist': fields.UniCapList(_distanceConfigSchema, deserializedValidators=validate.Length(minValue=1)),
 'radiusByDist': fields.UniCapList(_distanceConfigSchema, deserializedValidators=validate.Length(minValue=1)),
 'appearanceDurationByDist': fields.UniCapList(_distanceConfigSchema, deserializedValidators=validate.Length(minValue=1)),
 'resolutions': fields.UniCapList(_resolutionSchema, deserializedValidators=validate.Length(minValue=1)),
 'defaultResolutionByPostProcessing': fields.UniCapList(_defaultResolutionByPostProcessingSchema, deserializedValidators=validate.Length(minValue=5, maxValue=5)),
 'noiseIntensityMultiplier': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0.01)),
 'maxSizePercentOfWindow': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0.1, maxValue=100.0)),
 'fadeoffFactorWhenNotAimed': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0.01)),
 'borderSmoothness': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0.0, maxValue=1.0)),
 'aimingCircleAdjustment': fields.Float(required=True, deserializedValidators=validate.Range(minValue=0.01)),
 'smoothnessInAimingCircleAdjustment': fields.Float(required=True, deserializedValidators=validate.Range(minValue=1.0))}, modelClass=ConfigModel, deserializedValidators=[_validateColorSchemasNames,
 _validatePatternsNames,
 _validateResolutionNames,
 _validateMaxResolutionNames])

def getConfig():
    global _config
    if _config:
        return _config
    root = ResMgr.openSection(_CONFIG_PATH)
    rawData = section2dict.parse(root)
    _config = _configSchema.deserialize(rawData)
    return _config


def isFeatureEnabled():
    serverConfig = serverConfigSchema.getModel()
    return serverConfig.enabled if serverConfig is not None else BattleReplay.isPlaying()
