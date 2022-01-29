# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/pagination/pagination_base.py


class IPageDataSource(object):

    def requestData(self, offset, limit):
        raise NotImplementedError

    def getDataCount(self):
        raise NotImplementedError


class PageBase(object):
    __slots__ = ('__idx', '_capacity', '__startIdx', '_dataSource')

    def __init__(self, idx, capacity, startIdx):
        self.__idx = idx
        self._capacity = capacity
        self.__startIdx = startIdx
        self._dataSource = self._getDataSource()

    def getSize(self):
        return len(self._dataSource.requestData(self.__startIdx, self._capacity))

    def getData(self):
        return self._dataSource.requestData(self.__startIdx, self._capacity)

    def getOffset(self):
        return self.__startIdx

    def getIDx(self):
        return self.__idx

    def _getDataSource(self):
        raise NotImplementedError


class BasePaginator(object):
    __slots__ = ('_pages', '__dataCount', '__inited', '__capacity')

    def __init__(self, capacity):
        self._pages = []
        self.__dataCount = 0
        self.__inited = False
        self.__capacity = capacity

    def init(self):
        self._initPages()

    def clear(self):
        self._pages = []
        self.__dataCount = 0
        self.__inited = False

    def isInited(self):
        return self.__inited

    def getDataFromPages(self, offset, limit):
        data = []
        if not self.__inited:
            self._initPages()
        dataCount = self.__dataCount
        if offset < dataCount:
            pageIndex = offset // self.__capacity
            page = self._pages[pageIndex]
            data = page.getData()[offset:limit]
        return data

    def getDataFromPage(self, pageIdx):
        if not self.__inited:
            self._initPages()
        return [] if pageIdx >= self.getPagesCount() else self._pages[pageIdx].getData()

    def getPagesCount(self):
        if not self.__inited:
            self._initPages()
        return len(self._pages)

    def _initPages(self):
        self.__dataCount = self._requestDataCount()
        self._pages = [ self._createPage(idx, self.__capacity, offset) for idx, offset in enumerate(range(0, self.__dataCount, self.__capacity)) ]
        self.__inited = True

    def update(self):
        self._initPages()

    def _requestDataCount(self):
        raise NotImplementedError

    def _createPage(self, idx, capacity, offset):
        raise NotImplementedError
