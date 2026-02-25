# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common/items/artefacts.py
import importlib
from items.components import component_constants
from items import _xml
from items.artefacts import Equipment
artefacts = importlib.import_module('items.artefacts')

class CosmicEventGravityFieldEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'radius', 'gravityFactor', 'impulsePerSecond')

    @property
    def tooltipParams(self):
        params = super(CosmicEventGravityFieldEquipment, self).tooltipParams
        params['radius'] = self.radius
        params['gravityFactor'] = self.gravityFactor
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventGravityFieldEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.radius = section.readFloat('radius')
        self.gravityFactor = section.readFloat('gravityFactor')
        self.impulsePerSecond = section.readFloat('impulsePerSecond')
        self._exportSlotsToVSE()


class CosmicEventWaveEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('radius', 'impulseFactor', 'duration', 'cooldownSeconds')

    @property
    def tooltipParams(self):
        params = super(CosmicEventWaveEquipment, self).tooltipParams
        params['radius'] = self.radius
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventWaveEquipment, self)._readConfig(xmlCtx, section)
        self.radius = section.readFloat('radius')
        self.impulseFactor = section.readFloat('impulseFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.duration = section.readFloat('duration')
        self._exportSlotsToVSE()


class CosmicEventRocketBoosterEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'cooldownSeconds')

    @property
    def tooltipParams(self):
        params = super(CosmicEventRocketBoosterEquipment, self).tooltipParams
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventRocketBoosterEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class CosmicEventBlackHoleEquipment(artefacts.VisualScriptEquipment, artefacts.AreaMarkerConfigReader, artefacts.ArcadeEquipmentConfigReader, object):
    __slots__ = ('duration', 'impulse', 'gravityFactor', 'radius', 'deploymentDelay') + artefacts.AreaMarkerConfigReader._MARKER_SLOTS_ + artefacts.ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(CosmicEventBlackHoleEquipment, self).__init__()
        self.initMarkerInformation()
        self.initArcadeInformation()

    @property
    def tooltipParams(self):
        params = super(CosmicEventBlackHoleEquipment, self).tooltipParams
        params['duration'] = self.duration
        params['impulse'] = self.impulse
        params['gravityFactor'] = self.gravityFactor
        params['radius'] = self.radius
        params['deploymentDelay'] = self.deploymentDelay
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventBlackHoleEquipment, self)._readConfig(xmlCtx, section)
        self.readMarkerConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.impulse = section.readFloat('impulse')
        self.gravityFactor = section.readFloat('gravityFactor')
        self.radius = section.readFloat('radius')
        self.deploymentDelay = section.readFloat('deploymentDelay')
        self._exportSlotsToVSE()


class CosmicEventHookShotEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'shellID', 'shotSpeed')

    @property
    def tooltipParams(self):
        params = super(CosmicEventHookShotEquipment, self).tooltipParams
        params['duration'] = self.duration
        params['shellID'] = self.shellID
        params['shotSpeed'] = self.shotSpeed
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventHookShotEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.shellID = section.readInt('shellID')
        self.shotSpeed = section.readInt('shotSpeed')
        self._exportSlotsToVSE()


class CosmicEventShieldEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('duration', 'gravityFactor', 'cooldownSeconds', 'radius')

    @property
    def tooltipParams(self):
        params = super(CosmicEventShieldEquipment, self).tooltipParams
        params['cooldown'] = self.cooldownSeconds
        params['duration'] = self.duration
        params['cooldownSeconds'] = self.cooldownSeconds
        params['radius'] = self.radius
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventShieldEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.gravityFactor = section.readFloat('gravityFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.radius = section.readFloat('radius')
        self._exportSlotsToVSE()


class CosmicEventPowerShotEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('shellID', 'shotSpeed')

    @property
    def tooltipParams(self):
        params = super(CosmicEventPowerShotEquipment, self).tooltipParams
        params['shellID'] = self.shellID
        params['shotSpeed'] = self.shotSpeed
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventPowerShotEquipment, self)._readConfig(xmlCtx, section)
        self.shellID = section.readInt('shellID')
        self.shotSpeed = section.readInt('shotSpeed')
        self._exportSlotsToVSE()


class CosmicEventStunShotEquipment(artefacts.VisualScriptEquipment, object):
    __slots__ = ('cooldownSeconds', 'stunDuration', 'vehicleSpeedMultiplier', 'turretRotationSpeedMultiplier', 'gunReloadTimeMultiplier', 'shellID', 'shotSpeed')

    @property
    def tooltipParams(self):
        params = super(CosmicEventStunShotEquipment, self).tooltipParams
        params['cooldownSeconds'] = self.cooldownSeconds
        params['stunDuration'] = self.stunDuration
        params['vehicleSpeedMultiplier'] = self.vehicleSpeedMultiplier
        params['turretRotationSpeedMultiplier'] = self.turretRotationSpeedMultiplier
        params['gunReloadTimeMultiplier'] = self.gunReloadTimeMultiplier
        params['shellID'] = self.shellID
        params['shotSpeed'] = self.shotSpeed
        return params

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventStunShotEquipment, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.stunDuration = section.readFloat('stunDuration')
        self.vehicleSpeedMultiplier = section.readFloat('vehicleSpeedMultiplier')
        self.turretRotationSpeedMultiplier = section.readFloat('turretRotationSpeedMultiplier')
        self.gunReloadTimeMultiplier = section.readFloat('gunReloadTimeMultiplier')
        self.shellID = section.readInt('shellID')
        self.shotSpeed = section.readInt('shotSpeed')
        self._exportSlotsToVSE()


class CosmicEventMineEquipment(Equipment, artefacts.ArcadeEquipmentConfigReader):
    __slots__ = ('duration', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'restrictedAreaColor')

    def __init__(self):
        super(CosmicEventMineEquipment, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.initArcadeInformation()
        self.areaLength = component_constants.ZERO_INT
        self.areaWidth = component_constants.ZERO_INT
        self.areaVisual = None
        self.areaColor = None
        self.restrictedAreaColor = None
        return

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventMineEquipment, self)._readConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.restrictedAreaColor = _xml.readIntOrNone(xmlCtx, section, 'restrictedAreaColor')


class CosmicEventTeleportEquipment(artefacts.Equipment, object):
    __slots__ = ('lifeTime',)

    def _readConfig(self, xmlCtx, section):
        super(CosmicEventTeleportEquipment, self)._readConfig(xmlCtx, section)
        self.lifeTime = section.readFloat('lifeTime')
