# Embedded file name: scripts/client/gui/shared/utils/requesters/deprecated/VehicleItemsRequester.py
from gui.shared.utils.gui_items import VehicleItem

class VehicleItemsRequester(object):

    def __init__(self, vehicles):
        self.__vehicles = vehicles

    def getItems(self, types):
        items = {}
        for v in self.__vehicles:
            for type in types:
                currents = self.__getItemsByType(v, type)
                for current in currents:
                    if current:
                        current = items.setdefault(current, VehicleItem(compactDescr=current))
                        current.count += 1
                        current.vehicles.append(v)

        return items.values()

    def __getItemsByType(self, v, itemTypeName):
        vd = v.descriptor
        if itemTypeName == 'vehicleChassis':
            return [vd.chassis['compactDescr']]
        if itemTypeName == 'vehicleEngine':
            return [vd.engine['compactDescr']]
        if itemTypeName == 'vehicleRadio':
            return [vd.radio['compactDescr']]
        if itemTypeName == 'vehicleFuelTank':
            return [vd.fuelTank['compactDescr']]
        if itemTypeName == 'vehicleTurret':
            if v.hasTurrets:
                return [vd.turret['compactDescr']]
        if itemTypeName == 'vehicleGun':
            return [vd.gun['compactDescr']]
        if itemTypeName == 'optionalDevice':
            return [ od['compactDescr'] for od in vd.optionalDevices if od ]
        if itemTypeName == 'equipment':
            return v.equipments
        return []
