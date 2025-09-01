# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/common/comp7_core_common/items/comp7_core_artefacts.py
from items.artefacts import BaseMarkerConfigReader, EffectsConfigReader, LevelBasedVisualScriptEquipment, VisualScriptEquipment

class Comp7CoreAoeHealEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'radius', 'heal', 'secondaryHealDebuff', 'tickInterval')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreAoeHealEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.radius = section.readFloat('radius')
        self.heal = tuple(map(float, section.readString('heal').split()))
        self.secondaryHealDebuff = section.readFloat('secondaryHealDebuff')
        self.tickInterval = section.readFloat('tickInterval')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreAllySupportEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'crewBuff')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreAllySupportEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.crewBuff = tuple(map(float, section.readString('crewBuff').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreAllyHunterEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'heal', 'gunReloadTimeBuff', 'tickInterval')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreAllyHunterEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.heal = tuple(map(float, section.readString('heal').split()))
        self.gunReloadTimeBuff = section.readFloat('gunReloadTimeBuff')
        self.tickInterval = section.readFloat('tickInterval')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreConcentrationEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'aimingTimeBuff', 'shotDispersionFactors', 'clipReloadTimeBoost')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreConcentrationEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.aimingTimeBuff = tuple(map(float, section.readString('aimingTimeBuff').split()))
        self.shotDispersionFactors = tuple(map(float, section.readString('shotDispersionFactors').split()))
        self.clipReloadTimeBoost = tuple(map(float, section.readString('clipReloadTimeBoost').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreBerserkEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'gunReloadTimeBuff', 'damageDistance', 'shotDispersionFactors')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreBerserkEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.gunReloadTimeBuff = tuple(map(float, section.readString('gunReloadTimeBuff').split()))
        self.damageDistance = section.readFloat('damageDistance')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.shotDispersionFactors = tuple(map(float, section.readString('shotDispersionFactors').split()))
        self._exportSlotsToVSE()


class Comp7CoreAoeInspireEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'radius', 'crewBuff')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreAoeInspireEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.crewBuff = tuple(map(float, section.readString('crewBuff').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreRedlineEquipment(LevelBasedVisualScriptEquipment, BaseMarkerConfigReader, EffectsConfigReader):
    _CONFIG_SLOTS = LevelBasedVisualScriptEquipment._LEVEL_BASED_SLOTS + BaseMarkerConfigReader._MARKER_SLOTS_ + EffectsConfigReader._EFFECTS_SLOTS_ + ('delay', 'damage', 'stunDuration', 'areaShow', 'fraction', 'requireAssists')

    def __init__(self):
        super(Comp7CoreRedlineEquipment, self).__init__()
        self.initMarkerInformation()
        self.initEffectsInformation()

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreRedlineEquipment, self)._readConfig(xmlCtx, section)
        self.delay = section.readFloat('delay')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.damage = tuple(map(float, section.readString('damage').split()))
        self.stunDuration = tuple(map(float, section.readString('stunDuration').split()))
        self.areaShow = section.readString('areaShow').lower() or None
        self.duration = section.readFloat('duration')
        self.readMarkerConfig(xmlCtx, section)
        self.readEffectConfig(xmlCtx, section)
        self.fraction = section.readFloat('fraction')
        self.requireAssists = section.readBool('requireAssists', False)
        self._exportSlotsToVSE()
        return


class Comp7CoreFastRechargeEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('gunReloadTimeBuff',)

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreFastRechargeEquipment, self)._readConfig(xmlCtx, section)
        self.gunReloadTimeBuff = tuple(map(float, section.readString('gunReloadTimeBuff').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreJuggernautEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'enginePowerFactor', 'dmgAbsorb', 'fwMaxSpeedBonus', 'bkMaxSpeedBonus', 'rammingDamageBonus', 'vehicleRotationSpeedFactor')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreJuggernautEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.enginePowerFactor = section.readFloat('enginePowerFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.dmgAbsorb = tuple(map(float, section.readString('dmgAbsorb').split()))
        self.fwMaxSpeedBonus = section.readFloat('fwMaxSpeedBonus')
        self.bkMaxSpeedBonus = section.readFloat('bkMaxSpeedBonus')
        self.rammingDamageBonus = section.readFloat('rammingDamageBonus')
        self.vehicleRotationSpeedFactor = section.readFloat('vehicleRotationSpeedFactor')
        self._exportSlotsToVSE()


class Comp7CoreSureShotEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'shotDispersionFactors', 'slvl', 'sdlvl')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreSureShotEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.shotDispersionFactors = tuple(map(float, section.readString('shotDispersionFactors').split()))
        self.slvl = tuple(map(float, section.readString('slvl').split()))
        self.sdlvl = tuple(map(float, section.readString('sdlvl').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreSniperEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'dispersionFactor', 'damageDistance', 'damageFactors')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreSniperEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.dispersionFactor = section.readFloat('dispersionFactor')
        self.damageDistance = section.readFloat('damageDistance')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.damageFactors = tuple(map(float, section.readString('damageFactors').split()))
        self._exportSlotsToVSE()


class Comp7CoreRiskyAttackEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'healDuration', 'baseHeal', 'extraHealFactor', 'fwdSpeedBoost', 'bkwSpeedBoost', 'enginePowerBuff')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreRiskyAttackEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.healDuration = section.readFloat('healDuration')
        self.baseHeal = section.readFloat('baseHeal')
        self.extraHealFactor = tuple(map(float, section.readString('extraHealFactor').split()))
        self.fwdSpeedBoost = section.readFloat('fwdSpeedBoost')
        self.bkwSpeedBoost = section.readFloat('bkwSpeedBoost')
        self.enginePowerBuff = section.readFloat('enginePowerBuff')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreReconEquipment(LevelBasedVisualScriptEquipment, BaseMarkerConfigReader):
    _CONFIG_SLOTS = LevelBasedVisualScriptEquipment._LEVEL_BASED_SLOTS + BaseMarkerConfigReader._MARKER_SLOTS_ + ('duration', 'delay', 'startupDelay')

    def __init__(self):
        super(Comp7CoreReconEquipment, self).__init__()
        self.initMarkerInformation()

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreReconEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.delay = section.readFloat('delay')
        self.startupDelay = section.readFloat('startupDelay')
        self.readMarkerConfig(xmlCtx, section)
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreAggressiveDetectionEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'visionFactor')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreAggressiveDetectionEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.visionFactor = tuple(map(float, section.readString('visionFactor').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreMarchEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'enginePowerBuff', 'fwdSpeedBoost', 'invisibilityFactor')

    def _readConfig(self, xmlCtx, section):
        super(Comp7CoreMarchEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.enginePowerBuff = section.readFloat('enginePowerBuff')
        self.fwdSpeedBoost = section.readFloat('fwdSpeedBoost')
        self.invisibilityFactor = section.readFloat('invisibilityFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()
