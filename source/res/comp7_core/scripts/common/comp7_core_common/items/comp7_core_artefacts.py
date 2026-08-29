# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/common/comp7_core_common/items/comp7_core_artefacts.py
from __future__ import absolute_import
from items.artefacts import BaseMarkerConfigReader, EffectsConfigReader, LevelBasedVisualScriptEquipment, VisualScriptEquipment

class Comp7CoreAoeHealEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'radius', 'heal', 'secondaryHealDebuff', 'tickInterval')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreAoeHealEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.radius = scriptSection.readFloat('radius')
        self.heal = tuple(map(float, scriptSection.readString('heal').split()))
        self.secondaryHealDebuff = scriptSection.readFloat('secondaryHealDebuff')
        self.tickInterval = scriptSection.readFloat('tickInterval')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreAllySupportEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'crewBuff')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreAllySupportEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.crewBuff = tuple(map(float, scriptSection.readString('crewBuff').split()))
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreAllyHunterEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'heal', 'gunReloadTimeBuff', 'tickInterval')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreAllyHunterEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.heal = tuple(map(float, scriptSection.readString('heal').split()))
        self.gunReloadTimeBuff = scriptSection.readFloat('gunReloadTimeBuff')
        self.tickInterval = scriptSection.readFloat('tickInterval')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreConcentrationEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'aimingTimeBuff', 'shotDispersionFactors', 'clipReloadTimeBoost')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreConcentrationEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.aimingTimeBuff = tuple(map(float, scriptSection.readString('aimingTimeBuff').split()))
        self.shotDispersionFactors = tuple(map(float, scriptSection.readString('shotDispersionFactors').split()))
        self.clipReloadTimeBoost = tuple(map(float, scriptSection.readString('clipReloadTimeBoost').split()))
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreBerserkEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'gunReloadTimeBuff', 'damageDistance', 'shotDispersionFactors')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreBerserkEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.gunReloadTimeBuff = tuple(map(float, scriptSection.readString('gunReloadTimeBuff').split()))
        self.damageDistance = scriptSection.readFloat('damageDistance')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self.shotDispersionFactors = tuple(map(float, scriptSection.readString('shotDispersionFactors').split()))
        self._exportSlotsToVSE()


class Comp7CoreAoeInspireEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'radius', 'crewBuff')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreAoeInspireEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.crewBuff = tuple(map(float, scriptSection.readString('crewBuff').split()))
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreRedlineEquipment(LevelBasedVisualScriptEquipment, BaseMarkerConfigReader, EffectsConfigReader):
    _CONFIG_SLOTS = LevelBasedVisualScriptEquipment._LEVEL_BASED_SLOTS + BaseMarkerConfigReader._MARKER_SLOTS_ + EffectsConfigReader._EFFECTS_SLOTS_ + ('delay', 'damage', 'stunDuration', 'areaShow', 'fraction', 'requireAssists')

    def __init__(self):
        super(Comp7CoreRedlineEquipment, self).__init__()
        self.initMarkerInformation()
        self.initEffectsInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreRedlineEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.delay = scriptSection.readFloat('delay')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self.damage = tuple(map(float, scriptSection.readString('damage').split()))
        self.stunDuration = tuple(map(float, scriptSection.readString('stunDuration').split()))
        self.areaShow = scriptSection.readString('areaShow').lower() or None
        self.duration = scriptSection.readFloat('duration')
        self.readMarkerConfig(xmlCtx, scriptSection)
        self.readEffectConfig(xmlCtx, scriptSection)
        self.fraction = scriptSection.readFloat('fraction')
        self.requireAssists = scriptSection.readBool('requireAssists', False)
        self._exportSlotsToVSE()
        return


class Comp7CoreFastRechargeEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('gunReloadTimeBuff', 'gunTemperatureBuff')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreFastRechargeEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.gunReloadTimeBuff = tuple(map(float, scriptSection.readString('gunReloadTimeBuff').split()))
        self.gunTemperatureBuff = tuple(map(float, scriptSection.readString('gunTemperatureBuff').split()))
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreJuggernautEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'enginePowerFactor', 'dmgAbsorb', 'fwMaxSpeedBonus', 'bkMaxSpeedBonus', 'rammingDamageBonus', 'vehicleRotationSpeedFactor')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreJuggernautEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = tuple(map(float, scriptSection.readString('duration').split()))
        self.enginePowerFactor = scriptSection.readFloat('enginePowerFactor')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self.dmgAbsorb = tuple(map(float, scriptSection.readString('dmgAbsorb').split()))
        self.fwMaxSpeedBonus = scriptSection.readFloat('fwMaxSpeedBonus')
        self.bkMaxSpeedBonus = scriptSection.readFloat('bkMaxSpeedBonus')
        self.rammingDamageBonus = scriptSection.readFloat('rammingDamageBonus')
        self.vehicleRotationSpeedFactor = scriptSection.readFloat('vehicleRotationSpeedFactor')
        self._exportSlotsToVSE()


class Comp7CoreSureShotEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'shotDispersionFactors', 'slvl', 'sdlvl')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreSureShotEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.shotDispersionFactors = tuple(map(float, scriptSection.readString('shotDispersionFactors').split()))
        self.slvl = tuple(map(float, scriptSection.readString('slvl').split()))
        self.sdlvl = tuple(map(float, scriptSection.readString('sdlvl').split()))
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreSniperEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'dispersionFactor', 'damageDistance', 'damageFactors')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreSniperEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = tuple(map(float, scriptSection.readString('duration').split()))
        self.dispersionFactor = scriptSection.readFloat('dispersionFactor')
        self.damageDistance = scriptSection.readFloat('damageDistance')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self.damageFactors = tuple(map(float, scriptSection.readString('damageFactors').split()))
        self._exportSlotsToVSE()


class Comp7CoreRiskyAttackEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'healDuration', 'baseHeal', 'extraHealFactor', 'fwdSpeedBoost', 'bkwSpeedBoost', 'enginePowerBuff')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreRiskyAttackEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.healDuration = scriptSection.readFloat('healDuration')
        self.baseHeal = scriptSection.readFloat('baseHeal')
        self.extraHealFactor = tuple(map(float, scriptSection.readString('extraHealFactor').split()))
        self.fwdSpeedBoost = scriptSection.readFloat('fwdSpeedBoost')
        self.bkwSpeedBoost = scriptSection.readFloat('bkwSpeedBoost')
        self.enginePowerBuff = scriptSection.readFloat('enginePowerBuff')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreReconEquipment(LevelBasedVisualScriptEquipment, BaseMarkerConfigReader):
    _CONFIG_SLOTS = LevelBasedVisualScriptEquipment._LEVEL_BASED_SLOTS + BaseMarkerConfigReader._MARKER_SLOTS_ + ('duration', 'delay', 'startupDelay')

    def __init__(self):
        super(Comp7CoreReconEquipment, self).__init__()
        self.initMarkerInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreReconEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = tuple(map(float, scriptSection.readString('duration').split()))
        self.delay = scriptSection.readFloat('delay')
        self.startupDelay = scriptSection.readFloat('startupDelay')
        self.readMarkerConfig(xmlCtx, scriptSection)
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreAggressiveDetectionEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'visionFactor')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreAggressiveDetectionEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = scriptSection.readFloat('duration')
        self.visionFactor = tuple(map(float, scriptSection.readString('visionFactor').split()))
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7CoreMarchEquipment(VisualScriptEquipment):
    _CONFIG_SLOTS = ('duration', 'enginePowerBuff', 'fwdSpeedBoost', 'invisibilityFactor')

    def _readConfig(self, xmlCtx, scriptSection):
        super(Comp7CoreMarchEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.duration = tuple(map(float, scriptSection.readString('duration').split()))
        self.enginePowerBuff = scriptSection.readFloat('enginePowerBuff')
        self.fwdSpeedBoost = scriptSection.readFloat('fwdSpeedBoost')
        self.invisibilityFactor = scriptSection.readFloat('invisibilityFactor')
        self.cooldownSeconds = scriptSection.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()
