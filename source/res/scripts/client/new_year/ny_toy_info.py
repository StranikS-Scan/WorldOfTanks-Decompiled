# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_toy_info.py
import logging
from collections import namedtuple
from helpers import dependency
from items import collectibles
from gui.impl.gen import R
from items import new_year
from items.components.ny_constants import YEARS_INFO, MAX_TOY_RANK, ToySettings, ToyTypes, UNDEFINED_TOY_RANK
from new_year.ny_constants import TOY_PREFIX
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)
_SLOT_TYPE_ORDER = {v:i for i, v in enumerate((ToyTypes.MEGA_FIR,
 ToyTypes.MEGA_TABLEFUL,
 ToyTypes.MEGA_INSTALLATION,
 ToyTypes.MEGA_ILLUMINATION,
 ToyTypes.KIOSK,
 ToyTypes.ATTRACTION,
 ToyTypes.GARLAND_FAIR,
 ToyTypes.GARLAND_INSTALLATION,
 ToyTypes.FERRIS_WHEEL,
 ToyTypes.AIRSHIP,
 ToyTypes.CASTLE,
 ToyTypes.TOP,
 ToyTypes.GARLAND,
 ToyTypes.GARLAND_FIR,
 ToyTypes.BALL,
 ToyTypes.FLOOR,
 ToyTypes.TABLE,
 ToyTypes.KITCHEN,
 ToyTypes.SCULPTURE,
 ToyTypes.DECORATION,
 ToyTypes.SCULPTURE_LIGHT,
 ToyTypes.TREES,
 ToyTypes.GROUND_LIGHT,
 ToyTypes.TENT,
 ToyTypes.PAVILION,
 ToyTypes.EXPOSITION,
 ToyTypes.SNOW_ITEM,
 ToyTypes.PYRO,
 ToyTypes.DOG_BOWL,
 ToyTypes.DOG_TOY,
 ToyTypes.DOG_COLLAR,
 ToyTypes.DOG_HOUSE,
 ToyTypes.COLOR_FIR))}
_TOY_SETTING_ORDER = {v:i for i, v in enumerate((ToySettings.NEW_YEAR,
 ToySettings.CHRISTMAS,
 ToySettings.ORIENTAL,
 ToySettings.FAIRYTALE,
 ToySettings.MEGA_TOYS,
 ToySettings.DOG_TOYS))}
_SortPriorityPart = namedtuple('SortPriorityPart', ('value', 'max'))

def registerInDict(registryDict, keyName):

    def wrapper(objectValue):
        registryDict[keyName] = objectValue
        return objectValue

    return wrapper


def _packSortPriority(descriptor):
    order = (_SortPriorityPart(MAX_TOY_RANK - descriptor.rank, MAX_TOY_RANK), _SortPriorityPart(_SLOT_TYPE_ORDER[descriptor.type], max(_SLOT_TYPE_ORDER.itervalues())), _SortPriorityPart(_TOY_SETTING_ORDER[descriptor.setting], max(_TOY_SETTING_ORDER.itervalues())))
    value = offset = 0
    for part in reversed(order):
        value |= part.value << offset
        offset += part.max.bit_length()

    return value


class _NewYearCommonToyInfo(object):
    COLLECTION_NAME = ''
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    __slots__ = ('_descriptor',)

    def __init__(self, descriptor):
        super(_NewYearCommonToyInfo, self).__init__()
        self._descriptor = descriptor

    def getToyType(self):
        return self._descriptor.type

    def getID(self):
        return self._descriptor.id

    def getSetting(self):
        return self._descriptor.setting

    def getRank(self):
        return self._descriptor.rank

    def getIconName(self):
        return self._descriptor.icon

    def getDropSource(self):
        return self._descriptor.dropSource

    def getCollectionName(self):
        return self.getSetting()

    def getCollectionID(self):
        return new_year.getToySettingID(toyDescr=self._descriptor)

    def isInCollection(self):
        toyCollection = self._itemsCache.items.festivity.getToyCollection()
        toyID = self.getID()
        bytePos = YEARS_INFO.getToyCollectionOffsetForYear(self.COLLECTION_NAME) + toyID / 8
        mask = 1 << toyID % 8
        return True if toyCollection[bytePos] & mask else False

    def getIcon(self, size='medium'):
        res = R.images.gui.maps.icons.newYear.toys.dyn(size).dyn(self.getIconName())
        if not res.exists():
            _logger.error('Missing NY Toy icon. Toy ID: %s; icon size: %s.', self.getID(), size)
            return R.invalid()
        return res()


class _NewYearBackportToyInfo(_NewYearCommonToyInfo):
    __slots__ = ()

    def getLocalKey(self):
        return TOY_PREFIX + str(self.getID())

    def getName(self):
        return R.strings.toys.decorations.dyn(self.getLocalKey()).name()

    def getDesc(self):
        return R.strings.toys.decorations.dyn(self.getLocalKey()).description() if self.getRank() == YEARS_INFO.getMaxToyRankByYear(self.COLLECTION_NAME) else R.invalid()

    def getRankIcon(self):
        return R.invalid()


class NewYearCurrentToyInfo(_NewYearBackportToyInfo):
    COLLECTION_NAME = YEARS_INFO.CURRENT_YEAR_STR
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__sortPriority',)

    def __init__(self, toyID):
        descriptor = collectibles.g_cache[self.COLLECTION_NAME].toys[toyID]
        super(NewYearCurrentToyInfo, self).__init__(descriptor)
        self.__sortPriority = _packSortPriority(descriptor)

    def getToyObject(self):
        return new_year.getObjectByToyType(self.getToyType())

    def getSortPriority(self):
        return self.__sortPriority

    def getRank(self):
        return UNDEFINED_TOY_RANK

    def getDesc(self):
        return R.strings.toys.decorations.dyn(self.getLocalKey()).description()
