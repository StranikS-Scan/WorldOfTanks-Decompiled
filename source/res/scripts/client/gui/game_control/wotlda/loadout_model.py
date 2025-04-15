# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wotlda/loadout_model.py
from typing import List, Tuple, Union, Any, Optional, TYPE_CHECKING
from dict2model import models, fields, utils
from dict2model.schemas import Schema, validate
from gui.game_control.wotlda.constants import EQUIPMENT_ARCHETYPE_1, EQUIPMENT_ARCHETYPE_2, EQUIPMENT_ARCHETYPE_3, ExpectedArchetypes, OptDeviceAssistType, LOADOUT_USAGE_PERCENTAGE
from renewable_subscription_common.optional_devices_usage_config import VehicleLoadout
if TYPE_CHECKING:
    from dict2model.fields import Number
    _OptDevicePreset = Tuple[OptDeviceAssistType, int, List[VehicleLoadout]]
_MODERNIZED_ARCHETYPES_TO_SIMPLE_DEVICES = {'modernizedAimDrivesAimingStabilizer': 'enhancedAimDrives',
 'modernizedTurbochargerRotationMechanism': 'turbocharger',
 'modernizedExtraHealthReserveAntifragmentationLining': 'extraHealthReserve',
 'modernizedImprovedSightsEnhancedAimDrives': 'improvedSights'}
_SIMPLE_DEVICES_TO_MODERNIZED_ARCHETYPES = {'enhancedAimDrives': 'modernizedAimDrivesAimingStabilizer',
 'turbocharger': 'modernizedTurbochargerRotationMechanism',
 'extraHealthReserve': 'modernizedExtraHealthReserveAntifragmentationLining',
 'improvedSights': 'modernizedImprovedSightsEnhancedAimDrives'}

class VehicleIdField(fields.Integer):

    def _deserialize(self, incoming, **kwargs):
        return None if incoming is None else super(VehicleIdField, self)._deserialize(incoming, **kwargs)


class PercentageField(fields.Float):

    def _deserialize(self, incoming, **kwargs):
        return 0 if incoming is None else super(PercentageField, self)._deserialize(incoming, **kwargs)


class NullString(fields.String):

    def _deserialize(self, incoming, **kwargs):
        return '' if incoming is None else self._convert(incoming)


class OneOfArchetypes(validate.OneOf):

    def __call__(self, incoming):
        if incoming:
            super(OneOfArchetypes, self).__call__(incoming)


class EquipmentField(NullString):

    def __init__(self):
        super(EquipmentField, self).__init__(required=True, default=None, deserializedValidators=OneOfArchetypes(ExpectedArchetypes))
        return


class EmptyLoadoutField(fields.UniCapList):

    def _convert(self, incoming, onlyPublic, method):
        return {} if not incoming else super(EmptyLoadoutField, self)._convert(incoming, onlyPublic, method)


class PercentRange(validate.Range):

    def __init__(self):
        super(PercentRange, self).__init__(minValue=0.0, maxValue=100.0)

    def __call__(self, incoming):
        if incoming is None:
            return
        else:
            super(PercentRange, self).__call__(incoming)
            return


class BaseOptDeviceLoadoutModel(models.Model):
    __slots__ = ('linkedVehicleID', 'equipmentArchetype1', 'equipmentArchetype2', 'equipmentArchetype3', 'usagePercentage')

    def __init__(self, vehicle_id, equipment_archetype_id_1, equipment_archetype_id_2, equipment_archetype_id_3, usage_percentage):
        super(BaseOptDeviceLoadoutModel, self).__init__()
        self.linkedVehicleID = vehicle_id
        self.equipmentArchetype1 = equipment_archetype_id_1
        self.equipmentArchetype2 = equipment_archetype_id_2
        self.equipmentArchetype3 = equipment_archetype_id_3
        self.usagePercentage = usage_percentage

    def getDevices(self, getModernized=False):
        devices = [ device for device in (self.equipmentArchetype1, self.equipmentArchetype2, self.equipmentArchetype3) if device ]
        if not getModernized:
            return [ _MODERNIZED_ARCHETYPES_TO_SIMPLE_DEVICES.get(device, device) for device in devices ]
        return [ self._getDeviceTierArchetype(device) for device in devices ]

    def _getDeviceTierArchetype(self, device):
        return _SIMPLE_DEVICES_TO_MODERNIZED_ARCHETYPES.get(device, device)


class BaseOptDeviceLoadoutSchema(Schema[BaseOptDeviceLoadoutModel]):

    def __init__(self):
        super(BaseOptDeviceLoadoutSchema, self).__init__(fields={'vehicle_id': VehicleIdField(required=True, default=None),
         EQUIPMENT_ARCHETYPE_1: EquipmentField(),
         EQUIPMENT_ARCHETYPE_2: EquipmentField(),
         EQUIPMENT_ARCHETYPE_3: EquipmentField(),
         LOADOUT_USAGE_PERCENTAGE: PercentageField(required=True, default=0.0, deserializedValidators=PercentRange())}, modelClass=BaseOptDeviceLoadoutModel)
        return


baseOptDeviceLoadoutSchema = BaseOptDeviceLoadoutSchema()

class VehicleOptDeviceLoadoutsModel(models.Model):
    __slots__ = ('vehicleId', 'gold', 'legend')

    def __init__(self, vehicleId, gold, legend):
        super(VehicleOptDeviceLoadoutsModel, self).__init__()
        self.vehicleId = vehicleId
        self.gold = gold
        self.legend = legend

    def convertToView(self):
        goldLoadouts = self._parse(self.gold)
        legendLoadouts = self._parse(self.legend)
        return (goldLoadouts, legendLoadouts)

    def _parse(self, loadoutModel):
        assistType = OptDeviceAssistType.NODATA
        loadouts = []
        resultVehicleID = self.vehicleId
        for loadout in loadoutModel:
            vehicleLoadout = VehicleLoadout([loadout.equipmentArchetype1, loadout.equipmentArchetype2, loadout.equipmentArchetype3], loadout.usagePercentage)
            loadouts.append(vehicleLoadout)
            if assistType == OptDeviceAssistType.NODATA:
                linkedVehicleID = loadout.linkedVehicleID
                assistType = self._determineAssistType(self.vehicleId, linkedVehicleID)
                if assistType == OptDeviceAssistType.LINKED:
                    resultVehicleID = linkedVehicleID

        return (assistType, resultVehicleID, loadouts)

    def _determineAssistType(self, vehicleId, linkedVehicleID):
        if linkedVehicleID is None:
            return OptDeviceAssistType.COMBINED
        elif linkedVehicleID == vehicleId:
            return OptDeviceAssistType.NORMAL
        else:
            return OptDeviceAssistType.LINKED if linkedVehicleID != vehicleId else OptDeviceAssistType.NODATA


class VehicleOptDeviceLoadoutsSchema(Schema[VehicleOptDeviceLoadoutsModel]):

    def __init__(self):
        super(VehicleOptDeviceLoadoutsSchema, self).__init__(fields={'vehicleId': fields.Integer(required=True),
         'gold': EmptyLoadoutField(fieldOrSchema=baseOptDeviceLoadoutSchema, required=False),
         'legend': EmptyLoadoutField(fieldOrSchema=baseOptDeviceLoadoutSchema, required=False)}, modelClass=VehicleOptDeviceLoadoutsModel)


vehicleOptDeviceLoadoutsSchema = VehicleOptDeviceLoadoutsSchema()
