# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_toy_info.py
import random
from helpers import dependency
from items import collectibles
from gui.impl.gen import R
from items import new_year
from items.components.ny_constants import YEARS_INFO, MAX_TOY_RANK, ToySettings
from new_year.ny_constants import TOY_PREFIX, Collections
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_PASSEPARTOUTS = ('passepartout_1', 'passepartout_2', 'passepartout_3', 'passepartout_4')
_EMPTY_PASSEPARTOUT = '_empty_passpartout'
TOYS_INFO_REGISTRY = {}

def registerInDict(registryDict, keyName):

    def wrapper(objectValue):
        registryDict[keyName] = objectValue
        return objectValue

    return wrapper


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

    def getCollectionName(self):
        return self.getSetting()

    def getCollectionID(self):
        return new_year.getToySettingID(toyDescr=self._descriptor)

    def getShards(self):
        craftCostConfig = self._lobbyCtx.getServerSettings().getNewYearCraftCostConfig()
        return craftCostConfig.calculateOldCraftCost(self.getID(), self.COLLECTION_NAME)

    def isInCollection(self):
        toyCollection = self._itemsCache.items.festivity.getToyCollection()
        toyID = self.getID()
        bytePos = YEARS_INFO.getToyCollectionOffsetForYear(self.COLLECTION_NAME) + toyID / 8
        mask = 1 << toyID % 8
        return True if toyCollection[bytePos] & mask else False

    def isMega(self):
        return self.getSetting() == ToySettings.MEGA_TOYS


class _NewYearBackportToyInfo(_NewYearCommonToyInfo):
    PREFIX = ''
    __slots__ = ()

    def getLocalKey(self):
        return TOY_PREFIX + str(self.getID())

    def getName(self):
        return R.strings.dyn(self.PREFIX).decorations.dyn(self.getLocalKey()).name()

    def getDesc(self):
        return R.strings.dyn(self.PREFIX).decorations.dyn(self.getLocalKey()).description() if self.getRank() == MAX_TOY_RANK or self.isMega() else R.invalid()

    def getIcon(self):
        return R.images.gui.maps.icons.new_year.dyn(self.PREFIX).big.dyn(self.getIconName())()

    def getRankIcon(self):
        if not self.isMega():
            image = R.images.gui.maps.icons.new_year.slots.c_80x80.ranks.dyn('rank_{}'.format(self._descriptor.rank))()
        else:
            image = R.invalid()
        return image


@registerInDict(TOYS_INFO_REGISTRY, Collections.NewYear18)
class NewYear18ToyInfo(_NewYearCommonToyInfo):
    COLLECTION_NAME = Collections.NewYear18
    __slots__ = ()

    def __init__(self, toyID):
        super(NewYear18ToyInfo, self).__init__(collectibles.g_cache.ny18.toys[toyID])

    def getName(self):
        return R.strings.toys18.dyn(self._descriptor.name)()

    def getDesc(self):
        return R.strings.toys18.descr.dyn(self._descriptor.name, R.invalid)()

    def getIcon(self):
        return R.images.gui.maps.icons.new_year.toys18.big.dyn(self._descriptor.icon)()

    def getEmptyPassepartout(self):
        return R.images.gui.maps.icons.new_year.album.page18.passepartout_empty()

    def getPassepartout(self):
        passepartout = random.choice(_PASSEPARTOUTS)
        return R.images.gui.maps.icons.new_year.album.page18.dyn(passepartout)()


@registerInDict(TOYS_INFO_REGISTRY, Collections.NewYear19)
class NewYear19ToyInfo(_NewYearBackportToyInfo):
    PREFIX = 'toys19'
    COLLECTION_NAME = Collections.NewYear19
    __slots__ = ()

    def __init__(self, toyID):
        super(NewYear19ToyInfo, self).__init__(collectibles.g_cache.ny19.toys[toyID])

    def getEmptyPassepartout(self):
        return R.images.gui.maps.icons.new_year.album.page19.passepartout_empty()

    def getPassepartout(self):
        passepartout = random.choice(_PASSEPARTOUTS)
        return R.images.gui.maps.icons.new_year.album.page19.dyn(passepartout)()


@registerInDict(TOYS_INFO_REGISTRY, Collections.NewYear20)
class NewYear20ToyInfo(_NewYearBackportToyInfo):
    PREFIX = 'toys20'
    COLLECTION_NAME = Collections.NewYear20
    __slots__ = ()

    def __init__(self, toyID):
        super(NewYear20ToyInfo, self).__init__(collectibles.g_cache.ny20.toys[toyID])

    def getEmptyPassepartout(self):
        return R.images.gui.maps.icons.new_year.album.page20.passepartout_empty_mega() if self.isMega() else R.images.gui.maps.icons.new_year.album.page20.passepartout_empty()

    def getPassepartout(self):
        passepartout = random.choice(_PASSEPARTOUTS)
        return R.images.gui.maps.icons.new_year.album.page20.megaPass.dyn(passepartout)() if self.isMega() else R.images.gui.maps.icons.new_year.album.page19.dyn(passepartout)()

    def getIcon(self, extraSize=False):
        size = 'extra_big' if extraSize else 'big'
        return R.images.gui.maps.icons.new_year.dyn(self.PREFIX).dyn(size).dyn(self._descriptor.icon)()


class NewYearCurrentToyInfo(NewYear20ToyInfo):

    def getShards(self):
        toyDecayCostConfig = self._lobbyCtx.getServerSettings().getNewYearToyDecayCostConfig()
        return toyDecayCostConfig.getToyDecayCost(toyDescr=self._descriptor)

    def getAtmosphere(self):
        generalConfig = self._lobbyCtx.getServerSettings().getNewYearGeneralConfig()
        pointsByRank = generalConfig.getAtmospherePointsByToyRank()
        return pointsByRank[self.getRank() - 1]

    def getToyObject(self):
        return new_year.getObjectByToyType(self.getToyType())
