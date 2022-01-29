# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/envelopes/storage_envelopes_pagination.py
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.pagination.pagination_base import PageBase, BasePaginator, IPageDataSource
from skeletons.gui.shared import IItemsCache

class StorageEnvelopesDataSource(IPageDataSource):
    __slots__ = ('__envelopeType',)
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, envelopeType):
        self.__envelopeType = envelopeType

    def requestData(self, offset, limit):
        return self.__itemsCache.items.giftSystem.getGiftFromStorage(self.__getGiftID(), offset, limit)

    def getDataCount(self):
        return self.__itemsCache.items.giftSystem.getGiftStorageGroupedCount(self.__getGiftID())

    def findGiftBySenderID(self, receiverID):
        return self.__itemsCache.items.giftSystem.findGiftBySenderID(self.__getGiftID(), receiverID)

    def __getGiftID(self):
        return self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(self.__envelopeType)


class StorageEnvelopesPage(PageBase):
    __slots__ = ('__envelopeType',)

    def __init__(self, idx, capacity, startIdx, envelopeType):
        self.__envelopeType = envelopeType
        super(StorageEnvelopesPage, self).__init__(idx, capacity, startIdx)

    def _getDataSource(self):
        return StorageEnvelopesDataSource(self.__envelopeType)


class StorageEnvelopesPaginator(BasePaginator):
    __slots__ = ('__envelopeType', '__dataSource')
    _PAGES_CAPACITY = 20
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, envelopeType):
        self.__envelopeType = envelopeType
        self.__dataSource = StorageEnvelopesDataSource(self.__envelopeType)
        super(StorageEnvelopesPaginator, self).__init__(self._PAGES_CAPACITY)

    def findPageById(self, senderID):
        if not self.isInited():
            self._initPages()
        idxInData, _ = self.__dataSource.findGiftBySenderID(senderID)
        for page in self._pages:
            if page.getOffset() <= idxInData < page.getOffset() + page.getSize():
                return page.getIDx()

    def _requestDataCount(self):
        return self.__dataSource.getDataCount()

    def _createPage(self, idx, capacity, offset):
        return StorageEnvelopesPage(idx, capacity, offset, self.__envelopeType)
