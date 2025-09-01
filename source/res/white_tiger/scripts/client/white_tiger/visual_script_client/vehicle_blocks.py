# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/visual_script_client/vehicle_blocks.py
import weakref
import GenericComponents
from visual_script.block import Block, InitParam, buildStrKeysValue
from visual_script.misc import ASPECT, EDITOR_TYPE, errorVScript
from visual_script.slot_types import SLOT_TYPE
from visual_script.vehicle_blocks import VehicleMeta
from visual_script.contexts.cgf_context import GameObjectWrapper
from visual_script.dependency import dependencyImporter
from soft_exception import SoftException
CGF, tankStructure, wt_battle_constants = dependencyImporter('CGF', 'vehicle_systems.tankStructure', 'white_tiger.gui.battle_control.white_tiger_battle_constants')

class InputSlotError(SoftException):
    pass


class GetGameObjectOfVehicle(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(GetGameObjectOfVehicle, self).__init__(*args, **kwargs)
        self._goToGet = self._getInitParams()
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._go = self._makeDataOutputSlot('gameObject', SLOT_TYPE.GAME_OBJECT, self._exec)

    def _exec(self):
        vehicle = self._vehicle.getValue()
        if vehicle is None:
            errorVScript(self, 'Please check input vehicle entity.')
            return
        elif vehicle.entityGameObject is None:
            errorVScript(self, 'Vehicle has no gameObject assigned to it.')
            return
        else:
            from vehicle_systems import vehicle_composition
            self.components = {'TankRootGameObject': vehicle_composition.VehicleSlots.CHASSIS,
             'HullGameObject': vehicle_composition.VehicleSlots.HULL,
             'TurretGameObject': vehicle_composition.VehicleSlots.TURRET,
             'GunGameObject': vehicle_composition.VehicleSlots.GUN_INCLINATION}
            requestedGOName = self.components[self._goToGet]
            entityGameObject = vehicle.entityGameObject
            requestedGO = GenericComponents.findSlot(entityGameObject, requestedGOName.value)
            if not requestedGO:
                errorVScript(self, 'Entity {0} has no {1}'.format(entityGameObject.name, self._goToGet))
            goWrapper = GameObjectWrapper(requestedGO)
            self._go.setValue(weakref.proxy(goWrapper))
            return

    @classmethod
    def initParams(cls):
        components = ['TankRootGameObject',
         'HullGameObject',
         'TurretGameObject',
         'GunGameObject']
        return [InitParam('GO to get', SLOT_TYPE.STR, buildStrKeysValue(*components), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def captionText(self):
        return 'Get {}'.format(self._goToGet)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class WTGetVehicleName(Block, VehicleMeta):

    def __init__(self, *args, **kwargs):
        super(WTGetVehicleName, self).__init__(*args, **kwargs)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._name = self._makeDataOutputSlot('name', SLOT_TYPE.STR, self._getName)

    def _getName(self):
        vehicle = self._vehicle.getValue()
        name = ''
        if vehicle.typeDescriptor:
            name = vehicle.typeDescriptor.name
        self._name.setValue(name)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class WTSetBaseCommand(Block, VehicleMeta):
    _COMMAND = ['ATTACK_BASE', 'DEFEND_BASE']

    def __init__(self, *args, **kwargs):
        super(WTSetBaseCommand, self).__init__(*args, **kwargs)
        self._inputSlot = self._makeEventInputSlot('in', self._execute)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._command = self._getInitParams()
        self._command = self._makeDataInputSlot('command', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._command.setEditorData(self._COMMAND)
        self._base = self._makeDataInputSlot('baseID', SLOT_TYPE.INT)
        self._outSlot = self._makeEventOutputSlot('out')

    def validate(self):
        if not self._vehicle.hasValue():
            return 'Vehicle is required'
        if not self._command.hasValue():
            return 'Command is required'
        return 'Base ID is required' if not self._base.hasValue() else None

    def _execute(self):
        vehicle = self._vehicle.getValue()
        if not vehicle:
            return
        command = self._command.getValue()
        ctrl = vehicle.guiSessionProvider.shared.chatCommands
        ctrl.handleChatCommand(command, self._base.getValue())
        self._outSlot.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class WTSetInspireMarker(Block):

    def __init__(self, *args, **kwargs):
        super(WTSetInspireMarker, self).__init__(*args, **kwargs)
        self._inputSlot = self._makeEventInputSlot('in', self._execute)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._active = self._makeDataInputSlot('isActive', SLOT_TYPE.BOOL)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        vehicle = self._vehicle.getValue()
        active = self._active.getValue()
        if not vehicle:
            return
        ctrl = vehicle.guiSessionProvider.shared.vehicleState
        ctrl.notifyStateChanged(wt_battle_constants.VEHICLE_VIEW_STATE.WT_INSPIRE, (vehicle.id, active))
        self._outSlot.call()
