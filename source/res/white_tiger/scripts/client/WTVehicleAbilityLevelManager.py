# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleAbilityLevelManager.py
from functools import partial
import BigWorld
import CGF
import GenericComponents
from items import vehicles
from vehicle_systems.model_assembler import loadAppearancePrefab
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from shared_utils import nextTick
from white_tiger.client_cgf.effects.components import WTAnimatorLinkComponent
from white_tiger.gui.shared.events import DynamicFactorsEvent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playDecreaseReloadByLevel, playIncreaseDamageByLevel

class WTVehicleAbilityLevelManager(DynamicScriptComponent):
    __FINISH_LAYER_NAME = '6'

    def __init__(self):
        super(WTVehicleAbilityLevelManager, self).__init__()
        self.__equipmentName = None
        self.__prefabGO = None
        return

    def onDestroy(self):
        self.__removePrefab()
        super(WTVehicleAbilityLevelManager, self).onDestroy()

    def set_isComponentActive(self, prev):
        if self.isComponentActive:
            self.__loadPrefab()
        elif self.currentAbilityLevel > 0:
            self.__removePrefabWithDelay()
        else:
            self.__removePrefab()
        self.__sendEvent({'keyName': self.__equipmentName,
         'isFail': self.isFail,
         'level': self.currentAbilityLevel,
         'isActive': self.isComponentActive})

    def set_currentAbilityLevel(self, prev):
        self.__sendEvent({'keyName': self.__equipmentName,
         'isFail': self.isFail,
         'level': self.currentAbilityLevel if not self.isFail else prev,
         'isActive': self.isComponentActive})
        if self.__prefabGO:
            self.__startAnimationLayer(str(self.currentAbilityLevel))
        self.__updateSound(prev)

    def _onAvatarReady(self):
        if self.isComponentActive:
            self.__loadPrefab()

    def __sendEvent(self, ctx):
        if BigWorld.player().playerVehicleID != self.entity.id:
            return
        g_eventBus.handleEvent(DynamicFactorsEvent(DynamicFactorsEvent.UPDATE_LEVEL, ctx=ctx), scope=EVENT_BUS_SCOPE.BATTLE)

    def __loadPrefab(self):
        equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        self.__equipmentName = equipment.name
        prefabPath = equipment.usagePrefab
        if not prefabPath:
            return
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed:
            loadAppearancePrefab(prefabPath, appearance, self.__onLoaded)

    def __onLoaded(self, go):
        if not self.isComponentActive:
            CGF.removeGameObject(go)
            return
        self.__prefabGO = go
        if self.currentAbilityLevel > 0:
            nextTick(partial(self.__startAnimationLayer, str(self.currentAbilityLevel)))()

    def __removePrefab(self):
        if self.__prefabGO and self.__prefabGO.isValid():
            CGF.removeGameObject(self.__prefabGO)
            self.__prefabGO = None
        return

    def __removePrefabWithDelay(self):
        if not self.__prefabGO:
            return
        self.__startAnimationLayer(self.__FINISH_LAYER_NAME)
        animator = self.__getAnimatorComponent()
        duration = 0
        if animator:
            duration = animator.getDurationByName(self.__FINISH_LAYER_NAME)
        self.__prefabGO.createComponent(GenericComponents.RemoveGoDelayedComponent, duration)

    def __startAnimationLayer(self, layerName):
        animator = self.__getAnimatorComponent()
        if animator and animator.isValid():
            animator.stop()
            animator.startLayerByName(layerName)

    def __getAnimatorComponent(self):
        animatorLinkComponent = self.__prefabGO.findComponentByType(WTAnimatorLinkComponent)
        return animatorLinkComponent.linkToAnimator()

    def __updateSound(self, prevLevel):
        if prevLevel == self.currentAbilityLevel:
            return
        if BigWorld.player().playerVehicleID != self.entity.id:
            return
        if self.__equipmentName == 'wt_decrease_reload_time':
            playDecreaseReloadByLevel(self.currentAbilityLevel)
        if self.__equipmentName == 'wt_increase_damage':
            playIncreaseDamageByLevel(self.currentAbilityLevel, self.entity.position)
