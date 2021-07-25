# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_equipment.py
import logging
import weakref
from account_shared import LayoutIterator
from items.components.detachment_components import PerkBonusInfluenceItem, PerkBonusApplier
from shared_utils import first
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from items import vehicles, EQUIPMENT_TYPES, ITEM_TYPES
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
ZERO_COMP_DESCR = 0
EMPTY_INVENTORY_DATA = [ZERO_COMP_DESCR]
LAYOUT_ITEM_SIZE = 2
EMPTY_ITEM = None

class _Equipment(object):
    __slots__ = ('_storage', '__guiItemType', '__capacity', '_proxy')
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, guiItemType, capacity, proxy, fromRawData, *args):
        self.__capacity = capacity
        self.__guiItemType = guiItemType
        self._proxy = proxy
        if args:
            if len(args) != self.getCapacity():
                raise SoftException('Length of arguments is not valid, args: {} for equipment: {}'.format(args, self))
            self._storage = []
            for item in args:
                if fromRawData:
                    self._storage.append(item)
                self._storage.append(self._getItemData(item) if item is not None else EMPTY_ITEM)

        else:
            self._storage = [EMPTY_ITEM] * self.getCapacity()
        return

    def __setitem__(self, slotIdx, item):
        self._validateType(item)
        self._validateIndex(slotIdx)
        if item is not None:
            item = self._getItemData(item)
        self._storage[slotIdx] = item
        return

    def __getitem__(self, slotIdx):
        if slotIdx >= len(self._storage):
            _logger.error('Wrong slotIdx=[%d] for Equipment=[%s]', slotIdx, self)
            return EMPTY_ITEM
        else:
            data = self._storage[slotIdx]
            return self._createItem(data) if data is not None else EMPTY_ITEM

    def __contains__(self, item):
        return item.intCD in self.getIntCDs()

    def __iter__(self):
        for itemData in self._storage:
            if itemData:
                yield self._createItem(itemData)
            yield EMPTY_ITEM

    def __len__(self):
        return len(self._storage)

    def __eq__(self, equipment):
        if len(self) == len(equipment):
            for i, item in enumerate(self):
                if not item == equipment[i]:
                    return False

            return True
        return False

    def __ne__(self, equipment):
        return not self.__eq__(equipment)

    def __repr__(self):
        return '{}, guiItemType: {}, capacity: {}'.format(self.__class__.__name__, GUI_ITEM_TYPE_NAMES[self.__guiItemType], self.__capacity)

    def clear(self):
        self._storage = [EMPTY_ITEM] * self.getCapacity()

    def getCapacity(self):
        return self.__capacity

    def containsIntCD(self, intCD, slotIdx=None):
        if slotIdx is None:
            installed = self.getIntCDs(default=EMPTY_ITEM)
            return intCD in installed
        else:
            return False if slotIdx >= self.getCapacity() else self._storage[slotIdx] != EMPTY_ITEM and self._getIntCD(self._storage[slotIdx]) == intCD

    def getIntCDs(self, default=ZERO_COMP_DESCR):
        return [ (self._getIntCD(itemData) if itemData != EMPTY_ITEM else default) for itemData in self._storage ]

    def getItems(self):
        return [ item for item in self if item != EMPTY_ITEM ]

    def copy(self):
        return self.__class__(self.__guiItemType, self.__capacity, self._proxy, True, *self._storage)

    def index(self, item):
        intCDs = self.getIntCDs()
        return intCDs.index(item.intCD) if item.intCD in intCDs else None

    def swap(self, leftID, rightID):
        self._storage[leftID], self._storage[rightID] = self._storage[rightID], self._storage[leftID]

    def _getIntCD(self, itemData):
        return itemData

    def _validateIndex(self, idx):
        if idx >= self.getCapacity():
            raise SoftException('Index {} exceeds the layout size!'.format(idx))

    def _validateType(self, item):
        if item is not None and item.itemTypeID != self.__guiItemType:
            raise SoftException('The item {} is not suitable for {}!'.format(item, self))
        return

    def _createItem(self, itemData):
        raise NotImplementedError

    def _getItemData(self, item):
        raise NotImplementedError


class _EquipmentCollector(object):
    __slots__ = ('_installed', '_layout', '__slots', '_proxy')

    def __init__(self, vehDescr, proxy, invData=None):
        super(_EquipmentCollector, self).__init__()
        self._proxy = proxy
        supplySlots = self.__getSupplySlots(vehDescr)
        self.__slots = self._readSlots(supplySlots)
        capacity = self._getCapacity(vehDescr)
        items, itemsLayout = self._parse(vehDescr, capacity, invData)
        self._installed = self._equipmentClazz()(self._guiItemType(), capacity, proxy, True, *items)
        self._layout = self._equipmentClazz()(self._guiItemType(), capacity, proxy, True, *itemsLayout)

    @property
    def installed(self):
        return self._installed

    def setInstalled(self, *values):
        self._installed = self._equipmentClazz()(self._guiItemType(), self.layoutCapacity, self._proxy, False, *values)

    @property
    def layout(self):
        return self._layout

    def setLayout(self, *values):
        self._layout = self._equipmentClazz()(self._guiItemType(), self.layoutCapacity, self._proxy, False, *values)

    def setByOther(self, collector):
        self.setInstalled(*collector.installed)
        self.setLayout(*collector.layout)

    @property
    def layoutCapacity(self):
        return self._layout.getCapacity()

    @property
    def slots(self):
        return self.__slots

    def swap(self, leftID, rightID):
        self._layout.swap(leftID, rightID)
        self._installed.swap(leftID, rightID)

    def _getCapacity(self, vehDescr):
        return len(self.__slots)

    def _equipmentClazz(self):
        raise NotImplementedError

    def _itemType(self):
        raise NotImplementedError

    def _guiItemType(self):
        raise NotImplementedError

    def _parse(self, vehDescr, capacity, invData):
        raise NotImplementedError

    def _readSlots(self, supplySlots):
        return [ slot for slot in supplySlots if slot.itemType == self._itemType() ]

    @staticmethod
    def __getSupplySlots(vehDescr):
        slotIDs = vehDescr.type.supplySlots.slotIDs
        slotDescrs = vehicles.g_cache.supplySlots().slotDescrs
        return [ slotDescrs[slotID] for slotID in slotIDs ]


class _ExpendableEquipment(_Equipment):
    __slots__ = ()

    def _createItem(self, intCD):
        return self._itemsCache.items.getItemByCD(intCD)

    def _getItemData(self, item):
        return item.intCD


class _ExpendableCollector(_EquipmentCollector):
    __slots__ = ()

    def _equipmentClazz(self):
        return _ExpendableEquipment

    def _itemType(self):
        return ITEM_TYPES.equipment

    def _readSlots(self, supplySlots):
        return [ slot for slot in supplySlots if slot.itemType == self._itemType() and slot.equipmentType == self._expendableType() ]

    def _expendableType(self):
        raise NotImplementedError


class _ConsumablesCollector(_ExpendableCollector):
    __slots__ = ()

    def _expendableType(self):
        return EQUIPMENT_TYPES.regular

    def _guiItemType(self):
        return GUI_ITEM_TYPE.EQUIPMENT

    def _parse(self, vehDescr, capacity, invData):
        eqs = self.__getInvData(invData.get('eqs', []), vehDescr, capacity)
        eqsLayout = self.__getInvData(invData.get('eqsLayout', []), vehDescr, capacity)
        return (self.__parseEqs(eqs), self.__parseEqs(eqsLayout))

    def __getInvData(self, data, vehDescr, capacity):
        layoutListSize = len(data)
        if layoutListSize < capacity:
            data += [ZERO_COMP_DESCR] * (capacity - layoutListSize)
        offset = self.__getOffset(vehDescr)
        return data[offset:offset + capacity]

    def __getOffset(self, vehDescr):
        offset = 0
        for eqType in vehicles.EQUIPMENT_TYPES_ORDER:
            if eqType == self._expendableType():
                break
            offset += vehDescr.type.supplySlots.getAmountForType(ITEM_TYPES.equipment, eqType)

        return offset

    @staticmethod
    def __parseEqs(eqsInvData):
        result = []
        for intCD in eqsInvData:
            result.append(abs(intCD) if intCD != ZERO_COMP_DESCR else EMPTY_ITEM)

        return result


class CrewBoosterInfluenceOnPerk(object):
    __slots__ = ('crewBooster', 'points')

    def __init__(self, crewBooster, points):
        self.crewBooster = crewBooster
        self.points = points


class _BattleBoostersCollector(_ConsumablesCollector):
    __slots__ = ()

    def collectPerkBonuses(self):
        collection = []
        for item in self._installed:
            if item and item.isCrewBooster():
                perkID, points, overcapPoints = item.getPerkBonus()
                collection.append(PerkBonusInfluenceItem(PerkBonusApplier.BOOSTER, item.intCD, perkID, points, overcapPoints))

        return collection

    def _expendableType(self):
        return EQUIPMENT_TYPES.battleBoosters

    def _guiItemType(self):
        return GUI_ITEM_TYPE.BATTLE_BOOSTER


class _BattleAbilitiesCollector(_ExpendableCollector):
    __slots__ = ()

    def setInstalled(self, *values):
        self._installed = self._equipmentClazz()(self._guiItemType(), len(values), self._proxy, False, *values)

    def setLayout(self, *values):
        self._layout = self._equipmentClazz()(self._guiItemType(), len(values), self._proxy, False, *values)

    def _equipmentClazz(self):
        return _BattleAbilitesEquipment

    def _expendableType(self):
        return EQUIPMENT_TYPES.battleAbilities

    def _guiItemType(self):
        return GUI_ITEM_TYPE.BATTLE_ABILITY

    def _parse(self, vehDescr, capacity, invData):
        empty = capacity * [EMPTY_ITEM]
        return (empty, empty)


class _ShellsEquipment(_Equipment):
    __slots__ = ()

    def __iter__(self):
        for itemData in self._storage:
            if itemData:
                yield self._createItem(itemData)

    def _createItem(self, itemData):
        intCD, count, isBoughtForAltPrice = itemData
        return self._itemsFactory.createShell(intCD, count, self._proxy, isBoughtForAltPrice)

    def _getItemData(self, item):
        return (item.intCD, item.count, item.isBoughtForAltPrice)

    def _getIntCD(self, itemData):
        return first(itemData)


class _BattleAbilitesEquipment(_ExpendableEquipment):
    __slots__ = ()

    def getIntCDs(self, default=ZERO_COMP_DESCR):
        return [ (itemData.intCD if itemData != EMPTY_ITEM else default) for itemData in self._storage ]

    def _createItem(self, itemData):
        return itemData

    def _getItemData(self, item):
        return item


class _ShellsCollector(_EquipmentCollector):
    __slots__ = ()
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def setInstalled(self, *values):
        values = self.__fixSize(list(values), self.layoutCapacity)
        super(_ShellsCollector, self).setInstalled(*values)

    def setLayout(self, *values):
        values = self.__fixSize(list(values), self.layoutCapacity)
        super(_ShellsCollector, self).setLayout(*values)

    def getShellsCount(self):
        return len(self.installed.getItems())

    def _equipmentClazz(self):
        return _ShellsEquipment

    def _itemType(self):
        return ITEM_TYPES.shell

    def _guiItemType(self):
        return GUI_ITEM_TYPE.SHELL

    def _parse(self, vehDescr, capacity, invData):
        installedItems = self.__parseInstalled(invData.get('shells', []), vehDescr, capacity)
        layoutItems = self.__parseLayout(invData.get('shellsLayout', {}), vehDescr, capacity)
        return (installedItems, layoutItems)

    def __parseInstalled(self, installed, vehDescr, capacity):
        shellsDict = {cd:count for cd, count, _ in LayoutIterator(installed)}
        installed = installed[:]
        for shot in vehDescr.gun.shots:
            cd = shot.shell.compactDescr
            if cd not in shellsDict and len(installed) < capacity * 2:
                installed.extend([cd, 0])

        result = []
        for intCD, count, isBoughtForCredits in LayoutIterator(installed):
            result.append((intCD, count, isBoughtForCredits))

        return self.__fixSize(result, capacity)

    def __parseLayout(self, shellsInvLayout, vehDescr, capacity):
        shellsLayoutKey = (vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
        if shellsLayoutKey in shellsInvLayout:
            shellsLayout = shellsInvLayout[shellsLayoutKey]
        else:
            shellsLayout = []
            gun = self.__itemsFactory.createVehicleGun(vehDescr.gun.compactDescr, descriptor=vehDescr.gun)
            if gun is not None:
                for shell in gun.defaultAmmo:
                    shellsLayout += (shell.intCD, shell.count)

        result = []
        for intCD, count, isBoughtForCredits in LayoutIterator(shellsLayout):
            result.append((intCD, count, isBoughtForCredits))

        return self.__fixSize(result, capacity)

    @staticmethod
    def __fixSize(parsed, capacity):
        size = len(parsed)
        if size < capacity:
            parsed += [EMPTY_ITEM] * (capacity - size)
        return parsed


class _OptDevicesEquipment(_Equipment):
    __slots__ = ()

    def _createItem(self, intCD):
        return self._itemsCache.items.getItemByCD(intCD)

    def _getItemData(self, item):
        return item.intCD


class _OptDevicesCollector(_EquipmentCollector):
    __slots__ = ()

    def _equipmentClazz(self):
        return _OptDevicesEquipment

    def _itemType(self):
        return ITEM_TYPES.optionalDevice

    def _guiItemType(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE

    def _parse(self, vehDescr, capacity, invData):
        result = []
        for optDevDescr in vehDescr.optionalDevices:
            result.append(optDevDescr.compactDescr if optDevDescr != EMPTY_ITEM else EMPTY_ITEM)

        return (result, result)


class VehicleEquipment(object):
    __slots__ = ('__consumables', '__battleBoosters', '__battleAbilities', '__shells', '__optDevices')

    def __init__(self, itemRequesterProxy, vehDescr, invData):
        proxy = weakref.proxy(itemRequesterProxy) if itemRequesterProxy else None
        self.__optDevices = _OptDevicesCollector(vehDescr, proxy)
        self.__shells = _ShellsCollector(vehDescr, proxy, invData)
        self.__consumables = _ConsumablesCollector(vehDescr, proxy, invData)
        self.__battleBoosters = _BattleBoostersCollector(vehDescr, proxy, invData)
        self.__battleAbilities = _BattleAbilitiesCollector(vehDescr, proxy, invData)
        return

    @property
    def optDevices(self):
        return self.__optDevices

    @property
    def shells(self):
        return self.__shells

    @property
    def consumables(self):
        return self.__consumables

    @property
    def battleBoosters(self):
        return self.__battleBoosters

    @property
    def battleAbilities(self):
        return self.__battleAbilities
