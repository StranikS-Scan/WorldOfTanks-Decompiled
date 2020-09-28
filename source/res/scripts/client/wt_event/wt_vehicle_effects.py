# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wt_event/wt_vehicle_effects.py
import BigWorld
import Math
import SoundGroups
import WtEffects
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, isPlayerAvatar
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IGameEventController
from svarog_script.script_game_object import ScriptGameObject, ComponentDescriptor
from svarog_script.py_component import Component

class WtVehicleEffectType(CONST_CONTAINER):
    HUNTER_IDLE = 0
    HUNTER_COLLECTOR = 1
    HUNTER_PROGRESS_BAR = 2
    BOSS_IDLE = 3
    BOSS_IDLE_SPECIAL = 4
    BOSS_SHIELD_INDICATOR = 5
    BOSS_SHIELD_INDICATOR_SPECIAL = 6


def getSequenceWrapper(effectType):
    if effectType == WtVehicleEffectType.HUNTER_IDLE:
        return HunterIdleEffectObject
    if effectType == WtVehicleEffectType.HUNTER_COLLECTOR:
        return HunterPowerCollectorObject
    if effectType == WtVehicleEffectType.HUNTER_PROGRESS_BAR:
        return HunterProgressBarObject
    return BossIdleEffect if effectType == WtVehicleEffectType.BOSS_IDLE else VehicleIdleEffect


def getSequenceComponent(effectType):
    if effectType == WtVehicleEffectType.HUNTER_COLLECTOR:
        return WtEffects.StateMachineComponent
    return WtEffects.StateMachineComponent if effectType == WtVehicleEffectType.HUNTER_PROGRESS_BAR else WtEffects.SequenceComponent


class _SoundComponent(Component):

    def __init__(self, entityID, eventID):
        self.__eventID = eventID
        self.__soundEffect = None
        entity = BigWorld.entities.get(entityID)
        if entity is not None and entity.model is not None:
            self.__soundEffect = SoundGroups.g_instance.getSound3D(Math.Matrix(entity.model.root), backport.sound(self.__eventID))
        return

    def deactivate(self):
        self.stop()
        super(_SoundComponent, self).deactivate()

    def destroy(self):
        self.stop()
        self.__soundEffect = None
        return

    def play(self):
        if self.__soundEffect is not None and not self.__soundEffect.isPlaying:
            self.__soundEffect.play()
        return

    def stop(self):
        if self.__soundEffect is not None and self.__soundEffect.isPlaying:
            self.__soundEffect.stop()
        return


class _SequenceDescriptor(ComponentDescriptor):

    def __set__(self, instance, value):
        super(_SequenceDescriptor, self).__set__(instance, value)
        instance.initAnimatorState()


class VehicleIdleEffect(ScriptGameObject):
    animator = _SequenceDescriptor()

    def __init__(self, worldID, entityID):
        super(VehicleIdleEffect, self).__init__(worldID)
        self._entityID = entityID

    def activate(self):
        super(VehicleIdleEffect, self).activate()
        if isPlayerAvatar() and BigWorld.player().playerVehicleID == self._entityID:
            BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged
        self._updateAnimatorState()

    def deactivate(self):
        if isPlayerAvatar() and BigWorld.player().playerVehicleID == self._entityID:
            BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
        super(VehicleIdleEffect, self).deactivate()

    def initAnimatorState(self):
        self._updateAnimatorState()

    def _updateAnimatorState(self):
        pass

    def __onCameraChanged(self, cameraName, _=None):
        if self.animator is not None:
            self.animator.setEnabled(cameraName != 'sniper')
        self._updateAnimatorState()
        return


class HunterIdleEffectObject(VehicleIdleEffect):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def activate(self):
        super(HunterIdleEffectObject, self).activate()
        vehicle = BigWorld.entities.get(self._entityID)
        if isPlayerAvatar() and vehicle is not None:
            if vehicle.isPlayerVehicle:
                ctrl = self._sessionProvider.shared.vehicleState
                if ctrl is not None:
                    ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            else:
                ctrl = self._sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def deactivate(self):
        vehicle = BigWorld.entities.get(self._entityID)
        if isPlayerAvatar() and vehicle is not None:
            if vehicle.isPlayerVehicle:
                ctrl = self._sessionProvider.shared.vehicleState
                if ctrl is not None:
                    ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            else:
                ctrl = self._sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        super(HunterIdleEffectObject, self).deactivate()
        return

    def _updateAnimatorState(self):
        if not isPlayerAvatar():
            return
        else:
            vehicle = BigWorld.entities.get(self._entityID)
            if vehicle is not None:
                self._invalidateStun(vehicle.stunInfo)
            return

    def _invalidateStun(self, value):
        if self.animator is not None:
            self.animator.setEnabled(value < 1e-09)
        return

    def __onVehicleFeedbackReceived(self, stateID, vehicleID, value):
        from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
        if vehicleID == self._entityID and stateID == _FET.VEHICLE_STUN:
            self._invalidateStun(value.endTime)

    def __onVehicleStateUpdated(self, stateID, value):
        from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
        if stateID == VEHICLE_VIEW_STATE.STUN:
            self._invalidateStun(value.endTime)


class HunterPowerCollectorObject(HunterIdleEffectObject):

    def activate(self):
        super(HunterPowerCollectorObject, self).activate()
        arenaInfoCtrl = self._sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged += self.__onPowerPointsChanged
        return

    def deactivate(self):
        arenaInfoCtrl = self._sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged -= self.__onPowerPointsChanged
        super(HunterPowerCollectorObject, self).deactivate()
        return

    def _invalidateStun(self, value):
        if self.animator is not None:
            self.animator.setFloatParam('stunInfo', value)
        return

    def __onPowerPointsChanged(self, _):
        if self.animator is not None:
            self.animator.setTrigger('onLootPickup')
        return


class HunterProgressBarObject(VehicleIdleEffect):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    soundComponent = ComponentDescriptor()

    def __init__(self, worldID, entityID):
        super(HunterProgressBarObject, self).__init__(worldID, entityID)
        if not isPlayerAvatar():
            self.soundComponent = _SoundComponent(entityID, R.sounds.ev_white_tiger_hangar_electric_substance_t55())

    def activate(self):
        super(HunterProgressBarObject, self).activate()
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged += self.__onPowerPointsChanged
        if self.soundComponent is not None:
            self.soundComponent.play()
        return

    def deactivate(self):
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged -= self.__onPowerPointsChanged
        super(HunterProgressBarObject, self).deactivate()
        return

    def _updateAnimatorState(self):
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            self.__onPowerPointsChanged(arenaInfoCtrl.powerPoints)
        else:
            self.__onPowerPointsChanged(0)
        return

    def _invalidateStun(self, value):
        if self.animator is not None:
            self.animator.setFloatParam('stunInfo', value.endTime)
        return

    def __onPowerPointsChanged(self, value):
        if self.animator is not None:
            self.animator.setIntParam('power', value)
        return


class BossIdleEffect(VehicleIdleEffect):

    def activate(self):
        super(BossIdleEffect, self).activate()
        if not isPlayerAvatar():
            g_clientUpdateManager.addCallbacks({'tokens': self._updateTicketsState})

    def deactivate(self):
        if not isPlayerAvatar():
            g_clientUpdateManager.removeObjectCallbacks(self)
        super(BossIdleEffect, self).deactivate()

    def initAnimatorState(self):
        super(BossIdleEffect, self).initAnimatorState()
        if not isPlayerAvatar():
            self._updateTicketsState(None)
        return

    def _updateTicketsState(self, diff):
        from gui.wt_event.wt_event_helpers import getTicketName
        if diff is not None and getTicketName() not in diff:
            return
        else:
            eventController = dependency.instance(IGameEventController)
            enabled = eventController.hasEnoughTickets()
            if not isPlayerAvatar():
                if diff is None:
                    if self.animator is not None:
                        self.animator.setEnabled(enabled)
                        return
                elif eventController.getWtEventTokenName() in diff:
                    if self.animator is not None:
                        self.animator.setEnabled(enabled)
            return


class BossShieldIndicator(BossIdleEffect):
    soundComponent = ComponentDescriptor()

    def __init__(self, worldID, entityID, isSpecial):
        super(BossShieldIndicator, self).__init__(worldID, entityID)
        self.__isSpecial = isSpecial
        if not isPlayerAvatar():
            self.soundComponent = _SoundComponent(entityID, R.sounds.ev_white_tiger_hangar_electric_substance_wt())

    def _updateTicketsState(self, diff):
        super(BossShieldIndicator, self)._updateTicketsState(diff)
        value = 1.0
        isEnabled = True
        if self.animator is not None and not self.__isSpecial:
            eventController = dependency.instance(IGameEventController)
            isEnabled = eventController.hasEnoughTickets()
            value = float(isEnabled)
        self.animator.setFloatParam('shieldPercent', value)
        self.__switchSoundEffect(isEnabled)
        return

    def __switchSoundEffect(self, isEnabled):
        if self.soundComponent is None:
            return
        else:
            if isEnabled:
                self.soundComponent.play()
            else:
                self.soundComponent.stop()
            return
