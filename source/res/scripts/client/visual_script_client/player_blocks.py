# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/player_blocks.py
import weakref
import BigWorld
from visual_script import ASPECT
from visual_script.block import Meta, Block
from visual_script.dependency import dependencyImporter
from visual_script.misc import errorVScript
from visual_script.slot_types import SLOT_TYPE
from visual_script.tunable_event_block import TunableEventBlock
from visual_script_client.vehicle_common import TunablePlayerVehicleEventBlock, getPartState, getPartNames, getPartName, TriggerListener
vehicles, helpers, TriggersManager, gun_marker_ctrl, Avatar, session = dependencyImporter('items.vehicles', 'helpers', 'TriggersManager', 'AvatarInputHandler.gun_marker_ctrl', 'Avatar', 'skeletons.gui.battle_session')

class PlayerMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @property
    def _avatar(self):
        if helpers.isPlayerAvatar():
            return BigWorld.player()
        errorVScript(self, 'BigWorld.player is not player avatar.')


class PlayerEventMeta(PlayerMeta):

    @classmethod
    def blockIcon(cls):
        pass


class GetPlayerVehicleGun(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerVehicleGun, self).__init__(*args, **kwargs)
        self._gunCanShoot = self._makeDataOutputSlot('gunCanShoot', SLOT_TYPE.BOOL, self._getGunCanShoot)
        self._gunPosition = self._makeDataOutputSlot('gunPosition', SLOT_TYPE.VECTOR3, self._getGunPosition)
        self._gunDirection = self._makeDataOutputSlot('gunDirection', SLOT_TYPE.VECTOR3, self._getGunDirection)

    @helpers.dependency.replace_none_kwargs(sessionProvider=session.IBattleSessionProvider)
    def _getGunCanShoot(self, sessionProvider):
        if sessionProvider is not None:
            canShoot, _ = sessionProvider.shared.ammo.canShoot()
            self._gunCanShoot.setValue(canShoot)
        return

    def _getGunPosition(self):
        avatar = self._avatar
        if avatar:
            position, _ = avatar.gunRotator.getCurShotPosition()
            self._gunPosition.setValue(position)

    def _getGunDirection(self):
        avatar = self._avatar
        if avatar:
            _, direction = avatar.gunRotator.getCurShotPosition()
            direction.normalise()
            self._gunDirection.setValue(direction)


class GetPlayerGunMarkerInfo(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerGunMarkerInfo, self).__init__(*args, **kwargs)
        self._pos = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, self._getPosition)
        self._dir = self._makeDataOutputSlot('direction', SLOT_TYPE.VECTOR3, self._getDirection)
        self._size = self._makeDataOutputSlot('size', SLOT_TYPE.FLOAT, self._getSize)

    @property
    def _markerInfo(self):
        avatar = self._avatar
        return avatar.gunRotator.markerInfo if avatar else None

    def _getPosition(self):
        markerInfo = self._markerInfo
        if markerInfo:
            self._pos.setValue(markerInfo[0])

    def _getDirection(self):
        markerInfo = self._markerInfo
        if markerInfo:
            self._dir.setValue(markerInfo[1])

    def _getSize(self):
        markerInfo = self._markerInfo
        if markerInfo:
            self._size.setValue(markerInfo[2])


class OnPlayerSnipeMode(TunableEventBlock, PlayerEventMeta, TriggerListener):
    _EVENT_SLOT_NAMES = ['onEnter', 'onExit']

    def onStartScript(self):
        manager = TriggersManager.g_manager
        if manager:
            manager.addListener(self)
        else:
            errorVScript(self, 'TriggersManager.g_manager is None')

    def onFinishScript(self):
        manager = TriggersManager.g_manager
        if manager:
            manager.delListener(self)
        else:
            errorVScript(self, 'TriggersManager.g_manager is None')

    def onTriggerActivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self._index = 0
            self._callOnEnter()

    def onTriggerDeactivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self._index = 1
            self._callOnExit()

    @TunableEventBlock.eventProcessor
    def _callOnEnter(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callOnExit(self):
        pass


class OnGunMarkerPenetrationStateChanged(TunableEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onChanged']

    def __init__(self, *args, **kwargs):
        super(OnGunMarkerPenetrationStateChanged, self).__init__(*args, **kwargs)
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.INT, None)
        self._oldResult = None
        return

    def onStartScript(self):
        avatar = self._avatar
        if avatar:
            avatar.guiSessionProvider.shared.crosshair.onGunMarkerStateChanged += self._onGunMarkerStateChanged

    def onFinishScript(self):
        avatar = self._avatar
        if avatar:
            crosshair = avatar.guiSessionProvider.shared.crosshair
            if crosshair:
                crosshair.onGunMarkerStateChanged -= self._onGunMarkerStateChanged

    def _onGunMarkerStateChanged(self, _, position, direction, collision):
        avatar = self._avatar
        if avatar:
            shotResultResolver = gun_marker_ctrl.createShotResultResolver()
            result = shotResultResolver.getShotResult(position, collision, direction, excludeTeam=avatar.team)
            if result != self._oldResult:
                self._oldResult = result
                self._callOutput(result)

    @TunableEventBlock.eventProcessor
    def _callOutput(self, result):
        self._state.setValue(result)


class GetPlayerVehicleDeviceState(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerVehicleDeviceState, self).__init__(*args, **kwargs)
        self._device = self._makeDataInputSlot('device', SLOT_TYPE.E_VEHICLE_DEVICE)
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.E_MODULE_STATE, self._execState)
        self._hasDevice = self._makeDataOutputSlot('hasDevice', SLOT_TYPE.BOOL, self._execHasDevice)

    def _execState(self):
        if helpers.isPlayerAvatar():
            deviceIdx = self._device.getValue()
            if deviceIdx >= len(vehicles.VEHICLE_DEVICE_TYPE_NAMES):
                errorVScript(self, 'unknown device identifier.')
                return
            state = getPartState(vehicles.VEHICLE_DEVICE_TYPE_NAMES[deviceIdx])
            self._state.setValue(state)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    def _execHasDevice(self):
        if helpers.isPlayerAvatar():
            deviceIdx = self._device.getValue()
            if deviceIdx >= len(vehicles.VEHICLE_DEVICE_TYPE_NAMES):
                errorVScript(self, 'unknown device identifier.')
                return
            deviceNames = [ pn + 'Health' for pn in getPartNames(vehicles.VEHICLE_DEVICE_TYPE_NAMES[deviceIdx]) ]
            isHas = any((te.name in deviceNames for te in BigWorld.player().vehicleTypeDescriptor.type.devices))
            self._hasDevice.setValue(isHas)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetPlayerVehicleTankmanState(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerVehicleTankmanState, self).__init__(*args, **kwargs)
        self._tankman = self._makeDataInputSlot('tankman', SLOT_TYPE.E_VEHICLE_TANKMAN)
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.E_MODULE_STATE, self._execState)
        self._hasTankman = self._makeDataOutputSlot('hasTankman', SLOT_TYPE.BOOL, self._execHasTankman)

    def _execState(self):
        if helpers.isPlayerAvatar():
            tankmanIdx = self._tankman.getValue()
            if tankmanIdx >= len(vehicles.VEHICLE_TANKMAN_TYPE_NAMES):
                errorVScript(self, 'unknown tankman identifier.')
                return
            state = getPartState(vehicles.VEHICLE_TANKMAN_TYPE_NAMES[tankmanIdx])
            self._state.setValue(state)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    def _execHasTankman(self):
        if helpers.isPlayerAvatar():
            tankmanIdx = self._tankman.getValue()
            if tankmanIdx >= len(vehicles.VEHICLE_TANKMAN_TYPE_NAMES):
                errorVScript(self, 'unknown tankman identifier.')
                return
            tankmanName = [ pn + 'Health' for pn in getPartNames(vehicles.VEHICLE_TANKMAN_TYPE_NAMES[tankmanIdx]) ]
            isHas = any((te.name in tankmanName for te in BigWorld.player().vehicleTypeDescriptor.type.tankmen))
            self._hasTankman.setValue(isHas)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OnPlayerVehicleShoot(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onShoot']

    @TunableEventBlock.eventProcessor
    def onPlayerShoot(self, aimInfo):
        pass


class OnPlayerShotMissed(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onMissed']

    @TunableEventBlock.eventProcessor
    def onPlayerShotMissed(self):
        pass


class OnPlayerAutoAim(TunablePlayerVehicleEventBlock, PlayerEventMeta, TriggerListener):
    _EVENT_SLOT_NAMES = ['onEnabled', 'onDisabled']

    def onStartScript(self):
        manager = TriggersManager.g_manager
        if manager:
            manager.addListener(self)
        else:
            errorVScript(self, 'TriggersManager.g_manager is None')

    def onFinishScript(self):
        manager = TriggersManager.g_manager
        if manager:
            manager.delListener(self)
        else:
            errorVScript(self, 'TriggersManager.g_manager is None')

    def onTriggerActivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE:
            self._index = 0
            self._callOnEnter()

    def onTriggerDeactivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE:
            self._index = 1
            self._callOnExit()

    @TunableEventBlock.eventProcessor
    def _callOnEnter(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callOnExit(self):
        pass


class OnPlayerMoveVehicle(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onMove']

    def __init__(self, *args, **kwargs):
        super(OnPlayerMoveVehicle, self).__init__(*args, **kwargs)
        self._forward = self._makeDataOutputSlot('forward', SLOT_TYPE.BOOL, None)
        self._backward = self._makeDataOutputSlot('backward', SLOT_TYPE.BOOL, None)
        self._left = self._makeDataOutputSlot('left', SLOT_TYPE.BOOL, None)
        self._right = self._makeDataOutputSlot('right', SLOT_TYPE.BOOL, None)
        self._cc25 = self._makeDataOutputSlot('cruise25pc', SLOT_TYPE.BOOL, None)
        self._cc50 = self._makeDataOutputSlot('cruise50pc', SLOT_TYPE.BOOL, None)
        self._break = self._makeDataOutputSlot('break', SLOT_TYPE.BOOL, None)
        return

    @TunableEventBlock.eventProcessor
    def onPlayerMove(self, moveCommands):
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.FORWARD, self._forward)
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.BACKWARD, self._backward)
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.ROTATE_LEFT, self._left)
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.ROTATE_RIGHT, self._right)
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.CRUISE_CONTROL25, self._cc25)
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.CRUISE_CONTROL50, self._cc50)
        self._processMoveCommand(moveCommands, Avatar.MOVEMENT_FLAGS.BLOCK_TRACKS, self._break)

    @staticmethod
    def _processMoveCommand(moveCommands, commandToCheck, slotToSet):
        if moveCommands & commandToCheck:
            slotToSet.setValue(True)
        else:
            slotToSet.setValue(False)


class OnPlayerVehicleDetectEnemy(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onDetect', 'onLost']

    def __init__(self, *args, **kwargs):
        super(OnPlayerVehicleDetectEnemy, self).__init__(*args, **kwargs)
        self._target = self._makeDataOutputSlot('target', SLOT_TYPE.VEHICLE, None)
        return

    def onPlayerDetectEnemy(self, new, lost):
        if new:
            self._index = 0
            self._callOutput(new[0])
        elif lost:
            self._index = 1
            self._callOutput(lost[0])

    @TunableEventBlock.eventProcessor
    def _callOutput(self, vehicle):
        self._target.setValue(weakref.proxy(vehicle))


class OnPlayerVehicleFireEvent(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onFire', 'onFireEnds']

    def onPlayerVehicleFireEvent(self, isStart):
        if isStart:
            self._index = 0
            self._callOutput()
        else:
            self._index = 1
            self._callOutput()

    @TunableEventBlock.eventProcessor
    def _callOutput(self):
        pass


class OnPlayerVehicleTankmanEvent(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onShocked', 'onHealed']

    def __init__(self, *args, **kwargs):
        super(OnPlayerVehicleTankmanEvent, self).__init__(*args, **kwargs)
        self._tankman = self._makeDataOutputSlot('tankman', SLOT_TYPE.E_VEHICLE_TANKMAN, None)
        return

    def onPlayerVehicleTankmanEvent(self, tankmanName, isHit):
        tankmanName = getPartName(tankmanName)
        if tankmanName in vehicles.VEHICLE_TANKMAN_TYPE_NAMES:
            tankman = vehicles.VEHICLE_TANKMAN_TYPE_NAMES.index(tankmanName)
            if isHit:
                self._index = 0
            else:
                self._index = 1
            self._callOutput(tankman)
        else:
            errorVScript(self, 'OnVehiclePlayerDeviceCrit unknown tankmanName')
            return

    @TunableEventBlock.eventProcessor
    def _callOutput(self, tankman):
        self._tankman.setValue(tankman)


class OnBootcampPlayerVehicleDetected(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onDetected', 'onLost']

    def onPlayerDetected(self, isDetected):
        if isDetected:
            self._index = 0
        else:
            self._index = 1
        self._callOutput()

    @TunableEventBlock.eventProcessor
    def _callOutput(self):
        pass


class OnPlayerVehicleDeviceCrit(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onDamaged',
     'onDestroyed',
     'onHealed',
     'onAutoHealToDamaged']

    def __init__(self, *args, **kwargs):
        super(OnPlayerVehicleDeviceCrit, self).__init__(*args, **kwargs)
        self._device = self._makeDataOutputSlot('device', SLOT_TYPE.E_VEHICLE_DEVICE, None)
        return

    def onPlayerVehicleDeviceEvent(self, deviceName, isCritical, isHit):
        deviceName = getPartName(deviceName)
        if deviceName in vehicles.VEHICLE_DEVICE_TYPE_NAMES:
            device = vehicles.VEHICLE_DEVICE_TYPE_NAMES.index(deviceName)
            if isHit:
                self._index = 0 if isCritical else 1
            else:
                self._index = 3 if isCritical else 2
            self._callOutput(device)
        else:
            errorVScript(self, 'OnVehiclePlayerDeviceCrit unknown deviceName')
            return

    @TunableEventBlock.eventProcessor
    def _callOutput(self, device):
        self._device.setValue(device)


class OnPlayerVehicleAreaTrigger(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onEnter', 'onExit']

    def __init__(self, *args, **kwargs):
        super(OnPlayerVehicleAreaTrigger, self).__init__(*args, **kwargs)
        self._trigger = self._makeDataInputSlot('trigger', SLOT_TYPE.AREA_TRIGGER)

    def onPlayerEnterTrigger(self, trigger, enter):
        if trigger == self._trigger.getValue().name:
            if enter:
                self._index = 0
            else:
                self._index = 1
            self._callOutput()

    @TunableEventBlock.eventProcessor
    def _callOutput(self):
        pass

    def validate(self):
        return 'Trigger value is required' if not self._trigger.hasValue() else super(OnPlayerVehicleAreaTrigger, self).validate()


class GetPlayerGunDispersionAngles(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerGunDispersionAngles, self).__init__(*args, **kwargs)
        self._current = self._makeDataOutputSlot('current', SLOT_TYPE.ANGLE, self._getCurrentDispersions)
        self._target = self._makeDataOutputSlot('target', SLOT_TYPE.ANGLE, self._getCurrentDispersions)
        self._ideal = self._makeDataOutputSlot('ideal', SLOT_TYPE.ANGLE, self._getIdealDispersion)

    def _getCurrentDispersions(self):
        avatar = self._avatar
        if avatar:
            angles = avatar.gunRotator.getCurShotDispersionAngles()
            self._current.setValue(angles[0])
            self._target.setValue(angles[1])

    def _getIdealDispersion(self):
        avatar = self._avatar
        if avatar:
            td = avatar.getVehicleDescriptor()
            self._ideal.setValue(td.gun.shotDispersionAngle)
