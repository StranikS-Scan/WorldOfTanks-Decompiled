# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodie_multiple_resources.py
from typing import TYPE_CHECKING
import GoodieResources as res
from GoodieValue import GoodieValue
if TYPE_CHECKING:
    from typing import Generator, TypeVar
    GoodieResource = TypeVar('GoodieResource', bound=res.GoodieResource)

class GoodieMultiValueDescr(GoodieValue):

    def increase(self, xList):
        return tuple([ super(GoodieMultiValueDescr, self).increase(x) for x in xList.values ])

    def reduce(self, xList):
        return tuple([ super(GoodieMultiValueDescr, self).reduce(x) for x in xList.values ])

    def delta(self, xList):
        return tuple([ super(GoodieMultiValueDescr, self).delta(x) for x in xList.values ])


class MultiValueResourceObject(object):
    __slots__ = ('__values',)

    def __init__(self, values):
        super(MultiValueResourceObject, self).__init__()
        self.__values = values

    def __eq__(self, number):
        for v in self.__values:
            if v != number:
                return False

        return True

    def __sub__(self, other):
        diff = 0
        for i, v in self.__values:
            res = v - other[i]
            if res > diff:
                diff = res

        return diff

    def __lt__(self, other):
        return sum(self.__values) < sum(other.values)

    @property
    def values(self):
        return self.__values


class GoodieMultiResourceList(res.GoodieResource):
    __slots__ = ('_subResources',)

    def __init__(self, values):
        self._subResources = self._getSupportedResourceSubTypes()
        super(GoodieMultiResourceList, self).__init__(MultiValueResourceObject(values))

    @classmethod
    def provideCompatibleValueDescr(cls, actualVal, isPercent):
        return GoodieMultiValueDescr(actualVal, not isPercent)

    @classmethod
    def _getSupportedResourceSubTypes(cls):
        raise NotImplementedError

    def iterate(self):
        multResObjVal = self.value
        for i, subRes in enumerate(self._subResources):
            yield subRes(multResObjVal.values[i])


class FreeXpCrewXpMultiResourceList(GoodieMultiResourceList):

    @classmethod
    def _getSupportedResourceSubTypes(cls):
        return tuple([res.FreeExperience, res.CrewExperience])


class FreeXpMainXpMultiResourceList(GoodieMultiResourceList):

    @classmethod
    def _getSupportedResourceSubTypes(cls):
        return tuple([res.FreeExperience, res.Experience])
