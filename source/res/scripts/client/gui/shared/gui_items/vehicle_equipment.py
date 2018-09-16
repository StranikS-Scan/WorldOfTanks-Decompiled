# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_equipment.py
from items import vehicles, EQUIPMENT_TYPES
from helpers import dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
BATTLE_BOOSTER_SLOT_IDX = vehicles.NUM_EQUIPMENT_SLOTS_BY_TYPE[EQUIPMENT_TYPES.regular]
EQUIPMENT_LAYOUT_SIZE = vehicles.NUM_EQUIPMENT_SLOTS
DEFAULT_EQUIPMENT_LAYOUT = [0] * EQUIPMENT_LAYOUT_SIZE
REGULAR_EQUIPMENT_LAYOUT_SIZE = vehicles.NUM_EQUIPMENT_SLOTS_BY_TYPE[EQUIPMENT_TYPES.regular]
BATTLE_BOOSTER_LAYOUT_SIZE = vehicles.NUM_EQUIPMENT_SLOTS_BY_TYPE[EQUIPMENT_TYPES.battleBoosters]
LAYOUT_ITEM_SIZE = 2
EMPTY_ITEM = None

class _VehicleConsumables(object):
    __slots__ = ('__consumables',)

    def __init__(self, *args):
        if args:
            if len(args) != self._getDefaultSize():
                raise UserWarning('Length of arguments is not valid')
            self.__consumables = []
            for item in args:
                self._validateType(item)
                self.__consumables.append(item)

        else:
            self.__consumables = [EMPTY_ITEM] * self._getDefaultSize()

    def __setitem__(self, slotIdx, item):
        self._validateType(item)
        self._validateIndex(slotIdx)
        self.__consumables[slotIdx] = item

    def __getitem__(self, slotIdx):
        return self.__consumables[slotIdx]

    def __contains__(self, item):
        return item in self.__consumables

    def __iter__(self):
        for consumable in self.__consumables:
            yield consumable

    def __len__(self):
        return len(self.__consumables)

    def __eq__(self, consumables):
        if len(self) == len(consumables):
            for i, item in enumerate(self):
                if not item == consumables[i]:
                    return False

            return True
        return False

    def containsIntCD(self, intCD, slotIdx=None):
        if slotIdx is None:
            installed = self.getIntCDs(default=EMPTY_ITEM)
            return intCD in installed
        else:
            return self[slotIdx] != EMPTY_ITEM and self[slotIdx].intCD == intCD

    def getIntCDs(self, default=0):
        return [ (item.intCD if item != EMPTY_ITEM else default) for item in self ]

    def getInstalledItems(self):
        return [ item for item in self if item != EMPTY_ITEM ]

    def copy(self):
        return self.__class__(*self)

    def _validateIndex(self, idx):
        if idx >= self._getDefaultSize():
            raise UserWarning('Index {} exceeds the layout size!'.format(idx))

    def _getDefaultSize(self):
        raise NotImplementedError

    def _validateType(self, item):
        raise NotImplementedError


class RegularEquipmentConsumables(_VehicleConsumables):
    __slots__ = ()

    def _validateType(self, item):
        if item is not None and item.itemTypeID != GUI_ITEM_TYPE.EQUIPMENT:
            raise UserWarning('The item {} is not valid equipment!'.format(item))
        return

    def _getDefaultSize(self):
        return REGULAR_EQUIPMENT_LAYOUT_SIZE


class BattleBoosterConsumables(_VehicleConsumables):
    __slots__ = ()

    def _validateType(self, item):
        if item is not None and item.itemTypeID != GUI_ITEM_TYPE.BATTLE_BOOSTER:
            raise UserWarning('The item {} is not valid battle booster!'.format(item))
        return

    def _getDefaultSize(self):
        return BATTLE_BOOSTER_LAYOUT_SIZE


class VehicleEquipment(object):
    __slots__ = ('__regularConsumables', '__boosterConsumables')
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, itemRequesterProxy, eqsInvData=None):
        self.__regularConsumables = RegularEquipmentConsumables()
        self.__boosterConsumables = BattleBoosterConsumables()
        inventoryData = eqsInvData if eqsInvData else DEFAULT_EQUIPMENT_LAYOUT
        self.__parseEqs(inventoryData, itemRequesterProxy)

    @property
    def regularConsumables(self):
        return self.__regularConsumables

    @property
    def battleBoosterConsumables(self):
        return self.__boosterConsumables

    def setRegularConsumables(self, consumables):
        self.__regularConsumables = consumables

    def setBattleBoosterConsumables(self, consumables):
        self.__boosterConsumables = consumables

    def getConsumablesIntCDs(self, default=0):
        intCDs = self.regularConsumables.getIntCDs(default)
        intCDs.extend(self.battleBoosterConsumables.getIntCDs(default))
        return intCDs

    def __parseEqs(self, inventoryData, proxy):
        layoutListSize = len(inventoryData)
        if layoutListSize > vehicles.NUM_EQUIPMENT_SLOTS:
            raise UserWarning('Size of layout is invalid')
        if layoutListSize < REGULAR_EQUIPMENT_LAYOUT_SIZE:
            inventoryData += [0] * (REGULAR_EQUIPMENT_LAYOUT_SIZE - layoutListSize)
            layoutListSize = REGULAR_EQUIPMENT_LAYOUT_SIZE
        for i in range(layoutListSize):
            intCD = inventoryData[i]
            item = self.itemsFactory.createEquipment(abs(intCD), proxy, intCD < 0) if intCD != 0 else None
            if i < BATTLE_BOOSTER_SLOT_IDX:
                self.__regularConsumables[i] = item
            self.__boosterConsumables[i - BATTLE_BOOSTER_SLOT_IDX] = item

        return


class _LayoutHelper(object):
    __slots__ = ('_vehicle',)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle):
        self._vehicle = vehicle

    def getRawLayout(self):
        raise NotImplementedError


class ShellLayoutHelper(_LayoutHelper):
    __slots__ = ('__shellLayout',)

    def __init__(self, vehicle, shellLayout=None):
        super(ShellLayoutHelper, self).__init__(vehicle)
        self.__shellLayout = shellLayout

    def getRawLayout(self):
        return self.__shellLayout


class EquipmentLayoutHelper(_LayoutHelper):
    __slots__ = ('__collectedLayout',)

    def __init__(self, vehicle, eqsLayout=None, battleBoosterLayout=None):
        super(EquipmentLayoutHelper, self).__init__(vehicle)
        self.__collectedLayout = self.__collectLayout(eqsLayout, battleBoosterLayout)

    def getRawLayout(self):
        return self.__collectedLayout

    def getRegularRawLayout(self):
        return self.__collectedLayout[:REGULAR_EQUIPMENT_LAYOUT_SIZE * LAYOUT_ITEM_SIZE]

    def getBattleBoosterRawLayout(self):
        return self.__collectedLayout[-BATTLE_BOOSTER_LAYOUT_SIZE * LAYOUT_ITEM_SIZE:]

    def __collectLayout(self, eqsLayout, battleBoosterLayout):
        if battleBoosterLayout is not None and eqsLayout is not None:
            result = eqsLayout[:]
            result.extend(battleBoosterLayout)
        elif eqsLayout is not None:
            result = eqsLayout[:]
            result.extend(self.__getBattleBoosterLayoutFromInv(self._vehicle))
        elif battleBoosterLayout is not None:
            result = self.__getRegularEquipmentLayoutFromInv(self._vehicle)
            result.extend(battleBoosterLayout)
        else:
            result = self.__expandLayout(self.__getEqsLayoutFromInv(self._vehicle))
        return result

    def __getBattleBoosterLayoutFromInv(self, vehicle):
        eqsLayout = self.__getEqsLayoutFromInv(vehicle)
        if len(eqsLayout) < EQUIPMENT_LAYOUT_SIZE:
            eqs = [0] * BATTLE_BOOSTER_LAYOUT_SIZE
        else:
            eqs = eqsLayout[-BATTLE_BOOSTER_LAYOUT_SIZE:]
        return self.__expandLayout(eqs)

    def __getRegularEquipmentLayoutFromInv(self, vehicle):
        eqsLayout = self.__getEqsLayoutFromInv(vehicle)
        if len(eqsLayout) < REGULAR_EQUIPMENT_LAYOUT_SIZE:
            eqs = [0] * REGULAR_EQUIPMENT_LAYOUT_SIZE
        else:
            eqs = eqsLayout[:REGULAR_EQUIPMENT_LAYOUT_SIZE]
        return self.__expandLayout(eqs)

    @staticmethod
    def __expandLayout(eqs):
        result = []
        for eq in eqs:
            result.extend((eq, 1 if eq else 0))

        return result

    def __getEqsLayoutFromInv(self, vehicle):
        vehInvData = self.itemsCache.items.inventory.getVehicleData(vehicle.invID)
        return vehInvData.eqsLayout
