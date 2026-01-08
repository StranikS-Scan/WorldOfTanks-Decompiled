# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/base_params.py
from collections import defaultdict
import inspect
from future.utils import iteritems, itervalues
from gui import GUI_SETTINGS
from gui.shared.items_parameters.functions import getInstalledModuleVehicle, formatCompatibles
from gui.shared.items_parameters.params_cache import g_paramsCache

class ParameterBase(object):

    def __init__(self, itemDescr, vehicleDescr=None):
        self._itemDescr = itemDescr
        self._vehicleDescr = vehicleDescr
        self.__preCachedInfo = None
        self.__rawParams = None
        return

    def getParamsDict(self):
        return ParamsDictProxy(self)

    def getAllDataDict(self):
        params = self.getParamsDict() if GUI_SETTINGS.technicalInfo else {}
        return {'parameters': params,
         'compatible': self._getCompatible()}

    def _getPrecachedInfo(self):
        if self.__preCachedInfo is None:
            self.__preCachedInfo = g_paramsCache.getPrecachedParameters(self._itemDescr.compactDescr)
        return self.__preCachedInfo

    def _getRawParams(self):
        if self.__rawParams is None:
            self.__rawParams = self._extractRawParams()
        return self.__rawParams

    def _extractRawParams(self):
        return self._getPrecachedInfo().params

    def _getCompatible(self):
        return tuple()


class CompatibleParams(ParameterBase):

    @property
    def compatibles(self):
        return g_paramsCache.getComponentVehiclesNames(self._itemDescr.compactDescr)

    def _getCompatible(self):
        curVehicle = getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        return (('vehicles', formatCompatibles(curVehicle, self.compatibles)),)


class WeightedParam(CompatibleParams):

    @property
    def weight(self):
        return self._itemDescr.weight


class ParamsDictProxy(object):
    __slots__ = ('__paramsCalculator', '__cachedParams', '__allAreLoaded', '__conditions', '__filteredByConditions', '__popped')

    def __init__(self, calculator, preload=False, conditions=None):
        super(ParamsDictProxy, self).__init__()
        self.__paramsCalculator = calculator
        self.__cachedParams = {}
        self.__allAreLoaded = False
        self.__conditions = defaultdict(list)
        self.__filteredByConditions = set()
        self.__popped = set()
        if conditions is not None:
            for keys, condition in conditions:
                for key in keys:
                    self.__conditions[key].append(condition)

        if preload:
            self.__loadAllValues()
        return

    def pop(self, item, default=None):
        self.__loadAllValues()
        if item in self:
            value = self[item]
            self.__popped.add(item)
            del self.__cachedParams[item]
        else:
            value = default
        return value

    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default

    def keys(self):
        return list(self.__iter__())

    def values(self):
        self.__loadAllValues()
        return itervalues(self.__cachedParams)

    def items(self):
        self.__loadAllValues()
        return iteritems(self.__cachedParams)

    def iteritems(self):
        self.__loadAllValues()
        return iteritems(self.__cachedParams)

    def __getitem__(self, item):
        if item not in self.__cachedParams:
            if item not in self.__filteredByConditions and item not in self.__popped and hasattr(self.__paramsCalculator, item):
                value = getattr(self.__paramsCalculator, item)
                if inspect.ismethod(value) or not self.__checkConditions(item, value):
                    self.__filteredByConditions.add(item)
                    raise KeyError(item)
                self.__cachedParams[item] = value
            else:
                raise KeyError(item)
        return self.__cachedParams[item]

    def __iter__(self):
        self.__loadAllValues()
        for k in self.__cachedParams:
            if k not in self.__popped:
                yield k

    def __len__(self):
        self.__loadAllValues()
        return len(self.__cachedParams)

    def __contains__(self, item):
        try:
            _ = self[item]
            return True
        except KeyError:
            return False

    def __loadAllValues(self):
        if not self.__allAreLoaded:
            for k, _ in inspect.getmembers(self.__paramsCalculator.__class__, lambda o: isinstance(o, property)):
                value = getattr(self.__paramsCalculator, k)
                if self.__checkConditions(k, value):
                    self.__cachedParams[k] = value

            self.__allAreLoaded = True

    def __checkConditions(self, key, value):
        if key in self.__conditions:
            for func in self.__conditions[key]:
                if not func(value):
                    self.__filteredByConditions.add(key)
                    return False

        return True
