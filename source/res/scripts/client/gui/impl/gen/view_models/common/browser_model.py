# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/browser_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BrowserState(Enum):
    INITIALIZATION = 'initialization'
    LOADING = 'loading'
    FORCELOADING = 'forceLoading'
    LOADED = 'loaded'


class PageState(Enum):
    INITIALIZATION = 'initialization'
    LOADING = 'loading'
    LOADED = 'loaded'
    FAILED = 'failed'


class BrowserModel(ViewModel):
    __slots__ = ('createWebView', 'focus', 'unfocus')

    def __init__(self, properties=6, commands=3):
        super(BrowserModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getBrowserState(self):
        return BrowserState(self._getString(1))

    def setBrowserState(self, value):
        self._setString(1, value.value)

    def getPageState(self):
        return PageState(self._getString(2))

    def setPageState(self, value):
        self._setString(2, value.value)

    def getHttpStatusCode(self):
        return self._getNumber(3)

    def setHttpStatusCode(self, value):
        self._setNumber(3, value)

    def getTitle(self):
        return self._getString(4)

    def setTitle(self, value):
        self._setString(4, value)

    def getWaitingMessage(self):
        return self._getString(5)

    def setWaitingMessage(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(BrowserModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('browserState')
        self._addStringProperty('pageState')
        self._addNumberProperty('httpStatusCode', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('waitingMessage', '')
        self.createWebView = self._addCommand('createWebView')
        self.focus = self._addCommand('focus')
        self.unfocus = self._addCommand('unfocus')
