# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/player_blocks.py
import weakref
import typing
import BigWorld
from aih_constants import CTRL_MODES
from visual_script import ASPECT
from visual_script.ability_common import Stage
from visual_script.block import Meta, Block, InitParam, buildStrKeysValue
from visual_script.dependency import dependencyImporter
from visual_script.misc import errorVScript, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.type import VScriptEnum
from visual_script.tunable_event_block import TunableEventBlock
from visual_script_client.vehicle_common import TunablePlayerVehicleEventBlock, getPartState, getPartNames, getPartName, TriggerListener
import items.vehicles as vehicles
if typing.TYPE_CHECKING:
    from Vehicle import StunInfo
helpers, TriggersManager, gun_marker_ctrl, equipment_ctrl, Avatar = dependencyImporter('helpers', 'TriggersManager', 'AvatarInputHandler.gun_marker_ctrl', 'gui.battle_control.controllers.consumables.equipment_ctrl', 'Avatar')

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
        self._gunPosition = self._makeDataOutputSlot('gunPosition', SLOT_TYPE.VECTOR3, self._getGunPosition)
        self._gunDirection = self._makeDataOutputSlot('gunDirection', SLOT_TYPE.VECTOR3, self._getGunDirection)

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


class OnPlayerSPGMode(TunableEventBlock, PlayerEventMeta, TriggerListener):
    _EVENT_SLOT_NAMES = ['onEnterTopDown', 'onEnterTrajectory', 'onExit']

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
        if triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_ENTER_SPG_STRATEGIC_MODE:
            self._index = 0
            self._callOnEnterTopDown()
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_ENTER_SPG_SNIPER_MODE:
            self._index = 1
            self._callOnEnterTrajectory()
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_LEAVE_SPG_MODE:
            self._index = 2
            self._callOnExit()

    @TunableEventBlock.eventProcessor
    def _callOnEnterTopDown(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callOnEnterTrajectory(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callOnExit(self):
        pass


class OnPlayerControlModeChange(TunableEventBlock, PlayerEventMeta, TriggerListener):
    _EVENT_SLOT_NAMES = ['OnEnter', 'OnExit']
    __CTRL_MODE_ANY = 'Any mode'

    def __init__(self, *args, **kwargs):
        super(OnPlayerControlModeChange, self).__init__(*args, **kwargs)
        self._controlMode = self._getInitParams()
        self._previousMode = self._makeDataOutputSlot('previous mode', PlayerControlMode.slotType(), None)
        self._currentMode = self._makeDataOutputSlot('current mode', PlayerControlMode.slotType(), None)
        return

    @classmethod
    def initParams(cls):
        allModes = [OnPlayerControlModeChange.__CTRL_MODE_ANY] + list(CTRL_MODES)
        return [InitParam('ControlMode', SLOT_TYPE.STR, buildStrKeysValue(*allModes), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def captionText(self):
        return 'On Change Control Mode (' + self._controlMode.upper() + ')'

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
        if triggerType is not TriggersManager.TRIGGER_TYPE.CTRL_MODE_CHANGE:
            return
        isAnyMode = self._controlMode == OnPlayerControlModeChange.__CTRL_MODE_ANY
        previousMode = params.get('previousMode')
        currentMode = params.get('currentMode')
        if isAnyMode or previousMode == self._controlMode:
            self._index = 1
            self._callOnExit(previousMode, currentMode)
        if isAnyMode or currentMode == self._controlMode:
            self._index = 0
            self._callOnEnter(previousMode, currentMode)

    @TunableEventBlock.eventProcessor
    def _callOnExit(self, previousMode, currentMode):
        self.__setOutputValues(previousMode, currentMode)

    @TunableEventBlock.eventProcessor
    def _callOnEnter(self, previousMode, currentMode):
        self.__setOutputValues(previousMode, currentMode)

    def __setOutputValues(self, previousMode, currentMode):
        previousModeIndex = PlayerControlMode.nameToIndex(previousMode)
        self._previousMode.setValue(previousModeIndex)
        currentModeIndex = PlayerControlMode.nameToIndex(currentMode)
        self._currentMode.setValue(currentModeIndex)


class IsControlModeActive(Block, PlayerEventMeta):

    def __init__(self, *args, **kwargs):
        super(IsControlModeActive, self).__init__(*args, **kwargs)
        self._controlMode = self._makeDataInputSlot('control mode', PlayerControlMode.slotType())
        self._active = self._makeDataOutputSlot('active', SLOT_TYPE.BOOL, self.__execute)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def __execute(self):
        player = BigWorld.player()
        aih = player.inputHandler if player else None
        if not aih:
            errorVScript(self, 'Cannot get players input handler')
            return
        else:
            controlMode = self._controlMode.getValue()
            self._active.setValue(controlMode == PlayerControlMode.nameToIndex(aih.ctrlModeName))
            return


class PlayerControlMode(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return CTRL_MODES

    @classmethod
    def nameToIndex(cls, ctrlModeName):
        return cls.vs_enum().index(ctrlModeName)

    @classmethod
    def _vs_collectEnumEntries(cls):
        entriesData = {}
        for name in cls.vs_enum():
            entriesData[name] = cls.vs_enum().index(name)

        return entriesData

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT]


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


class OnPlayerShotHit(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onHit']

    def __init__(self, *args, **kwargs):
        super(OnPlayerShotHit, self).__init__(*args, **kwargs)
        self._target = self._makeDataOutputSlot('target', SLOT_TYPE.VEHICLE, None)
        self._flags = self._makeDataOutputSlot('hitFlags', SLOT_TYPE.INT, None)
        return

    @TunableEventBlock.eventProcessor
    def onPlayerShotHit(self, target, flags):
        if target is not None:
            self._target.setValue(weakref.proxy(target))
        else:
            self._target.setValue(None)
        self._flags.setValue(flags)
        return


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


class OnShowTracer(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onShow']

    def __init__(self, *args, **kwargs):
        super(OnShowTracer, self).__init__(*args, **kwargs)
        self._attacker = self._makeDataOutputSlot('attacker', SLOT_TYPE.VEHICLE, None)
        self._isRicochet = self._makeDataOutputSlot('isRicochet', SLOT_TYPE.BOOL, None)
        self._startPoint = self._makeDataOutputSlot('startPoint', SLOT_TYPE.VECTOR3, None)
        self._direction = self._makeDataOutputSlot('direction', SLOT_TYPE.VECTOR3, None)
        self._velocity = self._makeDataOutputSlot('velocity', SLOT_TYPE.FLOAT, None)
        self._gravity = self._makeDataOutputSlot('gravity', SLOT_TYPE.FLOAT, None)
        self._maxDist = self._makeDataOutputSlot('maxDist', SLOT_TYPE.FLOAT, None)
        return

    @TunableEventBlock.eventProcessor
    def onShowTracer(self, attacker, isRicochet, startPoint, velocity, gravity, maxShotDist):
        if attacker is not None:
            self._attacker.setValue(weakref.proxy(attacker))
        else:
            self._attacker.setValue(None)
        self._isRicochet.setValue(bool(isRicochet))
        self._startPoint.setValue(startPoint)
        self._velocity.setValue(velocity.length)
        velocity.normalise()
        self._direction.setValue(velocity)
        self._gravity.setValue(gravity)
        self._maxDist.setValue(maxShotDist)
        return


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


class GetPlayerEquipments(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerEquipments, self).__init__(*args, **kwargs)
        self._equipments = self._makeDataOutputSlot('equipments', arrayOf(SLOT_TYPE.STR), self._getEquipments)

    def _getEquipments(self):
        avatar = self._avatar
        res = []
        if avatar:
            eqs = avatar.guiSessionProvider.shared.equipments.getOrderedEquipmentsLayout()
            for _, item in eqs:
                res.append(item.getDescriptor().name)

        self._equipments.setValue(res)


class GetPlayerEquipmentState(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(GetPlayerEquipmentState, self).__init__(*args, **kwargs)
        self._equipmentName = self._makeDataInputSlot('equipment', SLOT_TYPE.STR)
        self._equipped = self._makeDataOutputSlot('isEquipped', SLOT_TYPE.BOOL, self._isEquipped)
        self._availableToUse = self._makeDataOutputSlot('isAvailableToUse', SLOT_TYPE.BOOL, self._isAvailableToUse)
        self._canActivate = self._makeDataOutputSlot('canBeActivated', SLOT_TYPE.BOOL, self._canBeActivated)
        self._stage = self._makeDataOutputSlot('stage', Stage.slotType(), self._getStage)

    @property
    def _equipment(self):
        avatar = self._avatar
        if avatar:
            equipName = self._equipmentName.getValue()
            eqs = avatar.guiSessionProvider.shared.equipments.getOrderedEquipmentsLayout()
            for _, item in eqs:
                if item.getDescriptor().name == equipName:
                    return item

        return None

    def _isEquipped(self):
        self._equipped.setValue(self._equipment is not None)
        return

    def _canBeActivated(self):
        item = self._equipment
        if item is not None:
            result, info = item.canActivate()
            if isinstance(info, equipment_ctrl.NeedEntitySelection):
                result = True
            self._canActivate.setValue(result)
        return

    def _isAvailableToUse(self):
        item = self._equipment
        if item is not None:
            self._availableToUse.setValue(item.isAvailableToUse)
        return

    def _getStage(self):
        item = self._equipment
        if item is not None:
            self._stage.setValue(item.getStage())
        return


class OnPlayerVehicleStun(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onStun', 'onStunHealed', 'onStunAutoHeal']

    def __init__(self, *args, **kwargs):
        super(OnPlayerVehicleStun, self).__init__(*args, **kwargs)
        self._reset()
        self._stunDuration = self._makeDataOutputSlot('stunDuration', SLOT_TYPE.FLOAT, None)
        return

    def _reset(self):
        self._lastStartTime = 0.0
        self._lastDuration = 0.0

    def onStunInfoUpdated(self, stunInfo):
        if stunInfo.duration > 0:
            self._stunDuration.setValue(stunInfo.duration)
            self._lastDuration = stunInfo.duration
            self._lastStartTime = stunInfo.startTime
            self._index = 0
            self._callOutput()
        elif stunInfo.duration == 0.0 and self._lastStartTime != 0.0:
            self._index = 1 if self._lastStartTime + self._lastDuration > BigWorld.serverTime() else 2
            self._reset()
            self._callOutput()
        elif stunInfo.duration == 0.0 and self._lastStartTime == 0.0:
            self._reset()
        else:
            self._reset()
            errorVScript(self, 'OnPlayerVehicleStun has got inconsistent stun data.')

    @TunableEventBlock.eventProcessor
    def _callOutput(self):
        pass


class OnVehicleSixthSenseActivated(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onDetected']

    @TunableEventBlock.eventProcessor
    def onSixthSenceActivated(self):
        pass


class OnPlayerUsedAOEEquipment(TunablePlayerVehicleEventBlock, PlayerEventMeta):
    _EVENT_SLOT_NAMES = ['onEquipmentUsed']

    def __init__(self, *args, **kwargs):
        super(OnPlayerUsedAOEEquipment, self).__init__(*args, **kwargs)
        self._name = self._makeDataOutputSlot('name', SLOT_TYPE.STR, None)
        self._position = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, None)
        return

    @TunableEventBlock.eventProcessor
    def onPlayerUsedAoEEquipment(self, name, position):
        self._name.setValue(name)
        self._position.setValue(position)
