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
    """
    This is a base class for any vehicle consumable.
    It contains the core logic: checking consumable type and size of internal storage.
    In general it behaves like list object but with some restrictions.
    """
    __slots__ = ('__consumables',)

    def __init__(self, *args):
        """
        Ctor, vehicle consumables may be created from the passed arguments(fitting items), otherwise
        empty container will be created
        :param args: nothing or fitting items
        """
        if args:
            assert len(args) == self._getDefaultSize()
            self.__consumables = []
            for item in args:
                self._validateType(item)
                self.__consumables.append(item)

        else:
            self.__consumables = [EMPTY_ITEM] * self._getDefaultSize()

    def __setitem__(self, slotIdx, item):
        """
        Overrides the operator [slotIdx] = item
        :param slotIdx: integer
        :param item: FittingItem instance, the type will be checked in child classes
        """
        self._validateType(item)
        self._validateIndex(slotIdx)
        self.__consumables[slotIdx] = item

    def __getitem__(self, slotIdx):
        """
        Overrides the operator [slotIdx]
        :param slotIdx: integer
        :return: FittingItem instance
        """
        return self.__consumables[slotIdx]

    def __contains__(self, item):
        """
        Overrides 'in' operator
        :param item: FittingItem instance
        :return: boolean
        """
        return item in self.__consumables

    def __iter__(self):
        """
        Overrides iterator
        :return: generator instance
        """
        for consumable in self.__consumables:
            yield consumable

    def __len__(self):
        """
        Overrides len()
        :return: integer, the number of consumables
        """
        return len(self.__consumables)

    def __eq__(self, consumables):
        """
        Overrides == operator
        :param consumables: _VehicleConsumables instance, or list
        :return: boolean
        """
        if len(self) == len(consumables):
            for i, item in enumerate(self):
                if not item == consumables[i]:
                    return False

            return True
        return False

    def containsIntCD(self, intCD, slotIdx=None):
        """
        Checks whether an item with the provided Int compact descriptor is in __consumables list.
        Specify slotIdx to check intCD on desired position.
        :param intCD: integer, item's int compact descriptor
        :param slotIdx: integer, if specified, the provided intCD will be check only for slotIdx position
        :return: boolean
        """
        if slotIdx is None:
            installed = self.getIntCDs(default=EMPTY_ITEM)
            return intCD in installed
        else:
            return self[slotIdx] != EMPTY_ITEM and self[slotIdx].intCD == intCD

    def getIntCDs(self, default=0):
        """
        Returns the list will all int compact descriptors (by default - 0 for empty consumable)
        :param: default - pass any value corresponding to empty item's intCD
        :return: list
        """
        return map(lambda item: item.intCD if item != EMPTY_ITEM else default, self)

    def getInstalledItems(self):
        """
        Returns list of installed consumables, empty items (None) will be ignored
        :return: list
        """
        return [ item for item in self if item != EMPTY_ITEM ]

    def copy(self):
        """
        Performs deep copy.
        :return: _VehicleConsumables instance
        """
        return self.__class__(*self)

    def _validateIndex(self, idx):
        """
        Validates the index is in 0...maxConsumablesSize range
        :param idx: integer
        """
        assert idx < self._getDefaultSize(), 'Index {} exceeds the layout size!'.format(idx)

    def _getDefaultSize(self):
        """
        Child classes should override this method to specify the correct size of internal storage.
        """
        raise NotImplementedError

    def _validateType(self, item):
        """
        Child classes should override this method to specify the correct type of each consumable.
        """
        raise NotImplementedError


class RegularEquipmentConsumables(_VehicleConsumables):
    """
    Regular consumables have 3 slots, they can be changed in TechnicalMaintenance window.
    Examples: med-kit, repair-kit, coca-cola, gasoline, etc.
    """
    __slots__ = ()

    def _validateType(self, item):
        condition = item is None or item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT
        assert condition, 'The item {} is not valid equipment!'.format(item)
        return

    def _getDefaultSize(self):
        return REGULAR_EQUIPMENT_LAYOUT_SIZE


class BattleBoosterConsumables(_VehicleConsumables):
    """
    It was introduced in 9.19 version. At the moment only 1 battle booster is available for each vehicle.
    But it is possible, a few boosters will be available someday. Don't forget about it while writing UI.
    Battle booster behaves like usual consumable (applied only on one battle).
    """
    __slots__ = ()

    def _validateType(self, item):
        condition = item is None or item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER
        assert condition, 'The item {} is not valid battle booster!'.format(item)
        return

    def _getDefaultSize(self):
        return BATTLE_BOOSTER_LAYOUT_SIZE


class VehicleEquipment(object):
    """
    This is container for vehicle equipment. Equipment consists of regular consumables and battle boosters.
    Also this class parses and creates necessary items from Inventory.
    In the future Shells also should be added in this class to have all consumables in one place.
    """
    __slots__ = ('__regularConsumables', '__boosterConsumables')
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, itemRequesterProxy, eqsInvData=None):
        """
        :param itemRequesterProxy: instance of ItemsRequester
        :param eqsInvData: equipment data for the inventory, list
        """
        self.__regularConsumables = RegularEquipmentConsumables()
        self.__boosterConsumables = BattleBoosterConsumables()
        inventoryData = eqsInvData if eqsInvData else DEFAULT_EQUIPMENT_LAYOUT
        self.__parseEqs(inventoryData, itemRequesterProxy)

    @property
    def regularConsumables(self):
        """
        Med-kit, repair-kit, coca-cola, chocolate, gasoline, etc
        :return: RegularEquipmentConsumables instance
        """
        return self.__regularConsumables

    @property
    def battleBoosterConsumables(self):
        """
        aimingStabilizerBattleBooster, camouflageBattleBooster, smoothTurretBattleBooster, etc
        :return: BattleBoosterConsumables instance
        """
        return self.__boosterConsumables

    def setRegularConsumables(self, consumables):
        """
        This method sets and validates regular consumables. Usually it is used in TTC view to calculate diff.
        :param consumables: instance of RegularEquipmentConsumables
        """
        assert isinstance(consumables, RegularEquipmentConsumables)
        assert len(consumables) == REGULAR_EQUIPMENT_LAYOUT_SIZE
        self.__regularConsumables = consumables

    def setBattleBoosterConsumables(self, consumables):
        """
        This method sets and validates battle booster consumables.
        Usually it is used in TTC view to calculate diff.
        :param consumables: instance of BattleBoosterConsumables
        """
        assert isinstance(consumables, BattleBoosterConsumables)
        assert len(consumables) == BATTLE_BOOSTER_LAYOUT_SIZE
        self.__boosterConsumables = consumables

    def getConsumablesIntCDs(self, default=0):
        """
        Returns the list will all intCDs (0 for empty consumable) for each type of consumable (regular + booster).
        :param: default - pass any value corresponding to empty item's intCD
        :return: list
        """
        intCDs = self.regularConsumables.getIntCDs(default)
        intCDs.extend(self.battleBoosterConsumables.getIntCDs(default))
        return intCDs

    def __parseEqs(self, inventoryData, proxy):
        """
        Parse inventory.eqs data from server, create and fill consumable objects.
        :param inventoryData: list, the inventory data or DEFAULT_EQUIPMENT_LAYOUT
        :param proxy: instance of ItemsRequester
        """
        layoutListSize = len(inventoryData)
        assert layoutListSize <= vehicles.NUM_EQUIPMENT_SLOTS
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
        """
        This method returns a list to be passed to Server
        :return: list
        """
        raise NotImplementedError


class ShellLayoutHelper(_LayoutHelper):
    """
    Helper for Shells Layout. At the moment return the original list.
    No specific logic is required.
    """
    __slots__ = ('__shellLayout',)

    def __init__(self, vehicle, shellLayout=None):
        super(ShellLayoutHelper, self).__init__(vehicle)
        self.__shellLayout = shellLayout

    def getRawLayout(self):
        return self.__shellLayout


class EquipmentLayoutHelper(_LayoutHelper):
    """
    Helper for Equipment Layout. It contains regular equipment + battleBooster.
    It gathers missing layout info from the Inventory to collect the whole layout. The collected layout is passed
    to server in one command.
    """
    __slots__ = ('__collectedLayout',)

    def __init__(self, vehicle, eqsLayout=None, battleBoosterLayout=None):
        super(EquipmentLayoutHelper, self).__init__(vehicle)
        self.__collectedLayout = self.__collectLayout(eqsLayout, battleBoosterLayout)

    def getRawLayout(self):
        """
        The whole layout contains regular equipment + battleBooster
        :return: list to be passed to Server
        """
        return self.__collectedLayout

    def getRegularRawLayout(self):
        """
        Return a layout only for regular equipment(without battleBooster)
        :return: list in format [intCD, count, intCD, count...]
        """
        return self.__collectedLayout[:REGULAR_EQUIPMENT_LAYOUT_SIZE * LAYOUT_ITEM_SIZE]

    def getBattleBoosterRawLayout(self):
        """
        Return a layout only for regular equipment(without battleBooster)
        :return: list in format [intCD, count, intCD, count...]
        """
        return self.__collectedLayout[-BATTLE_BOOSTER_LAYOUT_SIZE * LAYOUT_ITEM_SIZE:]

    def __collectLayout(self, eqsLayout, battleBoosterLayout):
        """
        BattleBooster is a part of equipment, the method appends it to the end of equipment layout (4th slot)
        """
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
        """
        Return only booster layout from Inventory Equipment Layout
        :param vehicle: instance of gui_item.Vehicle
        :return: list in format [intCD, count]
        """
        eqsLayout = self.__getEqsLayoutFromInv(vehicle)
        if len(eqsLayout) < EQUIPMENT_LAYOUT_SIZE:
            eqs = [0] * BATTLE_BOOSTER_LAYOUT_SIZE
        else:
            eqs = eqsLayout[-BATTLE_BOOSTER_LAYOUT_SIZE:]
        return self.__expandLayout(eqs)

    def __getRegularEquipmentLayoutFromInv(self, vehicle):
        """
        Return only regular equipment layout(the first three slots, without battle booster)
        :param vehicle: instance of gui_item.Vehicle
        :return: list in format [intCD_1, count_1, intCD_2, count_2, ...]
        """
        eqsLayout = self.__getEqsLayoutFromInv(vehicle)
        if len(eqsLayout) < REGULAR_EQUIPMENT_LAYOUT_SIZE:
            eqs = [0] * REGULAR_EQUIPMENT_LAYOUT_SIZE
        else:
            eqs = eqsLayout[:REGULAR_EQUIPMENT_LAYOUT_SIZE]
        return self.__expandLayout(eqs)

    @staticmethod
    def __expandLayout(eqs):
        """
        Expand the provided layout with number for each intCD
        :param eqs: list of intCDs
        :return: list in format [intCD1, count1, intCD2, count2, etc...]
        """
        result = []
        for eq in eqs:
            result.extend((eq, 1 if eq else 0))

        return result

    def __getEqsLayoutFromInv(self, vehicle):
        """
        Return the whole equipment layout. It contains regular Equipment (first 3 slots) + 1 battle booster slot
        :param vehicle: instance of gui_item.Vehicle
        :return: list of compact descriptors [intCD_x, intCD_y, ... etc]
        """
        vehInvData = self.itemsCache.items.inventory.getVehicleData(vehicle.invID)
        return vehInvData.eqsLayout
