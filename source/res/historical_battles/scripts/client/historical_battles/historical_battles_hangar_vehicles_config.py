# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/historical_battles_hangar_vehicles_config.py
import logging
from extension_utils import ResMgr
from items import vehicles
from constants import IS_DEVELOPMENT
_logger = logging.getLogger(__name__)
_CONFIG_FILE = 'historical_battles/gui/historical_battles_hangar_vehicles_config.xml'

class _BasicEffectsContainer(object):

    def __init__(self):
        self._effectsStorage = {}

    @property
    def effectsStorage(self):
        return self._effectsStorage

    def _prepare(self):
        self._effectsStorage.clear()

    def _extendEffectsStorage(self, newEffects):
        if newEffects:
            self._effectsStorage.update(newEffects)


class ConfigDataReader(_BasicEffectsContainer):

    def __init__(self):
        super(ConfigDataReader, self).__init__()
        self.__frontConfigs = []

    @property
    def frontConfigs(self):
        return self.__frontConfigs

    def readConfigFile(self):
        self._prepare()
        self.__frontConfigs = []
        configSection = ResMgr.openSection(_CONFIG_FILE)
        effectsReader = EffectsReader()
        effectsReader.readEffectConfigs(configSection['common_effects'])
        self._extendEffectsStorage(effectsReader.effectsStorage)
        frontsSection = configSection['fronts']
        for _, section in frontsSection.items():
            self.__readFront(section)

        if IS_DEVELOPMENT:
            self.__validateAllEffects()

    def __readFront(self, frontSection):
        frontId = len(self.frontConfigs) + 1
        reader = FrontConfigReader(frontId)
        frontConfig = reader.readFront(frontSection)
        self.frontConfigs.append(frontConfig)
        self._extendEffectsStorage(reader.effectsStorage)

    def __validateAllEffects(self):
        for front in self.frontConfigs:
            for vehConfig in front.vehicleConfigs.values():
                self.__validateObjectEffects(vehConfig)
                for customizations in vehConfig.customizations.values():
                    for custConfig in customizations:
                        self.__validateObjectEffects(custConfig)

            for slotConfig in front.layout.values():
                self.__validateObjectEffects(slotConfig)

    def __validateObjectEffects(self, objConfig):
        for effect in objConfig.effectsContainer.effects:
            if self.effectsStorage.get(effect, None) is None:
                _logger.error('The effect %s is not present in the common effects', effect)

        return


class FrontConfigReader(_BasicEffectsContainer):

    def __init__(self, frontId):
        super(FrontConfigReader, self).__init__()
        self.__frontId = frontId

    def readFront(self, frontSection):
        self._prepare()
        vehicleConfigs = {}
        vehicleNames = {}
        vehiclesSection = frontSection['vehicles']
        for _, section in vehiclesSection.items():
            vehicleConfigObject = self.__readVehicle(section)
            vehicleConfigs[vehicleConfigObject.intCD] = vehicleConfigObject
            vehicleNames[vehicleConfigObject.name] = vehicleConfigObject.intCD

        effectBasicName = self.__getEffectNamePrefix() + '_layout_'
        layoutReader = LayoutReader(effectBasicName, vehicleNames)
        layoutReader.read(frontSection['vehicles_layout'])
        self._extendEffectsStorage(layoutReader.effectsStorage)
        return FrontConfig(self.__frontId, vehicleConfigs, layoutReader.layout)

    def __readVehicle(self, vehicleSection):
        name = vehicleSection['name'].asString
        typeName = vehicleSection['type'].asString
        modelPath = vehicleSection['model'].asString
        basicNamePrefix = self.__getEffectNamePrefix() + '_' + name
        custEffectNamePrefix = basicNamePrefix + '_custom_'
        customizationReader = CustomizationsReader(custEffectNamePrefix)
        customizationReader.readCustomizations(vehicleSection['customizations'])
        self._extendEffectsStorage(customizationReader.effectsStorage)
        intCD = vehicles.makeVehicleTypeCompDescrByName(typeName)
        effectNamePrefix = basicNamePrefix + '_'
        effectsReader = EffectsReader(effectNamePrefix)
        effectsReader.readEffects(vehicleSection['effects'])
        self._extendEffectsStorage(effectsReader.effectsStorage)
        return FrontVehicleConfig(name, intCD, typeName, modelPath, effectsReader.getEffectsContainer(), customizationReader.customizations)

    def __getEffectNamePrefix(self):
        return 'front_' + str(self.__frontId)


class LayoutReader(_BasicEffectsContainer):

    def __init__(self, effectBasePrefix, vehicleNames):
        super(LayoutReader, self).__init__()
        self.__effectBasePrefix = effectBasePrefix
        self.__vehicleNames = vehicleNames
        self.layout = {}

    def read(self, layoutSection):
        self._prepare()
        for _, section in layoutSection.items():
            slotConfigObject = self.__readLayoutSlot(section)
            if IS_DEVELOPMENT:
                pass
            self.layout[slotConfigObject.vehicleIndex] = slotConfigObject

    def __readLayoutSlot(self, slotSection):
        index = slotSection['vehicleIndex'].asInt
        name = slotSection['name'].asString
        effectPrefix = self.__getEffectNamePrefix(index)
        effectsReader = EffectsReader(effectPrefix)
        effectsReader.readEffects(slotSection['effects'])
        self._extendEffectsStorage(effectsReader.effectsStorage)
        intCD = self.__vehicleNames[name]
        return LayoutSlotConfig(index, intCD, effectsReader.getEffectsContainer())

    def __getEffectNamePrefix(self, index):
        return self.__effectBasePrefix + str(index) + '_'


class CustomizationsReader(_BasicEffectsContainer):

    def __init__(self, effectNamePrefix):
        super(CustomizationsReader, self).__init__()
        self.__effectNamePrefix = effectNamePrefix
        self.customizations = {}

    def readCustomizations(self, customizationsSection):
        self._prepare()
        self.customizations.clear()
        if customizationsSection is None:
            return
        else:
            for _, section in customizationsSection.items():
                customizationObject = self.__readCustomization(section)
                customizationList = self.customizations.get(customizationObject.vehicleIndex, None)
                if customizationList is None:
                    customizationList = [customizationObject]
                    self.customizations[customizationObject.vehicleIndex] = customizationList

            return

    def __readCustomization(self, customizationSection):
        index = customizationSection['vehicleIndex'].asInt
        modelPath = customizationSection['model'].asString
        effectPrefix = self.__getEffectNamePrefix()
        effectsReader = EffectsReader(effectPrefix)
        effectsReader.readEffects(customizationSection['effects'])
        self._extendEffectsStorage(effectsReader.effectsStorage)
        return CustomizationConfig(index, modelPath, effectsReader.getEffectsContainer())

    def __getEffectNamePrefix(self):
        return self.__effectNamePrefix + 'custom_' + str(len(self.customizations) + 1) + '_'


class EffectsReader(_BasicEffectsContainer):

    def __init__(self, namePreffix=None):
        super(EffectsReader, self).__init__()
        self.__namePreffix = namePreffix
        self.__effects = []
        self.__extend = False
        self.__available = False

    def readEffects(self, effectsSection):
        self._prepare()
        self.__effects = []
        self.__available = effectsSection is not None
        if not self.__available:
            return
        else:
            self.__extend = effectsSection.has_key('extend')
            commonEffectsSection = effectsSection['common_effects']
            if commonEffectsSection is not None:
                self.__readVehicleEffects(commonEffectsSection)
            customEffectsSection = effectsSection['custom_effects']
            if customEffectsSection is not None:
                self.readEffectConfigs(customEffectsSection)
            if self._effectsStorage:
                additionalEffects = self._effectsStorage.keys()
                self.__effects.extend(additionalEffects)
            return

    def readEffectConfigs(self, section):
        for _, effectSection in section.items():
            self.__readEffectConfig(effectSection)

    def getEffectsContainer(self):
        return TankEffectsContainer(self.__available, self.__extend, self.__effects)

    def __readVehicleEffects(self, section):
        self.__effects.extend(section.asString.split())

    def __readEffectConfig(self, section):
        if self.__namePreffix:
            name = self.__namePreffix + str(len(self._effectsStorage) + 1)
        else:
            name = section['name'].asString
        hardpoint = section['hardpoint'].asString
        sequencePath = section['sequence'].asString
        effect = TankEffectConfig(name, hardpoint, sequencePath)
        if IS_DEVELOPMENT:
            pass
        self._effectsStorage[name] = effect


class FrontConfig(object):
    __slots__ = ('frontId', 'vehicleConfigs', 'layout')

    def __init__(self, frontId, vehicleConfigs, layout):
        self.frontId = frontId
        self.vehicleConfigs = vehicleConfigs
        self.layout = layout

    def getVehicleData(self, intCD, index):
        vehicleConfig = self.vehicleConfigs[intCD]
        return vehicleConfig.createVehicleDataObject(index)

    def getDefaultSlotVehicleData(self, index):
        slotConfig = self.layout.get(index, None)
        if slotConfig is None:
            _logger.error('There is no vehicle data at %d slot', index)
            return
        else:
            vehicleConfig = self.vehicleConfigs[slotConfig.intCD]
            return vehicleConfig.createVehicleDataObject(index)

    def getVehicleEffects(self, intCD, index):
        vehicleConfig = self.vehicleConfigs[intCD]
        effects, hasCustomizationEffects = vehicleConfig.getVehicleEffects(index)
        if not hasCustomizationEffects:
            slotConfig = self.layout.get(index, None)
            if slotConfig is not None:
                return slotConfig.effectsContainer.extendEffects(effects)
        return effects


class FrontVehicleConfig(object):
    __slots__ = ('name', 'intCD', 'typeName', 'modelPath', 'effectsContainer', 'customizations')

    def __init__(self, name, intCD, typeName, modelPath, effectsContainer, customizations):
        self.name = name
        self.intCD = intCD
        self.typeName = typeName
        self.modelPath = modelPath
        self.effectsContainer = effectsContainer
        self.customizations = customizations

    def createVehicleDataObject(self, index):
        customizations = self.customizations.get(index, None)
        if customizations:
            for customization in customizations:
                if customization:
                    return VehicleData(self.intCD, self.typeName, customization.modelPath)

        return VehicleData(self.intCD, self.typeName, self.modelPath)

    def getVehicleEffects(self, index):
        effects = self.effectsContainer.effects
        customizations = self.customizations.get(index, None)
        if customizations:
            for customization in customizations:
                if customization:
                    effectsContainer = customization.effectsContainer
                    return (effectsContainer.extendEffects(effects), True)

        return (effects, False)


class LayoutSlotConfig(object):
    __slots__ = ('vehicleIndex', 'intCD', 'effectsContainer')

    def __init__(self, vehicleIndex, intCD, effectsContainer):
        self.vehicleIndex = vehicleIndex
        self.intCD = intCD
        self.effectsContainer = effectsContainer


class CustomizationConfig(object):
    __slots__ = ('vehicleIndex', 'modelPath', 'effectsContainer')

    def __init__(self, vehicleIndex, modelPath, effectsContainer):
        self.vehicleIndex = vehicleIndex
        self.modelPath = modelPath
        self.effectsContainer = effectsContainer


class TankEffectsContainer(object):
    __slots__ = ('__available', 'extend', 'effects')

    def __init__(self, available, extend, effects):
        self.__available = available
        self.extend = extend
        self.effects = tuple(effects)

    def extendEffects(self, effects):
        if not self.__available:
            return effects
        return effects + self.effects if self.extend else self.effects


class TankEffectConfig(object):
    __slots__ = ('name', 'hardpoint', 'sequencePath')

    def __init__(self, name, hardpoint, sequencePath):
        self.name = name
        self.hardpoint = hardpoint
        self.sequencePath = sequencePath


class VehicleData(object):

    def __init__(self, intCD, typeName, modelPath):
        self.intCD = intCD
        self.typeName = typeName
        self.modelPath = modelPath
