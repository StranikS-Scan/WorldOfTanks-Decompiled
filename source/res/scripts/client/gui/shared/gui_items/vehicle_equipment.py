# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_equipment.py
import logging
import weakref
import typing
from itertools import chain
from account_shared import LayoutIterator
from items.components.supply_slots_components import SupplySlot
from items.vehicles import VehicleDescriptor
from post_progression_common import TankSetupLayouts, MAX_LAYOUTS_NUMBER_ON_VEHICLE, GROUP_ID_BY_LAYOUT
from shared_utils import first
from helpers import dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from items import vehicles, EQUIPMENT_TYPES, ITEM_TYPES
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.utils.requesters.ItemsRequester import ItemsRequester
_logger = logging.getLogger(__name__)
ZERO_COMP_DESCR = 0
EMPTY_INVENTORY_DATA = [ZERO_COMP_DESCR]
LAYOUT_ITEM_SIZE = 2
EMPTY_ITEM = None

class _Equipment(object):
    __slots__ = ('_storage', '__guiItemType', '__capacity', '_proxy')

    def __init__(self, guiItemType, capacity, proxy, fromRawData, *args):
        self.__capacity = capacity
        self.__guiItemType = guiItemType
        self._proxy = proxy
        if args:
            if len(args) != self.getCapacity():
                _logger.warning('Length of arguments is not valid, args: %s for equipment: %s', args, self)
                args = args[:self.getCapacity()]
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

    def getItems(self, ignoreEmpty=True):
        return [ item for item in self if item != EMPTY_ITEM or not ignoreEmpty ]

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
    __slots__ = ('_installed', '_layout', '__slots', '__setupLayouts', '_proxy', '_vehDescr')

    def __init__(self, vehDescr, proxy, setupLayouts, invData=None):
        super(_EquipmentCollector, self).__init__()
        self._vehDescr = vehDescr
        self._proxy = proxy
        groupID = self.__setupGroupID()
        supplySlots = self._getSupplySlots(vehDescr)
        self.__slots = self._readSlots(supplySlots)
        capacity = self._getCapacity(vehDescr)
        self.__setupLayouts = self._equipmentSetupClazz()(groupID, setupLayouts, capacity)
        setups, items, itemsLayout = self._parse(vehDescr, capacity, invData)
        self._installed = self._equipmentClazz()(self._guiItemType(), capacity, proxy, True, *items)
        self._layout = self._equipmentClazz()(self._guiItemType(), capacity, proxy, True, *itemsLayout)
        for idx, setup in enumerate(setups):
            if self.__setupLayouts.layoutIndex == idx:
                self.__setupLayouts.addSetup(idx, self._installed)
            setupItems = self._equipmentClazz()(self._guiItemType(), capacity, proxy, True, *setup)
            self.__setupLayouts.addSetup(idx, setupItems)

    @property
    def installed(self):
        return self._installed

    def setInstalled(self, *values):
        self._installed = self._equipmentClazz()(self._guiItemType(), self.layoutCapacity, self._proxy, False, *values)

    @property
    def layout(self):
        return self._layout

    @property
    def setupLayouts(self):
        return self.__setupLayouts

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

    def _getCapacity(self, _):
        return len(self.__slots)

    def _equipmentClazz(self):
        raise NotImplementedError

    def _equipmentSetupClazz(self):
        return _EquipmentSetupLayout

    def _itemType(self):
        raise NotImplementedError

    def _layoutType(self):
        pass

    def _guiItemType(self):
        raise NotImplementedError

    def _parse(self, vehDescr, capacity, invData):
        raise NotImplementedError

    def _readSlots(self, supplySlots):
        return [ slot for slot in supplySlots if slot.itemType == self._itemType() ]

    def __setupGroupID(self):
        layoutType = self._layoutType()
        return GROUP_ID_BY_LAYOUT.get(layoutType, None)

    @staticmethod
    def _getSupplySlots(vehDescr):
        slotIDs = vehDescr.type.supplySlots.slotIDs
        slotDescrs = vehicles.g_cache.supplySlots().slotDescrs
        return [ slotDescrs[slotID] for slotID in slotIDs ]


class _ExpendableEquipment(_Equipment):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __slots__ = ()

    def _createItem(self, intCD):
        return self.__itemsFactory.createEquipment(intCD, self._proxy)

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

    def _layoutType(self):
        return TankSetupLayouts.EQUIPMENT

    def _invType(self):
        pass

    def _parse(self, vehDescr, capacity, invData):
        setups = []
        installedItems = None
        resultLayoutItems = None
        eqsLayouts = invData.get(self._layoutType(), [[]])
        eqsLayoutsSize = len(eqsLayouts)
        for layoutIdx in range(self.setupLayouts.capacity):
            if eqsLayoutsSize <= layoutIdx < self.setupLayouts.capacity:
                eqsLayout = []
            else:
                eqsLayout = eqsLayouts[layoutIdx]
            eqsLayout = self.__getInvData(eqsLayout, capacity)
            eqs = self.__getInvData(invData.get(self._invType(), []), capacity, eqsLayout)
            items = self.__parseEqs(eqs)
            layoutItems = self.__parseEqs(eqsLayout)
            if layoutIdx == self.setupLayouts.layoutIndex:
                installedItems = items
                resultLayoutItems = layoutItems
            setups.append(items)

        return (setups, installedItems, resultLayoutItems)

    def __getInvData(self, data, capacity, layout=None):
        layoutListSize = len(data)
        if layoutListSize < capacity:
            data += [ZERO_COMP_DESCR] * (capacity - layoutListSize)
        if layout is not None:
            return [ (intCD if intCD and intCD in data else ZERO_COMP_DESCR) for intCD in layout ]
        else:
            return data

    @staticmethod
    def __parseEqs(eqsInvData):
        result = []
        for intCD in eqsInvData:
            result.append(abs(intCD) if intCD != ZERO_COMP_DESCR else EMPTY_ITEM)

        return result


class _BattleBoostersCollector(_ConsumablesCollector):
    __slots__ = ()

    def _expendableType(self):
        return EQUIPMENT_TYPES.battleBoosters

    def _guiItemType(self):
        return GUI_ITEM_TYPE.BATTLE_BOOSTER

    def _layoutType(self):
        return TankSetupLayouts.BATTLE_BOOSTERS

    def _invType(self):
        pass


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
        setups = self.setupLayouts.capacity * [empty]
        return (setups, empty, empty)

    @staticmethod
    def _getSupplySlots(vehDescr):
        return vehicles.g_cache.supplySlots().slotDescrs.values()


class _ShellsEquipment(_Equipment):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __slots__ = ()

    def __iter__(self):
        for itemData in self._storage:
            if itemData:
                yield self._createItem(itemData)

    def _createItem(self, itemData):
        intCD, count, isBoughtForAltPrice = itemData
        return self.__itemsFactory.createShell(intCD, count, self._proxy, isBoughtForAltPrice)

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
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __slots__ = ()

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

    def _equipmentSetupClazz(self):
        return _ShellsSetupLayout

    def _itemType(self):
        return ITEM_TYPES.shell

    def _layoutType(self):
        return TankSetupLayouts.SHELLS

    def _guiItemType(self):
        return GUI_ITEM_TYPE.SHELL

    def _parse(self, vehDescr, capacity, invData):
        setups = []
        resultInstalledItems = None
        resultLayoutItems = None
        for layoutIdx in range(self.setupLayouts.capacity):
            layoutItems, shellsLayout = self.__parseLayout(invData.get(self._layoutType(), {}), vehDescr, capacity, layoutIdx)
            installedItems = self.__parseInstalled(invData.get('shells', []), shellsLayout, vehDescr, capacity)
            setups.append(installedItems)
            if layoutIdx == self.setupLayouts.layoutIndex:
                resultInstalledItems = installedItems
                resultLayoutItems = layoutItems

        return (setups, resultInstalledItems, resultLayoutItems)

    def __parseInstalled(self, installed, shellsLayout, vehDescr, capacity):
        installedDict = {cd:count for cd, count, _ in LayoutIterator(installed)}
        layoutDict = {cd:count for cd, count, _ in LayoutIterator(shellsLayout)}
        missed = []
        shellsLayout = shellsLayout[:]
        for shot in vehDescr.gun.shots:
            cd = shot.shell.compactDescr
            if cd in layoutDict:
                count = 0
                if cd in installedDict:
                    count = min(installedDict.get(cd, 0), layoutDict.get(cd, 0))
                idx = shellsLayout.index(cd) + 1
                shellsLayout[idx] = count
            missed.append(cd)

        for cd in missed:
            shellsLayout.extend([cd, 0])

        result = []
        for intCD, count, isBoughtForCredits in LayoutIterator(shellsLayout):
            result.append((intCD, count, isBoughtForCredits))

        return self.__fixSize(result, capacity)

    def __parseLayout(self, shellsInvLayout, vehDescr, capacity, layoutIdx):
        shellsLayoutKey = (vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
        if shellsLayoutKey in shellsInvLayout:
            shellsLayouts = shellsInvLayout[shellsLayoutKey]
            shellsLayoutsSize = len(shellsLayouts)
            if shellsLayoutsSize <= layoutIdx < self.setupLayouts.capacity or not shellsLayouts[layoutIdx]:
                shellsLayout = self.__getDefaultShellsLayout(vehDescr, defaultCount=0)
            else:
                shellsLayout = shellsLayouts[layoutIdx]
        else:
            shellsLayout = self.__getDefaultShellsLayout(vehDescr)
        result = []
        for intCD, count, isBoughtForCredits in LayoutIterator(shellsLayout):
            result.append((intCD, count, isBoughtForCredits))

        return (self.__fixSize(result, capacity), shellsLayout)

    def __getDefaultShellsLayout(self, vehDescr, defaultCount=None):
        shellsLayout = []
        gun = self.__itemsFactory.createVehicleGun(vehDescr.gun.compactDescr, descriptor=vehDescr.gun)
        if gun is not None:
            for shell in gun.defaultAmmo:
                count = defaultCount if defaultCount is not None else shell.count
                shellsLayout += (shell.intCD, count)

        return shellsLayout

    @staticmethod
    def __fixSize(parsed, capacity):
        size = len(parsed)
        if size < capacity:
            parsed += [EMPTY_ITEM] * (capacity - size)
        return parsed


class _OptDevicesEquipment(_Equipment):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __slots__ = ()

    def _createItem(self, intCD):
        return self.__itemsFactory.createOptionalDevice(intCD, self._proxy)

    def _getItemData(self, item):
        return item.intCD


OptDeviceSlotData = typing.NamedTuple('OptDeviceSlotInfo', (('item', SupplySlot), ('isDynamic', bool)))

class _OptDevicesCollector(_EquipmentCollector):
    __slots__ = ('_dynSlotTypeIdx', '_dynSlotType', '_dynSlotTypeOptions')

    def __init__(self, vehDescr, proxy, setupLayouts, invData=None):
        super(_OptDevicesCollector, self).__init__(vehDescr, proxy, setupLayouts, invData)
        slotDescrs = vehicles.g_cache.supplySlots().slotDescrs
        self._dynSlotTypeIdx = self.__getDynSlotTypeIdx()
        self._dynSlotType = slotDescrs[vehDescr.customRoleSlotTypeId] if vehDescr.customRoleSlotTypeId > 0 else None
        self._dynSlotTypeOptions = [ slotDescrs[opt] for opt in vehDescr.type.customRoleSlotOptions ]
        return

    @property
    def dynSlotTypeIdx(self):
        return self._dynSlotTypeIdx

    @property
    def dynSlotType(self):
        return self._dynSlotType

    @property
    def dynSlotTypeOptions(self):
        return self._dynSlotTypeOptions

    @dynSlotType.setter
    def dynSlotType(self, value):
        customRoleSlotTypeId = value.slotID if value else 0
        self._vehDescr.installCustomRoleSlot(customRoleSlotTypeId)
        self._dynSlotType = value

    def getSlot(self, slotIdx):
        if slotIdx < 0 or slotIdx >= len(self.slots):
            raise SoftException('Wrong slotIdx=[%r]' % slotIdx)
        return OptDeviceSlotData(self._dynSlotType, True) if self._dynSlotType and self.isSlotHasDynamicSpecialization(slotIdx) else OptDeviceSlotData(self.slots[slotIdx], False)

    def isSlotHasDynamicSpecialization(self, slotIdx):
        return self._dynSlotTypeIdx == slotIdx

    def _equipmentClazz(self):
        return _OptDevicesEquipment

    def _itemType(self):
        return ITEM_TYPES.optionalDevice

    def _layoutType(self):
        return TankSetupLayouts.OPTIONAL_DEVICES

    def _guiItemType(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE

    def _parse(self, vehDescr, capacity, invData):
        if not invData:
            optDevices = []
            for optDevDescr in vehDescr.optionalDevices:
                optDevices.append(optDevDescr.compactDescr if optDevDescr != EMPTY_ITEM else ZERO_COMP_DESCR)

            devicesLayout = [optDevices]
        else:
            devicesLayout = invData.get(self._layoutType(), [[]])
        eqsLayoutsSize = len(devicesLayout)
        result = None
        setups = []
        for layoutIdx in range(self.setupLayouts.capacity):
            if eqsLayoutsSize <= layoutIdx < self.setupLayouts.capacity:
                dvsLayout = []
            else:
                dvsLayout = devicesLayout[layoutIdx]
            items = [ (item if item != ZERO_COMP_DESCR else EMPTY_ITEM) for item in dvsLayout ]
            layoutSize = len(dvsLayout)
            if layoutSize < capacity:
                items += [EMPTY_ITEM] * (capacity - layoutSize)
            setups.append(items)
            if layoutIdx == self.setupLayouts.layoutIndex:
                result = items

        return (setups, result, result)

    def __getDynSlotTypeIdx(self):
        for idx, slot in enumerate(self.slots):
            if not slot.categories:
                return idx


class _EquipmentsSetupGroups(object):
    __slots__ = ('_groups',)

    def __init__(self, invData):
        super(_EquipmentsSetupGroups, self).__init__()
        self._groups = self._parse(invData)

    def __eq__(self, setupGroups):
        if len(self._groups.keys()) != len(setupGroups.groups.keys()):
            return False
        for groupID, layoutIdx in setupGroups.groups.items():
            if self.getLayoutIndex(groupID) != layoutIdx:
                return False

        return True

    def __ne__(self, setupGroups):
        return not self.__eq__(setupGroups)

    @property
    def groups(self):
        return self._groups

    def setGroups(self, value):
        self._groups = value

    def getLayoutIndex(self, groupID):
        return self._groups.get(groupID, 0)

    def getGroupCapacity(self, groupID):
        return MAX_LAYOUTS_NUMBER_ON_VEHICLE.get(groupID, 0)

    def getNextLayoutIndex(self, groupID):
        index = self.getLayoutIndex(groupID) + 1
        return index if index < self.getGroupCapacity(groupID) else 0

    def _parse(self, invData):
        return invData.get('layoutIndexes', {}).copy()


class _EquipmentSetupLayout(object):
    __slots__ = ('__groupID', '__layoutIdx', '__capacity', '__setups', '__slotsCapacity')

    def __init__(self, groupID, setupLayouts, slotsCapacity):
        super(_EquipmentSetupLayout, self).__init__()
        self.__groupID = groupID
        self.__capacity = setupLayouts.getGroupCapacity(groupID)
        self.__layoutIdx = setupLayouts.getLayoutIndex(groupID)
        self.__slotsCapacity = slotsCapacity
        self.__setups = {}

    def __iter__(self):
        for item in chain.from_iterable(self.__setups.itervalues()):
            if item:
                yield item

    def __contains__(self, item):
        return self.containsIntCD(item.intCD)

    @property
    def groupID(self):
        return self.__groupID

    @property
    def layoutIndex(self):
        return self.__layoutIdx

    def setLayoutIndex(self, value):
        self.__layoutIdx = value

    @property
    def capacity(self):
        return self.__capacity

    @property
    def setups(self):
        return self.__setups

    def addSetup(self, idx, setup):
        self.__setups[idx] = setup

    def setSetups(self, value):
        self.__setups = value

    def setupByIndex(self, idx):
        return self.__setups.get(idx, None)

    def isInSetup(self, item):
        for _, setup in self.__setups.iteritems():
            if item in setup:
                return True

        return False

    def isInOtherLayout(self, item):
        return bool([ idx for idx, setup in self.__setups.iteritems() if item in setup and idx != self.__layoutIdx ])

    def getIntCDs(self, setupIdx=None, default=ZERO_COMP_DESCR):
        if setupIdx is None:
            return [ (self._getIntCD(itemData) if itemData != EMPTY_ITEM else default) for itemData in chain.from_iterable(self.__setups.itervalues()) ]
        else:
            setup = self.setupByIndex(setupIdx)
            if setup is not None:
                return [ (self._getIntCD(itemData) if itemData != EMPTY_ITEM else default) for itemData in setup ]
            return [default] * self.__slotsCapacity

    def containsIntCD(self, intCD, setupIdx=None, slotIdx=None):
        if setupIdx is None:
            installed = self.getIntCDs(default=EMPTY_ITEM)
            return intCD in installed
        elif slotIdx is None:
            installed = self.getIntCDs(setupIdx=setupIdx, default=EMPTY_ITEM)
            return intCD in installed
        elif slotIdx >= self.__layoutCapacity(setupIdx):
            return False
        else:
            item = self.setupByIndex(setupIdx)[slotIdx]
            return item != EMPTY_ITEM and self._getIntCD(item) == intCD

    def hasAlternativeItems(self, setupIdx):
        for idx, setup in self.__setups.iteritems():
            if idx != setupIdx:
                for itemData in setup:
                    if itemData != EMPTY_ITEM:
                        return True

        return False

    def getUniqueItems(self):
        equipments = []
        intCDs = set()
        for setup in self.__setups.values():
            for item in setup.getItems():
                if item.intCD not in intCDs:
                    intCDs.add(item.intCD)
                    equipments.append(item)

        return equipments

    def _getIntCD(self, item):
        return item.intCD

    def __layoutCapacity(self, layoutIdx):
        return min(self.__slotsCapacity, len(self.setupByIndex(layoutIdx)))


class _ShellsSetupLayout(_EquipmentSetupLayout):
    __slots__ = ()

    def ammoLoaded(self, intCD):
        ammo = 0
        for s in chain.from_iterable(self.setups.itervalues()):
            if s and self._getIntCD(s) == intCD:
                ammo = max(ammo, s.count)

        return ammo

    def ammoLoadedInOtherSetups(self, intCD):
        ammo = 0
        for idx, setup in self.setups.iteritems():
            if idx != self.layoutIndex:
                for s in setup:
                    if s and self._getIntCD(s) == intCD:
                        ammo = max(ammo, s.count)

        return ammo

    def isAmmoNotFull(self, minAmmo=0):
        for idx, setup in self.setups.iteritems():
            count = sum(((s.count if s != EMPTY_ITEM else 0) for s in setup))
            if count < minAmmo:
                return (True, idx)

        return (False, None)

    def isAmmoFull(self, setupIdx=None, minAmmo=0):
        if setupIdx is None:
            return sum(((s.count if s != EMPTY_ITEM else 0) for s in chain.from_iterable(self.setups.itervalues()))) >= minAmmo
        else:
            setup = self.setupByIndex(setupIdx)
            return sum(((s.count if s != EMPTY_ITEM else 0) for s in setup)) >= minAmmo if setup is not None else True

    def hasAlternativeItems(self, setupIdx):
        return self.__hasAlternativeAmmo(setupIdx)

    def getUniqueItems(self):
        shells = []
        intCDs = set()
        for setup in self.setups.values():
            for shell in setup.getItems():
                if shell.intCD not in intCDs:
                    intCDs.add(shell.intCD)
                    shells.append(shell)
                for idx, item in enumerate(shells):
                    if shell.intCD == item.intCD:
                        if shell.count > item.count:
                            shells[idx] = shell
                        break

        return shells

    def __hasAlternativeAmmo(self, setupIdx):
        count = 0
        for idx, setup in self.setups.iteritems():
            if idx != setupIdx:
                count += sum(((s.count if s != EMPTY_ITEM else 0) for s in setup))

        return count > 0


class VehicleEquipment(object):
    __slots__ = ('__consumables', '__battleBoosters', '__battleAbilities', '__shells', '__optDevices', '__setupLayouts')

    def __init__(self, itemRequesterProxy, vehDescr, invData):
        proxy = weakref.proxy(itemRequesterProxy) if itemRequesterProxy else None
        self.__setupLayouts = setupLayouts = _EquipmentsSetupGroups(invData)
        self.__optDevices = _OptDevicesCollector(vehDescr, proxy, setupLayouts, invData)
        self.__shells = _ShellsCollector(vehDescr, proxy, setupLayouts, invData)
        self.__consumables = _ConsumablesCollector(vehDescr, proxy, setupLayouts, invData)
        self.__battleBoosters = _BattleBoostersCollector(vehDescr, proxy, setupLayouts, invData)
        self.__battleAbilities = _BattleAbilitiesCollector(vehDescr, proxy, setupLayouts, invData)
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

    @property
    def setupLayouts(self):
        return self.__setupLayouts
