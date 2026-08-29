# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleExplosiveDamageShield.py
import CGF
import GenericComponents
from items import vehicles
from shared_utils import nextTick
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers.CallbackDelayer import CallbackDelayer
from vehicle_systems.model_assembler import loadAppearancePrefab
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playExplosiveShieldSound
from white_tiger.client_cgf.effects.components import WTAnimatorLinkComponent
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import WTExplosiveDamageShieldTimerViewState

class WTVehicleExplosiveDamageShield(DynamicScriptComponent):
    __START_LAYER = 'Start'
    __IDLE_LAYER = 'Idle'
    __HIT_LAYER = 'Hit'
    __END_LAYER = 'End'
    __EXPLODE_LAYER = 'Explode'

    def __init__(self):
        super(WTVehicleExplosiveDamageShield, self).__init__()
        self.__prefabGO = None
        self.__timerValue = None
        self.__maxDamage = None
        self.__duration = None
        self.__currentLayer = None
        self.__cd = CallbackDelayer()
        return

    def onDestroy(self):
        self.__cd.destroy()
        self.__cd = None
        self.__removePrefab()
        super(WTVehicleExplosiveDamageShield, self).onDestroy()
        return

    def set_isExplosiveDamageShieldActive(self, prev):
        if self.isExplosiveDamageShieldActive == prev:
            return
        if self.isExplosiveDamageShieldActive:
            self.__loadPrefab()
        elif self.__prefabGO:
            self.__removePrefabWithDelay()
        self.__updateTimer()

    def set_totalInComeDamage(self, prev):
        self.__updateTimer()
        if self.isExplosiveDamageShieldActive:
            self.__currentLayer = self.__HIT_LAYER
            self.__startAnimation()
            duration = self.__getAnimationDuration()
            self.__cd.delayCallback(duration, self.__animationFinished)

    def _onAvatarReady(self):
        if self.isExplosiveDamageShieldActive:
            self.__loadPrefab()
        self.__updateTimer()

    def __updateTimer(self):
        value = WTExplosiveDamageShieldTimerViewState(self.isExplosiveDamageShieldActive, self.__duration, self.finishTime, self.totalInComeDamage, self.__maxDamage)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_ENERGY_SHIELD, value, vehicleID=self.entity.id)

    def __loadPrefab(self):
        equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        self.__maxDamage = equipment.maxDamage
        self.__duration = equipment.consumeSeconds
        prefabPath = equipment.usagePrefab
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed:
            loadAppearancePrefab(prefabPath, appearance, self.__onLoaded)

    def __onLoaded(self, go):
        if not self.isExplosiveDamageShieldActive:
            CGF.removeGameObject(go)
            return
        self.__prefabGO = go
        self.__currentLayer = self.__START_LAYER
        self.__startAnimation()
        duration = self.__getAnimationDuration()
        if duration:
            self.__cd.delayCallback(duration, self.__animationFinished)

    def __removePrefab(self):
        if self.__prefabGO is not None and self.__prefabGO.isValid():
            CGF.removeGameObject(self.__prefabGO)
            self.__prefabGO = None
        return

    def __animationFinished(self):
        if not self.isExplosiveDamageShieldActive:
            return
        if self.__currentLayer in (self.__START_LAYER, self.__HIT_LAYER):
            self.__currentLayer = self.__IDLE_LAYER
            self.__startAnimation()

    @nextTick
    def __startAnimation(self):
        animatorComponent = self.__getAnimatorComponent()
        if animatorComponent and animatorComponent.isValid():
            animatorComponent.stop()
            animatorComponent.startLayerByName(self.__currentLayer)
        self.__playSound()

    def __getAnimationDuration(self):
        animatorComponent = self.__getAnimatorComponent()
        duration = 0
        if animatorComponent and animatorComponent.isValid():
            duration = animatorComponent.getDurationByName(self.__currentLayer)
        return duration

    def __getAnimatorComponent(self):
        if not self.__prefabGO:
            return
        shieldComponent = self.__prefabGO.findComponentByType(WTAnimatorLinkComponent)
        return shieldComponent.linkToAnimator()

    def __removePrefabWithDelay(self):
        self.__cd.clearCallbacks()
        layerName = self.__EXPLODE_LAYER if self.totalInComeDamage >= self.__maxDamage else self.__END_LAYER
        self.__currentLayer = layerName
        self.__startAnimation()
        duration = self.__getAnimationDuration()
        self.__prefabGO.createComponent(GenericComponents.RemoveGoDelayedComponent, duration)

    def __playSound(self):
        playExplosiveShieldSound(self.__currentLayer, self.entity)
