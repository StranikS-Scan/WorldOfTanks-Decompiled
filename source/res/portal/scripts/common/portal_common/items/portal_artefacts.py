# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common/items/portal_artefacts.py
import BigWorld
from constants import IS_CLIENT
import items.artefacts as artefacts
from items import _xml
from items.artefacts import Equipment, VehicleFactorsXmlReader, ArcadeEquipmentConfigReader, _CommonMinefieldEquipment
from items.components import component_constants

class PortalAOEEquipment(artefacts.AreaOfEffectEquipment):
    __slots__ = ()

    def _readConfig(self, xmlCtx, section):
        super(PortalAOEEquipment, self)._readConfig(xmlCtx, section)
        if IS_CLIENT:
            presetIndex = BigWorld.detectGraphicsPresetFromSystemSettings()
            lowPresetIndex = BigWorld.getSystemPerformancePresetIdFromName('LOW')
            if presetIndex >= lowPresetIndex:
                self.areaVisibleToEnemies = False

    def readSharedCooldownConsumableConfig(self, xmlCtx, section):
        pass


class BasePortalArtefact(Equipment):
    __slots__ = ('idx',)

    def __init__(self):
        super(BasePortalArtefact, self).__init__()
        self.idx = 0

    def _readConfig(self, xmlCtx, section):
        super(BasePortalArtefact, self)._readConfig(xmlCtx, section)
        self.idx = _xml.readIntOrNone(xmlCtx, section, 'idx')


class PortalVehicleChangeShot(BasePortalArtefact):
    __slots__ = ('duration', 'shellCD', 'selfVehiclePrefab', 'capturedVehiclePrefab', 'gunFirePrefab')

    def __init__(self):
        super(PortalVehicleChangeShot, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.shellCD = component_constants.ZERO_INT
        self.selfVehiclePrefab = component_constants.EMPTY_STRING
        self.capturedVehiclePrefab = component_constants.EMPTY_STRING
        self.gunFirePrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(PortalVehicleChangeShot, self)._readConfig(xmlCtx, section)
        self.duration = _xml.readInt(xmlCtx, section, 'duration')
        self.shellCD = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.selfVehiclePrefab = _xml.readString(xmlCtx, section, 'selfVehiclePrefab')
        self.capturedVehiclePrefab = _xml.readString(xmlCtx, section, 'capturedVehiclePrefab')
        self.gunFirePrefab = _xml.readString(xmlCtx, section, 'gunFirePrefab')


class PortalGuidedMissile(BasePortalArtefact):
    __slots__ = ('duration',)

    def __init__(self):
        super(PortalGuidedMissile, self).__init__()
        self.duration = component_constants.ZERO_INT


class PortalSentryGun(BasePortalArtefact, ArcadeEquipmentConfigReader):
    __slots__ = ('attackRadius', 'sentryGunVehicle', 'deployEffectDuration', 'duration') + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(PortalSentryGun, self).__init__()
        self.sentryGunVehicle = component_constants.EMPTY_STRING
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.areaColor = component_constants.ZERO_INT
        self.deployEffectDuration = component_constants.ZERO_FLOAT
        self.duration = component_constants.ZERO_INT
        self.initArcadeInformation()

    def _readConfig(self, xmlCtx, section):
        super(PortalSentryGun, self)._readConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.duration = _xml.readInt(xmlCtx, section, 'duration')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaLength = _xml.readFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readString(xmlCtx, section, 'areaVisual')
        self.sentryGunVehicle = _xml.readString(xmlCtx, section, 'sentryGunVehicle')
        self.deployEffectDuration = _xml.readFloat(xmlCtx, section, 'deployEffectDuration')


class PortalBerserk(BasePortalArtefact):
    __slots__ = ('increaseFactors', 'duration')

    def __init__(self):
        super(PortalBerserk, self).__init__()
        self.increaseFactors = component_constants.EMPTY_DICT
        self.duration = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, scriptSection):
        super(PortalBerserk, self)._readConfig(xmlCtx, scriptSection)
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, scriptSection, 'increaseFactors')
        self.duration = _xml.readInt(xmlCtx, scriptSection, 'duration')


class PortalMinefield(_CommonMinefieldEquipment):
    __slots__ = ('cooldownSeconds', 'duration', 'idx')

    def __init__(self):
        super(PortalMinefield, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.idx = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(PortalMinefield, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = self.sharedCooldownTime
        self.duration = self.mineParams.lifetime
        self.idx = _xml.readIntOrNone(xmlCtx, section, 'idx')


class PortalVehicleShield(BasePortalArtefact):
    __slots__ = ('duration',)

    def __init__(self):
        super(PortalVehicleShield, self).__init__()
        self.duration = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(PortalVehicleShield, self)._readConfig(xmlCtx, section)
        self.duration = _xml.readInt(xmlCtx, section, 'duration')


class VehicleFireShot(BasePortalArtefact):
    __slots__ = ('duration', 'gunFirePrefab', 'hitPrefab')

    def __init__(self):
        super(VehicleFireShot, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.gunFirePrefab = component_constants.EMPTY_STRING
        self.hitPrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(VehicleFireShot, self)._readConfig(xmlCtx, section)
        self.gunFirePrefab = _xml.readString(xmlCtx, section, 'gunFirePrefab')
        self.hitPrefab = _xml.readString(xmlCtx, section, 'hitPrefab')


class VehicleFrozenShot(BasePortalArtefact):
    __slots__ = ('params', 'duration', 'gunFirePrefab', 'hitPrefab')

    def __init__(self):
        super(VehicleFrozenShot, self).__init__()
        self.params = {'debuffFactors': component_constants.EMPTY_DICT,
         'debuffDuration': component_constants.ZERO_FLOAT,
         'equipmentID': component_constants.ZERO_INT}
        self.duration = self.cooldownSeconds
        self.gunFirePrefab = component_constants.EMPTY_STRING
        self.hitPrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(VehicleFrozenShot, self)._readConfig(xmlCtx, section)
        self.params['debuffDuration'] = section.readFloat('debuffDuration')
        if section.has_key('debuffFactors'):
            self.params['debuffFactors'] = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'debuffFactors')
        self.params['equipmentID'] = self.id[1]
        self.gunFirePrefab = _xml.readString(xmlCtx, section, 'gunFirePrefab')
        self.hitPrefab = _xml.readString(xmlCtx, section, 'hitPrefab')


class VehicleLaughShot(BasePortalArtefact):
    __slots__ = ('params', 'duration', 'gunFirePrefab', 'hitPrefab')

    def __init__(self):
        super(VehicleLaughShot, self).__init__()
        self.params = {'debuffFactors': component_constants.EMPTY_DICT,
         'debuffDuration': component_constants.ZERO_FLOAT,
         'equipmentID': component_constants.ZERO_INT}
        self.duration = self.cooldownSeconds
        self.gunFirePrefab = component_constants.EMPTY_STRING
        self.hitPrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(VehicleLaughShot, self)._readConfig(xmlCtx, section)
        self.params['debuffDuration'] = section.readFloat('debuffDuration')
        if section.has_key('debuffFactors'):
            self.params['debuffFactors'] = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'debuffFactors')
        self.params['equipmentID'] = self.id[1]
        self.gunFirePrefab = _xml.readString(xmlCtx, section, 'gunFirePrefab')
        self.hitPrefab = _xml.readString(xmlCtx, section, 'hitPrefab')


class VehicleCurseShot(BasePortalArtefact):
    __slots__ = ('params', 'duration', 'gunFirePrefab', 'hitPrefab')

    def __init__(self):
        super(VehicleCurseShot, self).__init__()
        self.params = {'damagedDevices': component_constants.EMPTY_DICT,
         'equipmentID': component_constants.ZERO_INT}
        self.duration = self.cooldownSeconds
        self.gunFirePrefab = component_constants.EMPTY_STRING
        self.hitPrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(VehicleCurseShot, self)._readConfig(xmlCtx, section)
        if section.has_key('damagedDevices'):
            subsection = _xml.getSubsection(xmlCtx, section, 'damagedDevices')
            devices = {}
            for device, _ in subsection.items():
                devices[device] = subsection.readFloat(device)

            self.params['damagedDevices'] = devices
        self.params['equipmentID'] = self.id[1]
        self.gunFirePrefab = _xml.readString(xmlCtx, section, 'gunFirePrefab')
        self.hitPrefab = _xml.readString(xmlCtx, section, 'hitPrefab')


class VehicleInfluenceZone(BasePortalArtefact):
    __slots__ = ('params', 'duration')

    def __init__(self):
        super(VehicleInfluenceZone, self).__init__()
        self.params = {'increaseFactors': component_constants.EMPTY_DICT,
         'duration': component_constants.ZERO_FLOAT,
         'radius': component_constants.ZERO_INT,
         'equipmentID': component_constants.ZERO_INT}

    def _readConfig(self, xmlCtx, section):
        super(VehicleInfluenceZone, self)._readConfig(xmlCtx, section)
        self.params['increaseFactors'] = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'increaseFactors')
        self.duration = self.params['duration'] = _xml.readInt(xmlCtx, section, 'duration')
        self.params['radius'] = _xml.readInt(xmlCtx, section, 'radius')
        self.params['equipmentID'] = self.id[1]
        self.params['usagePrefab'] = _xml.readString(xmlCtx, section, 'usagePrefab')


class VehicleTrap(artefacts.VisualScriptEquipment, artefacts.AreaMarkerConfigReader, artefacts.ArcadeEquipmentConfigReader, object):
    __slots__ = ('duration', 'impulse', 'gravityFactor', 'radius', 'offsetY', 'deploymentDelay', 'cooldown', 'idx') + artefacts.AreaMarkerConfigReader._MARKER_SLOTS_ + artefacts.ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(VehicleTrap, self).__init__()
        self.initMarkerInformation()
        self.initArcadeInformation()
        self.duration = 0.0
        self.impulse = 0.0
        self.gravityFactor = 0.0
        self.radius = 0.0
        self.offsetY = 0.0
        self.deploymentDelay = 0.0
        self.cooldown = 0.0
        self.idx = 0

    @property
    def tooltipParams(self):
        params = super(VehicleTrap, self).tooltipParams
        params['duration'] = self.duration
        params['impulse'] = self.impulse
        params['gravityFactor'] = self.gravityFactor
        params['radius'] = self.radius
        params['offsetY'] = self.offsetY
        params['deploymentDelay'] = self.deploymentDelay
        params['cooldown'] = self.cooldown
        return params

    def _readConfig(self, xmlCtx, section):
        super(VehicleTrap, self)._readConfig(xmlCtx, section)
        self.readMarkerConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.impulse = section.readFloat('impulse')
        self.gravityFactor = section.readFloat('gravityFactor')
        self.radius = section.readFloat('radius')
        self.offsetY = section.readFloat('offsetY')
        self.deploymentDelay = section.readFloat('deploymentDelay')
        self.cooldown = section.readFloat('cooldown')
        self.idx = section.readInt('idx')
        self._exportSlotsToVSE()
