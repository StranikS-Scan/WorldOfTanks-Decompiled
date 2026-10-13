# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffVehicleEffectsComponent.py
from __future__ import absolute_import
from HWBuffSequencesComponent import HWBuffSequencesComponent
from dyn_components_groups import groupComponent
from xml_config_specs import StrParam
from VehicleEffects import DamageFromShotDecoder
from constants import VEHICLE_HIT_EFFECT

@groupComponent(moduleName=StrParam())
class HWBuffVehicleEffectsComponent(HWBuffSequencesComponent):
    _START_TRIGGER = 'start_trigger'
    _DEATH_MODULE = 'death'

    def __init__(self):
        super(HWBuffVehicleEffectsComponent, self).__init__()
        self.__isDeathModule = self.groupComponentConfig.moduleName == self._DEATH_MODULE

    def onDestroy(self):
        self.entity.events.onShowDamageFromShot -= self._onShowDamageFromShot
        if self.__isDeathModule:
            self.entity.events.onVehicleHealthChanged -= self.__onVehicleHealthChanged
            appearance = self.entity.appearance
            if appearance is not None and appearance.onModelChanged is not None:
                appearance.onModelChanged -= self.__onModelChanged
        super(HWBuffVehicleEffectsComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        super(HWBuffVehicleEffectsComponent, self)._onAvatarReady()
        self.entity.events.onShowDamageFromShot += self._onShowDamageFromShot
        if self.__isDeathModule:
            self.entity.events.onVehicleHealthChanged += self.__onVehicleHealthChanged

    def _onShowDamageFromShot(self, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield):
        parsedPoints = DamageFromShotDecoder.parseHitPoints(points, self.entity.appearance.collisions)
        if not parsedPoints:
            return
        maxPriorityHitPoint = parsedPoints[-1]
        maxHitEffectCode = maxPriorityHitPoint.hitEffectCode
        hasPiercedHit = maxHitEffectCode in VEHICLE_HIT_EFFECT.PIERCED_HITS
        moduleName = maxPriorityHitPoint.componentName
        if hasPiercedHit and moduleName == self.groupComponentConfig.moduleName:
            self._triggerEffects(self._START_TRIGGER)

    def __onVehicleHealthChanged(self, _vehicleID, newHealth, oldHealth):
        if not oldHealth > 0 >= newHealth:
            return
        else:
            appearance = self.entity.appearance
            if appearance is not None and appearance.onModelChanged is not None:
                appearance.onModelChanged += self.__onModelChanged
            return

    def __onModelChanged(self):
        appearance = self.entity.appearance
        if appearance is None or not appearance.damageState.isCurrentModelDamaged:
            return
        else:
            appearance.onModelChanged -= self.__onModelChanged
            self._triggerEffects(self._START_TRIGGER)
            return
