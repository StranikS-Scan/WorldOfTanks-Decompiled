# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/data_providers.py
# Compiled at: 2011-07-29 13:15:51
from abc import abstractmethod, ABCMeta, abstractproperty
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface

class BaseDataProvider(UIInterface):
    __metaclass__ = ABCMeta

    def __init__(self, prefix):
        UIInterface.__init__(self)
        self.__prefix = prefix

    def prefix(self):
        return self.__prefix

    @abstractmethod
    def buildList(self, *args):
        pass

    @abstractmethod
    def emptyItem(self):
        pass

    @abstractproperty
    def list(self):
        pass

    def length(self):
        return len(self.list)

    def requestItemAt(self, idx):
        if -1 < idx < self.length():
            return self.list[idx]
        else:
            return None

    def requestItemRange(self, startIndex, endIndex):
        return self.list[startIndex:endIndex]

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'%s.RequestLength' % self.__prefix: self.onRequestLength,
         '%s.RequestItemAt' % self.__prefix: self.onRequestItemAt,
         '%s.RequestItemRange' % self.__prefix: self.onRequestItemRange})

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('%s.RequestLength' % self.__prefix, '%s.RequestItemAt' % self.__prefix, '%s.RequestItemRange' % self.__prefix)
        UIInterface.dispossessUI(self)

    def refresh(self):
        self.uiHolder.call('%s.RefreshList' % self.__prefix, [self.length()])

    def onRequestLength(self, *args):
        parser = CommandArgsParser(self.onRequestLength.__name__)
        parser.parse(*args)
        parser.addArg(self.length())
        self.respond(parser.args())

    def onRequestItemAt(self, *args):
        parser = CommandArgsParser(self.onRequestItemAt.__name__, 1, [int])
        index = parser.parse(*args)
        item = self.requestItemAt(index)
        if item:
            parser.addArgs(item)
        else:
            parser.addArgs(self.emptyItem())
        self.respond(parser.args())

    def onRequestItemRange(self, *args):
        parser = CommandArgsParser(self.onRequestItemRange.__name__, 2, [int, int])
        startIndex, endIndex = parser.parse(*args)
        for item in self.list[startIndex:endIndex + 1]:
            parser.addArgs(item)

        self.respond(parser.args())
