# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/sort_keys.py
from gui.shared.gui_items import Vehicle
from gui.shared.sort_key import SortKey

class AchievementSortKey(SortKey):
    __slots__ = ('achievement',)

    def __init__(self, achievement):
        super(AchievementSortKey, self).__init__()
        self.achievement = achievement

    def _cmp(self, other):
        x = self.achievement[0]
        y = other.achievement[0]
        result = cmp(y.hasRibbon(), x.hasRibbon())
        if result:
            return result
        result = cmp(y.getUserName(), x.getUserName())
        return result if result else None


class _VehicleSortKey(SortKey):
    __slots__ = ('info',)

    def __init__(self, vehicleInfo):
        super(_VehicleSortKey, self).__init__()
        self.info = vehicleInfo

    def _cmp(self, other):
        left = self.info.vehicle
        right = other.info.vehicle
        if left is not None:
            level = left.level
            classOrder = self.info.getOrderByClass()
            shortName = left.shortUserName
        else:
            level = -1
            classOrder = Vehicle.UNKNOWN_VEHICLE_CLASS_ORDER
            shortName = ''
        if right is not None:
            otherLevel = right.level
            otherClassOrder = other.info.getOrderByClass()
            otherShortName = right.shortUserName
        else:
            otherLevel = -1
            otherClassOrder = Vehicle.UNKNOWN_VEHICLE_CLASS_ORDER
            otherShortName = ''
        result = cmp(otherLevel, level)
        if result:
            return result
        else:
            result = cmp(classOrder, otherClassOrder)
            if result:
                return result
            result = cmp(shortName, otherShortName)
            return result if result else None


class VehicleInfoSortKey(_VehicleSortKey):
    __slots__ = ()

    def _cmp(self, other):
        result = super(VehicleInfoSortKey, self)._cmp(other)
        return result if result else cmp(self.info.player.name, other.info.player.name)


class TeamItemSortKey(_VehicleSortKey):
    __slots__ = ()

    def _cmp(self, other):
        result = super(TeamItemSortKey, self)._cmp(other)
        return -result if result else cmp(self.info.player.name, other.info.player.name)


class VehicleXpSortKey(_VehicleSortKey):
    __slots__ = ()

    def _cmp(self, other):
        return cmp(other.info.xp, self.info.xp)


class RankedVehicleXpSortKey(_VehicleSortKey):
    __slots__ = ()

    def _cmp(self, other):
        return cmp(other.info.xp - other.info.xpPenalty, self.info.xp - self.info.xpPenalty)
