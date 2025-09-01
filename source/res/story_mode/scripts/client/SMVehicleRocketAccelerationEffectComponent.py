# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMVehicleRocketAccelerationEffectComponent.py
from functools import partial
import typing
import BigWorld
import CGF
from cgf_components.rocket_acceleration_component import RocketAccelerationStateListener
from debug_utils import LOG_ERROR
from items.components.c11n_constants import SLOT_DEFAULT_ALLOWED_MODEL
from script_component.DynamicScriptComponent import DynamicScriptComponent
from shared_utils import safeCancelCallback
from vehicle_systems.model_assembler import loadAppearancePrefab

class SMVehicleRocketAccelerationEffectComponent(DynamicScriptComponent):

    def __init__(self, *_, **__):
        super(SMVehicleRocketAccelerationEffectComponent, self).__init__(*_, **__)
        self._gameObject = None
        self._startCallbackId = None
        return

    def onDestroy(self):
        self.entity.onAppearanceReady -= self._tryLoadPrefab
        if self._gameObject is not None:
            self._goToEndState(self._gameObject)
            self._gameObject = None
        if self._startCallbackId is not None:
            safeCancelCallback(self._startCallbackId)
            self._startCallbackId = None
        super(SMVehicleRocketAccelerationEffectComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        super(SMVehicleRocketAccelerationEffectComponent, self)._onAvatarReady()
        isPrefabLoading = self._tryLoadPrefab()
        if not isPrefabLoading:
            self.entity.onAppearanceReady += self._tryLoadPrefab

    def _tryLoadPrefab(self):
        if self._gameObject is not None:
            return False
        else:
            typeDescriptor = self.entity.typeDescriptor
            if typeDescriptor is None or self.entity.isDestroyed or not self.entity.isAlive():
                return False
            appearance = self.entity.appearance
            if appearance is None or not appearance.isConstructed or appearance.isDestroyed:
                return False
            prefabPath = self._getPrefabPath()
            if prefabPath is None:
                return False
            loadAppearancePrefab(prefabPath, appearance, self._onLoaded)
            return True

    def _getPrefabPath(self):
        accelerationParams = self.entity.typeDescriptor.type.rocketAccelerationParams
        if accelerationParams is None or accelerationParams.effectsPrefab is None:
            return
        else:
            modelsSet = self.entity.appearance.outfit.modelsSet or SLOT_DEFAULT_ALLOWED_MODEL
            if modelsSet not in accelerationParams.effectsPrefab:
                LOG_ERROR('Effects prefab path is not specified for modelsSet.'.format(modelsSet))
                return
            return accelerationParams.effectsPrefab[modelsSet]

    def _onLoaded(self, gameObject):
        if not gameObject.isValid:
            return
        self._gameObject = gameObject
        self._goToStartState()

    def _goToStartState(self):
        rocketAcceleration = self._getRocketAcceleration()
        if rocketAcceleration is not None:
            rocketAcceleration.start.activate()
            self._startCallbackId = BigWorld.callback(rocketAcceleration.startDuration, self._goToIdleState)
        return

    def _goToIdleState(self):
        self._startCallbackId = None
        rocketAcceleration = self._getRocketAcceleration()
        if rocketAcceleration is not None:
            rocketAcceleration.start.deactivate()
            rocketAcceleration.idle.activate()
        return

    def _goToEndState(self, gameObject):
        rocketAcceleration = self._getRocketAcceleration()
        if rocketAcceleration is not None:
            if self._startCallbackId is not None:
                rocketAcceleration.start.deactivate()
            else:
                rocketAcceleration.idle.deactivate()
                rocketAcceleration.end.activate()
            BigWorld.callback(rocketAcceleration.endDuration, partial(CGF.removeGameObject, gameObject))
        return

    def _getRocketAcceleration(self):
        return self._gameObject.findComponentByType(RocketAccelerationStateListener) if self._gameObject is not None else None
