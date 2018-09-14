# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_layout.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items import EQUIPMENT_LAYOUT_SIZE, REGULAR_EQUIPMENT_LAYOUT_SIZE, BATTLE_BOOSTER_LAYOUT_SIZE, LAYOUT_ITEM_SIZE

class _BaseVehicleLayout(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle):
        self._vehicle = vehicle

    def getRawLayout(self):
        """
        This method returns a list to be passed to Server
        :return: list
        """
        raise NotImplementedError


class ShellVehicleLayout(_BaseVehicleLayout):
    """
    Layout for Shells. At the moment return the original list.
    No specific logic is required.
    """

    def __init__(self, vehicle, shellLayout=None):
        super(ShellVehicleLayout, self).__init__(vehicle)
        self.__shellLayout = shellLayout

    def getRawLayout(self):
        return self.__shellLayout


class EquipmentVehicleLayout(_BaseVehicleLayout):
    """
    Layout for equipment. It contains regular equipment + battleBooster.
    It gathers missing layout info from the Inventory to collect the whole layout.
    """

    def __init__(self, vehicle, eqsLayout=None, battleBoosterLayout=None):
        super(EquipmentVehicleLayout, self).__init__(vehicle)
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
