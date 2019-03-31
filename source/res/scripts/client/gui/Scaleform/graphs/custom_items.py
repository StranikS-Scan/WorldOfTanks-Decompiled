# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/graphs/custom_items.py
# Compiled at: 2011-06-14 19:48:09
from items import ITEM_TYPE_NAMES, vehicles
from gui.Scaleform.graphs import _VEHICLE_TYPE_NAME
from gui.Scaleform.graphs import SMALL_ICONS_PATH
from gui.Scaleform.utils.gui_items import FittingItem, InventoryItem, InventoryVehicle
import nations
import pickle
INVENTORY_ITEM_CREW_IDX = 'crew'
INVENTORY_ITEM_BROKEN_IDX = 'repair'
INVENTORY_ITEM_SETTINGS_IDX = 'settings'
INVENTORY_ITEM_LOCKED_IDX = 'lock'
INVENTORY_ITEM_EQS_IDX = 'eqs'
INVENTORY_ITEM_EQS_LAYOUT_IDX = 'eqsLayout'
INVENTORY_ITEM_SHELLS_IDX = 'shells'
INVENTORY_ITEM_SHELLS_LAYOUT_IDX = 'shellsLayout'

class _VehicleComponent(FittingItem):

    def __init__(self, compactDescr):
        self.__descriptor = None
        self.intCompactDescr = compactDescr
        itemTypeID, nationID, compTypeID = vehicles.parseIntCompactDescr(compactDescr)
        itemTypeName = ITEM_TYPE_NAMES[itemTypeID]
        FittingItem.__init__(self, compactDescr, itemTypeName)
        self.compTypeID = compTypeID
        self.nationID = nationID
        return

    @property
    def descriptor(self):
        """
        Descriptor for Item
        VehicleDescr for vehicles
        """
        if self.__descriptor is None:
            if self.itemTypeName == _VEHICLE_TYPE_NAME:
                self.__descriptor = vehicles.VehicleDescr(typeID=(self.nationID, self.compTypeID))
            else:
                self.__descriptor = vehicles.getDictDescr(self.compactDescr)
        return self.__descriptor

    @property
    def nation(self):
        return self.nationID

    @property
    def nationName(self):
        return nations.NAMES[self.nationID]

    @property
    def name(self):
        if self.itemTypeName == _VEHICLE_TYPE_NAME:
            return self.descriptor.type.userString
        return self.descriptor['userString']

    @property
    def smallIcon(self):
        return SMALL_ICONS_PATH % {'type': self.itemTypeName,
         'unicName': self.unicName.replace(':', '-')}

    @property
    def hasTurrets(self):
        """
        @return: True if vehicle has at least one not fake turret, False otherwise
        """
        return len(self.descriptor.type.hull.get('fakeTurrets', {}).get('lobby', ())) != len(self.descriptor.type.turrets)

    def pack(self):
        return pickle.dumps([_VehicleComponent, (self.intCompactDescr,)])


class _InventoryItem(InventoryItem):

    @property
    def nationName(self):
        return nations.NAMES[self.nation]

    @property
    def smallIcon(self):
        return SMALL_ICONS_PATH % {'type': self.itemTypeName,
         'unicName': self.unicName.replace(':', '-')}


class _InventoryVehicle(InventoryVehicle):

    @property
    def nationName(self):
        return nations.NAMES[self.nation]

    @property
    def smallIcon(self):
        return SMALL_ICONS_PATH % {'type': self.itemTypeName,
         'unicName': self.unicName.replace(':', '-')}


def _makeInventoryItem(itemTypeID, itemCompactDesc, count):
    return _InventoryItem(itemTypeName=ITEM_TYPE_NAMES[itemTypeID], compactDescr=itemCompactDesc, count=count)


def _makeInventoryVehicle(invID, vCompactDescr, data):
    repairCost, health = data.get(INVENTORY_ITEM_BROKEN_IDX, {}).get(invID, (0, 0))
    return _InventoryVehicle(compactDescr=vCompactDescr, id=invID, crew=data.get(INVENTORY_ITEM_CREW_IDX, {}).get(invID, []), shells=data.get(INVENTORY_ITEM_SHELLS_IDX, {}).get(invID, []), ammoLayout=data.get(INVENTORY_ITEM_SHELLS_LAYOUT_IDX, {}).get(invID, {}), repairCost=repairCost, health=health, lock=data.get(INVENTORY_ITEM_LOCKED_IDX, {}).get(invID, 0), equipments=data.get(INVENTORY_ITEM_EQS_IDX, {}).get(invID, [0, 0, 0]), equipmentsLayout=data.get(INVENTORY_ITEM_EQS_LAYOUT_IDX, {}).get(invID, [0, 0, 0]), settings=data.get(INVENTORY_ITEM_SETTINGS_IDX, {}).get(invID, 0))
