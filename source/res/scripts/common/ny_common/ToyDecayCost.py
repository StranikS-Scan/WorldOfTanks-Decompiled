# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/ToyDecayCost.py
from typing import Optional, TYPE_CHECKING
from items import new_year
from items.components.ny_constants import MEGA_TOY_TYPES
if TYPE_CHECKING:
    from items.collectibles import ToyDescriptor

class ToyDecayCostConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getToyDecayCost(self, toyID=None, toyDescr=None):
        if toyDescr is None:
            toyDescr = new_year.g_cache.toys[toyID]
        return getattr(toyDescr, 'fragments', 0) or self._config.get((toyDescr.type, toyDescr.rank), 0)

    def getMaxToyDecayCost(self):
        maxCost = 0
        for (toyType, _), toyCost in self._config.iteritems():
            if toyType in MEGA_TOY_TYPES:
                continue
            if toyCost > maxCost:
                maxCost = toyCost

        return maxCost
