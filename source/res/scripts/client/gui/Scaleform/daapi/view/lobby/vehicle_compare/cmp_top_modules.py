# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_top_modules.py
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_COMMON_CRITERIA = REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.HIDDEN

class _BaseModuleComparator(object):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_items', '_vehicle')

    def __init__(self, items, vehicle):
        super(_BaseModuleComparator, self).__init__()
        self._items = items
        self._vehicle = vehicle

    def clear(self):
        """Clear items"""
        self._items = None
        return

    def maxLvl(self, excludes=None):
        """Return module with maximum level
        :param excludes: module for exclude from search
        :return: True, module with max lvl for tank or False, None
        """

        def __key(item):
            return item.level

        items = [ x for x in self._items.values() if x not in excludes ]
        if not items:
            return (False, None)
        elif len(items) == 1:
            return (True, self._items.values()[0])
        else:
            sortedItems = sorted(items, key=__key)
            return (False, sortedItems[-1]) if sortedItems[-1].level == sortedItems[-2].level else (True, sortedItems[-1])

    def maxResearchCost(self, excludes=None):
        """Return module with maximum research points cost
        :param excludes: modules for exclude from search
        :return: True, module with max research cost or (False, None)
        """
        res = []
        for intCD, module in self._items.items():
            if excludes and module in excludes:
                continue
            unlockPrices = g_techTreeDP.getUnlockPrices(intCD)
            if unlockPrices:
                vehIntCD = self._vehicle.intCD
                if vehIntCD in unlockPrices:
                    res.append((unlockPrices[vehIntCD], module))

        if not res:
            return (False, None)
        else:
            res = sorted(res)
            return (True, res[-1][1])

    def mostValuableParam(self, excludes=None):
        """Return module with max valuable param (damage for gun, distance for radio, etc)
        :param excludes: modules for exclude from search
        :return: True, module with max valuable param or (False, None)
        """
        pass

    def _getValuableParam(self, paramName, excludes=None):
        res = []
        for intCD, module in self._items.items():
            if excludes and module in excludes:
                continue
            maxLoad = module.descriptor[paramName]
            res.append((maxLoad, module))

        if len(res) == 0:
            return (False, None)
        else:
            res = sorted(res)
            return (True, res[-1][1])


class TopModulesChecker(object):
    __slots__ = ('_comparators', '_requestCriteria', '__vehicle')

    def __init__(self, vehicle):
        super(TopModulesChecker, self).__init__()
        self.__vehicle = vehicle
        self._requestCriteria = _COMMON_CRITERIA | REQ_CRITERIA.VEHICLE.SUITABLE([self.__vehicle])
        self._comparators = [ChassisComparator(self._requestCriteria, self.__vehicle),
         TurretComparator(self._requestCriteria, self.__vehicle),
         GunComparator(self._requestCriteria, self.__vehicle),
         EngineComparator(self._requestCriteria, self.__vehicle),
         RadioComparator(self._requestCriteria, self.__vehicle)]
        g_techTreeDP.load()

    def process(self):
        """Check module for lvl, research cost, most valuable param
        :return: top module for vehicle
        """
        modules = []
        for comparator in self._comparators:
            for functor in (comparator.maxLvl, comparator.maxResearchCost, comparator.mostValuableParam):
                fit, module = self.__check(functor)
                if fit:
                    modules.append(module)
                    break

        return modules

    def clear(self):
        """Clear items in comparators"""
        for comparator in self._comparators:
            comparator.clear()

    def __check(self, functor):
        excludes = []
        assert callable(functor)
        while True:
            found, module = functor(excludes)
            if found:
                if module.mayInstall(self.__vehicle):
                    return (True, module)
                excludes.append(module)
            return (False, None)

        return None


class ChassisComparator(_BaseModuleComparator):

    def __init__(self, criteria, vehicle):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CHASSIS, criteria)
        super(ChassisComparator, self).__init__(items, vehicle)

    def mostValuableParam(self, excludes=None):
        return self._getValuableParam('maxLoad', excludes)


class TurretComparator(_BaseModuleComparator):

    def __init__(self, criteria, vehicle):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.TURRET, criteria)
        super(TurretComparator, self).__init__(items, vehicle)

    def mostValuableParam(self, excludes=None):
        return self._getValuableParam('primaryArmor', excludes)


class GunComparator(_BaseModuleComparator):
    __slots__ = ('__vehicle',)

    def __init__(self, criteria, vehicle):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.GUN, criteria)
        super(GunComparator, self).__init__(items, vehicle)

    def mostValuableParam(self, excludes=None):
        res = []
        for intCD, module in self._items.items():
            if excludes and module in excludes:
                continue
            gp = params.GunParams(module.descriptor, self._vehicle.descriptor)
            if gp:
                paramsDict = gp.getParamsDict()
                avgDamage = paramsDict.get('avgDamagePerMinute', 0.0)
                res.append((avgDamage, module))

        if len(res) == 0:
            return (False, None)
        else:
            res = sorted(res)
            return (True, res[-1][1])


class EngineComparator(_BaseModuleComparator):

    def __init__(self, criteria, vehicle):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.ENGINE, criteria)
        super(EngineComparator, self).__init__(items, vehicle)

    def mostValuableParam(self, excludes=None):
        return self._getValuableParam('power', excludes=excludes)


class RadioComparator(_BaseModuleComparator):

    def __init__(self, criteria, vehicle):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.RADIO, criteria)
        super(RadioComparator, self).__init__(items, vehicle)

    def mostValuableParam(self, excludes=None):
        return self._getValuableParam('distance', excludes=excludes)
