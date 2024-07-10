# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/common/battle_royale_artefacts.py
from Math import Vector3
from constants import IS_CLIENT, ATTACK_REASON, ATTACK_REASON_INDICES, SERVER_TICK_LENGTH
from items.artefacts import Repairkit, CountableConsumableConfigReader, Equipment, VehicleFactorsXmlReader, DOTParams, HOTParams, Bomber, ArcadeEquipmentConfigReader, Smoke, TooltipConfigReader, AreaMarkerConfigReader, HealPointConfigReader, PREDEFINED_HEAL_GROUPS, Minefield
from items import _xml, vehicles
from items.components import component_constants
from items.stun import g_cfg as stunConfig
if IS_CLIENT:
    from helpers import i18n
    from gui.impl.backport import text
    from gui.impl.backport.backport_system_locale import getNiceNumberFormat, getIntegralFormat
    from gui.impl.gen import R

class BattleDescriptionConfigReader(object):
    _BATTLE_DESCRIPTION_SLOTS = ('battleDescription',)

    def initBattleDescriptionSlots(self):
        self.battleDescription = component_constants.EMPTY_STRING

    def readBattleDescriptionConfig(self, xmlCtx, section):
        if IS_CLIENT:
            self.battleDescription = _xml.readString(xmlCtx, section, 'battleDescription')


class RepairkitBattleRoyale(Repairkit, CountableConsumableConfigReader):

    def __init__(self):
        super(RepairkitBattleRoyale, self).__init__()
        self.initCountableConsumableSlots()

    def _readConfig(self, xmlCtx, section):
        super(RepairkitBattleRoyale, self)._readConfig(xmlCtx, section)
        self.readCountableConsumableConfig(xmlCtx, section)


class AfterburningBattleRoyale(Equipment, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = ('consumeSeconds', 'enginePowerFactor', 'maxSpeedFactor', 'vehicleRotationSpeed', 'deploySeconds', 'rechargeSeconds') + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS

    def __init__(self):
        super(AfterburningBattleRoyale, self).__init__()
        self.consumeSeconds = component_constants.ZERO_INT
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.maxSpeedFactor = component_constants.ZERO_FLOAT
        self.vehicleRotationSpeed = component_constants.ZERO_FLOAT
        self.deploySeconds = component_constants.ZERO_FLOAT
        self.rechargeSeconds = component_constants.ZERO_FLOAT
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, section):
        self.consumeSeconds = _xml.readInt(xmlCtx, section, 'consumeSeconds', 0)
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.maxSpeedFactor = _xml.readPositiveFloat(xmlCtx, section, 'maxSpeedFactor')
        self.vehicleRotationSpeed = _xml.readPositiveFloat(xmlCtx, section, 'vehicleRotationSpeed')
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
            factors['vehicle/maxSpeed'] *= self.maxSpeedFactor
        except:
            pass

    def _getDescription(self, descr):
        localizeDescr = super(AfterburningBattleRoyale, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        enginePowerFactor = getNiceNumberFormat(100 * self.enginePowerFactor - 100)
        return i18n.makeString(descr, enginePowerFactor=enginePowerFactor + percentSymbol, maxSpeedFactor=int(self.maxSpeedFactor), consumeSeconds=int(self.consumeSeconds))


class InfluenceZone(object):
    __slots__ = ('radius', 'height', 'depth', 'timer', 'terrainResistance', 'debuffFactors', 'dotParams', 'hotParams', 'influenceType', 'fireEffectName', 'componentName')

    def __init__(self):
        self.radius = component_constants.ZERO_FLOAT
        self.height = component_constants.ZERO_FLOAT
        self.depth = component_constants.ZERO_FLOAT
        self.timer = component_constants.ZERO_FLOAT
        self.terrainResistance = component_constants.ZERO_FLOAT
        self.debuffFactors = component_constants.EMPTY_DICT
        self.dotParams = component_constants.EMPTY_DICT
        self.hotParams = component_constants.EMPTY_DICT
        self.influenceType = component_constants.INFLUENCE_ALL
        self.fireEffectName = component_constants.EMPTY_STRING
        self.componentName = None
        return

    def _readConfig(self, xmlCtx, section):
        self.debuffFactors = component_constants.EMPTY_DICT
        self.dotParams = component_constants.EMPTY_DICT
        self.hotParams = component_constants.EMPTY_DICT
        self.radius = _xml.readPositiveFloat(xmlCtx, section, 'radius')
        self.height = _xml.readPositiveFloat(xmlCtx, section, 'height')
        self.depth = _xml.readNonNegativeFloat(xmlCtx, section, 'depth', 0.0)
        self.timer = _xml.readPositiveFloat(xmlCtx, section, 'timer')
        if section.has_key('fireEffectName'):
            self.fireEffectName = _xml.readString(xmlCtx, section, 'fireEffectName')
        if section.has_key('terrainResistance'):
            self.terrainResistance = _xml.readPositiveFloat(xmlCtx, section, 'terrainResistance')
        if section.has_key('influenceType'):
            self.influenceType = _xml.readInt(xmlCtx, section, 'influenceType', component_constants.INFLUENCE_ALL, component_constants.INFLUENCE_ENEMY)
        if section.has_key('debuffFactors'):
            self.debuffFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'debuffFactors')
        if section.has_key('dotParams'):
            self.dotParams = DOTParams()
            self.dotParams._readConfig(xmlCtx, section['dotParams'])
        if section.has_key('hotParams'):
            self.hotParams = HOTParams()
            self.hotParams._readConfig(xmlCtx, section['hotParams'])


class TrapPoint(Equipment, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('influenceZone',)

    def __init__(self):
        super(TrapPoint, self).__init__()
        self.radius = component_constants.ZERO_FLOAT
        self.zonesCount = component_constants.ZERO_FLOAT
        self.influenceZone = InfluenceZone()
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, section):
        super(TrapPoint, self)._readConfig(xmlCtx, section)
        self.influenceZone._readConfig(xmlCtx, section['influenceZone'])
        self.radius = self.influenceZone.radius
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        localizeDescr = super(TrapPoint, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        if self.influenceZone.debuffFactors:
            vehicleMaxSpeed = getNiceNumberFormat(100 - self.influenceZone.debuffFactors['vehicle/maxSpeed'] * 100)
            gunReloadTime = getNiceNumberFormat(self.influenceZone.debuffFactors['gun/reloadTime'] * 100 - 100)
            return i18n.makeString(descr, duration=int(self.influenceZone.timer), vehicleMaxSpeed=vehicleMaxSpeed + percentSymbol, gunReloadTime=gunReloadTime + percentSymbol)
        if self.influenceZone.hotParams:
            healPerTick = getNiceNumberFormat(self.influenceZone.hotParams.healPerTick * 100)
            return i18n.makeString(descr, healPerTick=healPerTick + percentSymbol, timer=int(self.influenceZone.timer))


class BomberArcade(Bomber, ArcadeEquipmentConfigReader, BattleDescriptionConfigReader):
    __slots__ = Bomber.__slots__ + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS

    def __init__(self):
        super(BomberArcade, self).__init__()
        self.initArcadeInformation()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        super(BomberArcade, self)._readConfig(xmlCtx, scriptSection)
        if scriptSection.has_key('influenceZone'):
            self.influenceZone = InfluenceZone()
            self.influenceZone._readConfig(xmlCtx, scriptSection['influenceZone'])
        self.readArcadeInformation(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)


class BomberArcadeWithOwnDamage(Bomber, ArcadeEquipmentConfigReader, BattleDescriptionConfigReader):
    __slots__ = Bomber.__slots__ + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('abilityRadius', 'directHitRadius', 'stunRadius', 'maxDamage', 'minDamage', 'maxModuleDamage', 'minModuleDamage', 'damageSpread', 'stunTime', 'minStunTime')

    def __init__(self):
        super(BomberArcadeWithOwnDamage, self).__init__()
        self.initArcadeInformation()
        self.initOwnDamageParams()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        super(BomberArcadeWithOwnDamage, self)._readConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)
        self._readOwnDamageConfig(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)
        if IS_CLIENT and self.longDescription:
            self.longDescription = self._prepareDescription(self.longDescription)
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def initOwnDamageParams(self):
        self.abilityRadius = component_constants.ZERO_FLOAT
        self.directHitRadius = component_constants.ZERO_FLOAT
        self.stunRadius = component_constants.ZERO_FLOAT
        self.maxDamage = component_constants.ZERO_INT
        self.minDamage = component_constants.ZERO_INT
        self.maxModuleDamage = component_constants.ZERO_INT
        self.minModuleDamage = component_constants.ZERO_INT
        self.damageSpread = component_constants.ZERO_FLOAT
        self.stunTime = component_constants.ZERO_INT
        self.minStunTime = component_constants.ZERO_INT

    def _readOwnDamageConfig(self, xmlCtx, scriptSection):
        self.abilityRadius = _xml.readPositiveFloat(xmlCtx, scriptSection, 'abilityRadius')
        self.directHitRadius = _xml.readPositiveFloat(xmlCtx, scriptSection, 'directHitRadius')
        self.stunRadius = _xml.readPositiveFloat(xmlCtx, scriptSection, 'stunRadius')
        self.maxDamage = _xml.readPositiveInt(xmlCtx, scriptSection, 'maxDamage')
        self.minDamage = _xml.readPositiveInt(xmlCtx, scriptSection, 'minDamage')
        self.maxModuleDamage = _xml.readPositiveInt(xmlCtx, scriptSection, 'maxModuleDamage')
        self.minModuleDamage = _xml.readPositiveInt(xmlCtx, scriptSection, 'minModuleDamage')
        self.damageSpread = _xml.readPositiveFloat(xmlCtx, scriptSection, 'damageSpread')
        self.stunTime = _xml.readPositiveInt(xmlCtx, scriptSection, 'stunTime')
        self.minStunTime = _xml.readPositiveInt(xmlCtx, scriptSection, 'minStunTime')

    def _getDescription(self, descr):
        localizeDescr = super(BomberArcadeWithOwnDamage, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        return i18n.makeString(descr, minDamage=int(self.minDamage), maxDamage=int(self.maxDamage), delay=int(self.delay))


class SmokeArcade(Smoke, ArcadeEquipmentConfigReader, BattleDescriptionConfigReader):
    __slots__ = Smoke.__slots__ + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS

    def __init__(self):
        super(SmokeArcade, self).__init__()
        self.orthogonalDir = True
        self.initArcadeInformation()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readSmokeConfig(xmlCtx, scriptSection)
        self.cooldownTime = _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds')
        self.readArcadeInformation(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)
        if IS_CLIENT and self.longDescription:
            self.longDescription = self._prepareDescription(self.longDescription)
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _prepareDescription(self, descr):
        if self.dotParams:
            percentSymbol = text(R.strings.common.common.percent())
            damagePerTick = getNiceNumberFormat(self.dotParams.damagePerTick * 100)
            preparedDescr = i18n.makeString(descr, damagePerTick=damagePerTick + percentSymbol, duration=int(self.totalDuration))
        else:
            preparedDescr = i18n.makeString(self.longDescription, duration=int(self.totalDuration))
        return preparedDescr


class SelfBuff(Equipment, TooltipConfigReader, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = ('duration', 'increaseFactors', 'longDescription', 'cooldownTime') + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS

    def __init__(self):
        super(SelfBuff, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.increaseFactors = {}
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.cooldownTime = _xml.readFloat(xmlCtx, scriptSection, 'cooldownTime', 0.0)
        self.duration = _xml.readInt(xmlCtx, scriptSection, 'duration', 0)
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, scriptSection, 'increaseFactors')
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        return self._prepareDescription(self.longDescription)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        gunAimingTime = getNiceNumberFormat(100 - self.increaseFactors['gun/aimingTime'] * 100)
        return i18n.makeString(descr, duration=int(self.duration), gunAimingTime=gunAimingTime + percentSymbol)


class Berserker(SelfBuff):
    __slots__ = ('dotParams',)

    def __init__(self):
        super(Berserker, self).__init__()
        self.dotParams = DOTParams(ATTACK_REASON_INDICES[ATTACK_REASON.BERSERKER])

    def _readConfig(self, xmlCtx, scriptSection):
        self.cooldownTime = _xml.readFloat(xmlCtx, scriptSection, 'cooldownTime', 0.0)
        self.duration = _xml.readInt(xmlCtx, scriptSection, 'duration', 0)
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, scriptSection, 'increaseFactors')
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)
        self.dotParams._readConfig(xmlCtx, scriptSection['dotParams'])
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        gunPiercing = getIntegralFormat(self.increaseFactors['gun/piercing'])
        gunAimingTime = getNiceNumberFormat(100 - self.increaseFactors['gun/aimingTime'] * 100)
        healthDebuff = getIntegralFormat(self.duration / self.dotParams.tickInterval * self.dotParams.damagePerTick * 100)
        return i18n.makeString(descr, gunPiercing=gunPiercing, gunAimingTime=gunAimingTime + percentSymbol, healthDebuff=healthDebuff + percentSymbol, duration=int(self.duration))


class _ClientSpawnBotVisuals(object):
    __slots__ = ('markerPositionOffset', 'markerScale', 'deliveringAnimationDuration', 'deliveringAnimationStartDelay', 'highlightDelay')

    def __init__(self, xmlCtx, scriptSection):
        self.markerPositionOffset = _xml.readVector3(xmlCtx, scriptSection, 'markerPositionOffset', Vector3(0, 0, 0))
        self.markerScale = _xml.readVector3(xmlCtx, scriptSection, 'markerScale', Vector3(1, 1, 1))
        self.deliveringAnimationDuration = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'deliveringAnimationDuration', 0.0)
        self.deliveringAnimationStartDelay = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'deliveringAnimationStartDelay', 0.0)
        self.highlightDelay = _xml.readFloat(xmlCtx, scriptSection, 'highlightDelay', 0.0)


class BRHealPoint(Equipment, TooltipConfigReader, CountableConsumableConfigReader, HealPointConfigReader, BattleDescriptionConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + HealPointConfigReader._HEAL_POINT_SLOTS + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('cooldownTime',)

    def __init__(self):
        super(BRHealPoint, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.initHealPointSlots()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'cooldownTime')
        self.readHealPointConfig(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)
        if IS_CLIENT and self.longDescription:
            self.longDescription = self._prepareDescription(self.longDescription)
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        healPerTick = getNiceNumberFormat(100 * self.healPerTick)
        return i18n.makeString(descr, healPerTick=healPerTick + percentSymbol, duration=int(self.duration))


class RegenerationKit(Equipment, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = ('healthRegenPerTick', 'initialHeal', 'healTime', 'healGroup', 'tickInterval')

    def __init__(self):
        super(RegenerationKit, self).__init__()
        self.healthRegenPerTick = component_constants.ZERO_FLOAT
        self.initialHeal = component_constants.ZERO_FLOAT
        self.healTime = component_constants.ZERO_FLOAT
        self.healGroup = None
        self.tickInterval = 1.0
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()
        return

    def _readConfig(self, xmlCtx, section):
        self.healthRegenPerTick = _xml.readNonNegativeFloat(xmlCtx, section, 'healthRegenPerTick', 0.0)
        self.initialHeal = _xml.readNonNegativeFloat(xmlCtx, section, 'initialHeal', 0.0)
        self.healTime = _xml.readNonNegativeFloat(xmlCtx, section, 'healTime', 0.0)
        self.healGroup = _xml.readIntOrNone(xmlCtx, section, 'healGroup')
        self.tickInterval = _xml.readPositiveFloat(xmlCtx, section, 'tickInterval', 1.0)
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        localizeDescr = super(RegenerationKit, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        healPerTickDuration = getIntegralFormat(self.healthRegenPerTick * self.healTime * 100)
        return i18n.makeString(descr, healPerTickDuration=healPerTickDuration + percentSymbol, duration=int(self.healTime))


class BRMinefield(Minefield, BattleDescriptionConfigReader):
    __slots__ = Minefield.__slots__ + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS

    def __init__(self):
        super(BRMinefield, self).__init__()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, section):
        super(BRMinefield, self)._readConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = i18n.makeString(self.battleDescription, duration=int(self.mineParams.lifetime))


class ConsumableSpawnBot(Equipment, TooltipConfigReader, CountableConsumableConfigReader, AreaMarkerConfigReader, ArcadeEquipmentConfigReader, BattleDescriptionConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + AreaMarkerConfigReader._MARKER_SLOTS_ + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('botType', 'botVehCompDescr', 'botLifeTime', 'botSpawnPointOffset', 'botXRayFactor', 'clientVisuals', 'explosionRadius', 'explosionDamage', 'explosionByShoot', 'damageReductionRate', 'delay', 'cooldownTime', 'disableAllyDamage')

    def __init__(self):
        super(ConsumableSpawnBot, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initArcadeInformation()
        self.initMarkerInformation()
        self.initBattleDescriptionSlots()
        self.botType = component_constants.EMPTY_STRING
        self.botVehCompDescr = component_constants.EMPTY_STRING
        self.botLifeTime = component_constants.ZERO_FLOAT
        self.botSpawnPointOffset = None
        self.botXRayFactor = 1.0
        self.explosionRadius = component_constants.ZERO_FLOAT
        self.explosionDamage = component_constants.ZERO_FLOAT
        self.explosionByShoot = False
        self.damageReductionRate = component_constants.ZERO_FLOAT
        self.clientVisuals = component_constants.EMPTY_DICT
        self.delay = component_constants.ZERO_FLOAT
        self.cooldownTime = component_constants.ZERO_INT
        self.disableAllyDamage = True
        return

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)
        self.readMarkerConfig(xmlCtx, scriptSection)
        self.readBattleDescriptionConfig(xmlCtx, scriptSection)
        self.botType = _xml.readString(xmlCtx, scriptSection, 'botType')
        self.botVehCompDescr = _xml.readString(xmlCtx, scriptSection, 'botVehCompDescr')
        self.delay = _xml.readFloat(xmlCtx, scriptSection, 'delay', 0.0)
        self.botLifeTime = _xml.readFloat(xmlCtx, scriptSection, 'botLifeTime', 0.0)
        self.botSpawnPointOffset = _xml.readVector3(xmlCtx, scriptSection, 'botSpawnPointOffset', Vector3())
        self.botXRayFactor = _xml.readFloat(xmlCtx, scriptSection, 'botXRayFactor', 0.0)
        self.explosionRadius = _xml.readFloat(xmlCtx, scriptSection, 'explosionRadius', 0.0)
        self.explosionDamage = _xml.readFloat(xmlCtx, scriptSection, 'explosionDamage', 0.0)
        self.explosionByShoot = _xml.readBool(xmlCtx, scriptSection, 'explosionByShoot', False)
        self.damageReductionRate = _xml.readFloat(xmlCtx, scriptSection, 'damageReductionRate', 0.0)
        self.clientRemovalNotificationDelay = _xml.readInt(xmlCtx, scriptSection, 'clientRemovalNotificationDelay', 0.0)
        self.cooldownTime = _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds')
        self.disableAllyDamage = _xml.readBool(xmlCtx, scriptSection, 'disableAllyDamage', True)
        if IS_CLIENT:
            if scriptSection['clientVisuals'] is not None:
                self.clientVisuals = _ClientSpawnBotVisuals(scriptSection, scriptSection['clientVisuals'])
                self.longDescription = self._prepareDescription(self.longDescription)
                self.battleDescription = self._prepareDescription(self.battleDescription)
        return

    def _prepareDescription(self, descr):
        return i18n.makeString(descr, botLifeTime=int(self.botLifeTime))


class ZonesCircle(Equipment):
    __slots__ = ('influenceZone', 'radius', 'zonesCount', 'vehicleHeightMultiplier')

    def __init__(self):
        super(ZonesCircle, self).__init__()
        self.radius = component_constants.ZERO_FLOAT
        self.zonesCount = component_constants.ZERO_FLOAT
        self.vehicleHeightMultiplier = 1.0
        self.influenceZone = InfluenceZone()

    def _readConfig(self, xmlCtx, section):
        super(ZonesCircle, self)._readConfig(xmlCtx, section)
        self.radius = _xml.readFloat(xmlCtx, section, 'radius')
        self.zonesCount = _xml.readPositiveInt(xmlCtx, section, 'zonesCount')
        self.vehicleHeightMultiplier = _xml.readNonNegativeFloat(xmlCtx, section, 'vehicleHeightMultiplier')
        self.influenceZone._readConfig(xmlCtx, section['influenceZone'])

    def _getDescription(self, descr):
        localizeDescr = super(ZonesCircle, self)._getDescription(descr)
        return i18n.makeString(localizeDescr, duration=int(self.influenceZone.timer))


class FireCircle(ZonesCircle, CountableConsumableConfigReader, BattleDescriptionConfigReader):

    def __init__(self):
        super(FireCircle, self).__init__()
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, section):
        super(FireCircle, self)._readConfig(xmlCtx, section)
        self.influenceZone.dotParams.attackReasonID = ATTACK_REASON_INDICES[ATTACK_REASON.FIRE_CIRCLE]
        self.influenceZone.componentName = 'VehicleFireCircleEffectComponent'
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        localizeDescr = super(FireCircle, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        dotParams = self.influenceZone.dotParams
        damagePerTickForInterval = getNiceNumberFormat(self.influenceZone.timer / dotParams.tickInterval * dotParams.damagePerTick * 100)
        return i18n.makeString(descr, damagePerTickForInterval=damagePerTickForInterval + percentSymbol, timer=int(self.influenceZone.timer))


class CorrodingShot(Equipment, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('damagePercentAfterShot', 'canBeStoppedRepairKit', 'increaseFactors', 'dotEffectDuration', 'dotParams', 'tooltipMovie', 'effectsIndex')

    def __init__(self):
        super(CorrodingShot, self).__init__()
        self.damagePercentAfterShot = component_constants.ZERO_FLOAT
        self.canBeStoppedRepairKit = component_constants.ZERO_INT
        self.increaseFactors = {}
        self.dotParams = DOTParams(ATTACK_REASON_INDICES[ATTACK_REASON.CORRODING_SHOT])
        self.dotEffectDuration = component_constants.ZERO_INT
        self.tooltipMovie = component_constants.EMPTY_STRING
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()

    def _readConfig(self, xmlCtx, section):
        self.damagePercentAfterShot = _xml.readFloat(xmlCtx, section, 'damagePercentAfterShot', 0.0)
        self.canBeStoppedRepairKit = _xml.readBool(xmlCtx, section, 'canBeStoppedRepairKit', False)
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'increaseFactors')
        self.dotEffectDuration = _xml.readInt(xmlCtx, section, 'dotEffectDuration', 0)
        self.dotParams._readConfig(xmlCtx, section['dotParams'])
        self.tooltipMovie = _xml.readStringOrEmpty(xmlCtx, section, 'tooltipMovie')
        self.effectsIndex = vehicles.g_cache.shotEffectsIndexes[_xml.readString(xmlCtx, section, 'shotEffect')]
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        localizeDescr = super(CorrodingShot, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        damagePerDotEffectDuration = getIntegralFormat(self.dotEffectDuration / self.dotParams.tickInterval * self.dotParams.damagePerTick * 100)
        return i18n.makeString(descr, damagePerDotEffectDuration=damagePerDotEffectDuration + percentSymbol, dotEffectDuration=int(self.dotEffectDuration))


class AdaptationHealthRestore(Equipment, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('duration', 'areaVisual', 'immediatelyRestore', 'posteffectPrefab', 'restoringCoefficient', 'restoringCoefficientTeamMates', 'teamMateRestoringRadius')

    def __init__(self):
        super(AdaptationHealthRestore, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.restoringCoefficient = component_constants.ZERO_FLOAT
        self.restoringCoefficientTeamMates = component_constants.ZERO_FLOAT
        self.teamMateRestoringRadius = component_constants.ZERO_INT
        self.areaVisual = None
        self.posteffectPrefab = None
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(AdaptationHealthRestore, self)._readBasicConfig(xmlCtx, section)
        self.posteffectPrefab = _xml.readStringOrNone(xmlCtx, section, 'posteffectPrefab')

    def _readConfig(self, xmlCtx, section):
        self.duration = _xml.readInt(xmlCtx, section, 'duration', 0)
        self.immediatelyRestore = _xml.readInt(xmlCtx, section, 'immediatelyRestore', 0.0)
        self.restoringCoefficient = _xml.readFloat(xmlCtx, section, 'restoringCoefficient', 0.0)
        self.restoringCoefficientTeamMates = _xml.readFloat(xmlCtx, section, 'restoringCoefficientTeamMates', 0.0)
        self.teamMateRestoringRadius = _xml.readInt(xmlCtx, section, 'teamMateRestoringRadius', 0)
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        localizeDescr = super(AdaptationHealthRestore, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        return i18n.makeString(descr, immediatelyRestore=int(self.immediatelyRestore), duration=int(self.duration))


class ThunderStrike(Equipment, ArcadeEquipmentConfigReader, TooltipConfigReader, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('noOwner', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'delay', 'duration', 'damage', 'thunderCount', 'thunderPeriod', 'deployTime', 'cooldownTime', 'decreaseFactors', 'isDamageAll', 'canBeStoppedRepairKit')

    def __init__(self):
        super(ThunderStrike, self).__init__()
        self.initArcadeInformation()
        self.cooldownTime = component_constants.ZERO_INT
        self.canBeStoppedRepairKit = component_constants.ZERO_INT
        self.noOwner = False
        self.consumeAmmo = True
        self.duration = 0
        self.damage = 0
        self.thunderCount = 0
        self.thunderPeriod = 0
        self.areaLength = 0
        self.areaWidth = 0
        self.areaVisual = None
        self.areaColor = None
        self.damageRadius = 0
        self.decreaseFactors = {}
        self.isDamageAll = False
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()
        return

    def _readConfig(self, xmlCtx, section):
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownSeconds')
        self.canBeStoppedRepairKit = _xml.readBool(xmlCtx, section, 'canBeStoppedRepairKit', False)
        self.damageRadius = _xml.readInt(xmlCtx, section, 'damageRadius', 0)
        self.duration = _xml.readInt(xmlCtx, section, 'duration', 0)
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay', 0)
        self.damage = _xml.readInt(xmlCtx, section, 'damage', 0)
        self.thunderCount = _xml.readInt(xmlCtx, section, 'thunderCount', 0)
        self.thunderPeriod = _xml.readPositiveFloat(xmlCtx, section, 'thunderPeriod', 0)
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.isDamageAll = _xml.readBool(xmlCtx, section, 'isDamageAll', False)
        self.decreaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'decreaseFactors')
        self.readArcadeInformation(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT and self.longDescription:
            self.longDescription = self._prepareDescription(self.longDescription)
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _prepareDescription(self, descr):
        return i18n.makeString(descr, thunderCount=int(self.thunderCount), damage=int(self.damage), delay=int(self.delay))


class ShotPassion(Equipment, CountableConsumableConfigReader, BattleDescriptionConfigReader):
    __slots__ = BattleDescriptionConfigReader._BATTLE_DESCRIPTION_SLOTS + ('duration', 'increaseFactors', 'enableRamDamage', 'enableHEDamage', 'damageIncreasePerShot', 'maxDamageIncreasePerShot', 'affectingAbilities', 'cooldownTime', 'enableThunderStrikeDamageIncrease', 'posteffectPrefab')

    def __init__(self):
        super(ShotPassion, self).__init__()
        self.duration = component_constants.ZERO_INT
        self.damageIncreasePerShot = component_constants.ZERO_FLOAT
        self.maxDamageIncreasePerShot = component_constants.ZERO_FLOAT
        self.cooldownTime = component_constants.ZERO_INT
        self.initCountableConsumableSlots()
        self.initBattleDescriptionSlots()

    def _readBasicConfig(self, xmlCtx, section):
        super(ShotPassion, self)._readBasicConfig(xmlCtx, section)
        self.posteffectPrefab = _xml.readStringOrNone(xmlCtx, section, 'posteffectPrefab')

    def _readConfig(self, xmlCtx, section):
        self.duration = _xml.readInt(xmlCtx, section, 'duration', 0)
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'increaseFactors')
        self.damageIncreasePerShot = _xml.readFloat(xmlCtx, section, 'damageIncreasePerShot', component_constants.ZERO_FLOAT)
        self.maxDamageIncreasePerShot = _xml.readFloat(xmlCtx, section, 'maxDamageIncreasePerShot', component_constants.ZERO_FLOAT)
        self.cooldownTime = _xml.readInt(xmlCtx, section, 'cooldownSeconds', component_constants.ZERO_INT)
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readBattleDescriptionConfig(xmlCtx, section)
        if IS_CLIENT:
            self.battleDescription = self._prepareDescription(self.battleDescription)

    def _getDescription(self, descr):
        localizeDescr = super(ShotPassion, self)._getDescription(descr)
        return self._prepareDescription(localizeDescr)

    def _prepareDescription(self, descr):
        percentSymbol = text(R.strings.common.common.percent())
        gunAimingTime = getNiceNumberFormat(100 * self.increaseFactors['gun/aimingTime'] - 100)
        damageIncreasePerShot = getNiceNumberFormat(self.damageIncreasePerShot * 100)
        return i18n.makeString(descr, duration=getNiceNumberFormat(self.duration), gunAimingTime=gunAimingTime + percentSymbol, damageIncreasePerShot=damageIncreasePerShot + percentSymbol)
