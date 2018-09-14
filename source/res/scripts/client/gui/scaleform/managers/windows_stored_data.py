# Embedded file name: scripts/client/gui/Scaleform/managers/windows_stored_data.py
from collections import namedtuple, defaultdict
import functools
import types
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_DEBUG
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.doc_loaders.WindowsStoredDataLoader import WindowsStoredDataLoader
from messenger.ext.channel_num_gen import isClientIDValid
WindowGeometry = namedtuple('WindowGeometry', ('x', 'y', 'width', 'height'))

class DATA_TYPE(object):
    UNIQUE_WINDOW = 1
    CAROUSEL_WINDOW = 2
    CHANNEL_WINDOW = 3
    RANGE = (UNIQUE_WINDOW, CAROUSEL_WINDOW, CHANNEL_WINDOW)


class TARGET_ID(object):
    CHANNEL_CAROUSEL = 1
    CHAT_MANAGEMENT = 2
    ALL = CHANNEL_CAROUSEL | CHAT_MANAGEMENT


DEF_TARGET_MASK = TARGET_ID.CHANNEL_CAROUSEL | TARGET_ID.CHAT_MANAGEMENT
STORED_DATA_MAX_LENGTH = 64
STORED_DATA_REV = 1

def _populateStoredData(targetID, window):
    storedData = g_windowsStoredData.getData(targetID, window)
    if storedData is not None:
        geom = storedData.getGeometry()
        if geom is not None:
            window.as_setGeometryS(*geom)
    return


def _updateStoredData(targetID, dataType, pyWindow):
    storedData = g_windowsStoredData.getData(targetID, pyWindow)
    if storedData is None:
        storedData = g_windowsStoredData.addData(targetID, dataType, pyWindow)
    if storedData is not None:
        geom = pyWindow.as_getGeometryS()
        if geom:
            x, y, width, height = geom[:4]
            storedData.setGeometry(WindowGeometry(int(round(x)), int(round(y)), int(round(width)), int(round(height))))
    return


class stored_window(object):

    def __init__(self, dataType, targetID):
        super(stored_window, self).__init__()
        self.__dataType = dataType
        self.__targetID = targetID

    def __call__(self, clazz):
        if not hasattr(clazz, '__mro__'):
            raise Exception, 'First argument is not class'
        if WindowViewMeta not in clazz.__mro__:
            raise Exception, 'Class must be extends WindowViewMeta'

        def wrapPopulate(func):

            @functools.wraps(func)
            def wrapper(window, *args, **kwargs):
                func(window, *args, **kwargs)
                _populateStoredData(self.__targetID, window)

            return wrapper

        def wrapDispose(func):

            @functools.wraps(func)
            def wrapper(window, *args, **kwargs):
                _updateStoredData(self.__targetID, self.__dataType, window)
                func(window, *args, **kwargs)

            return wrapper

        if not getattr(clazz, '__stored_window__', False):
            clazz._populate = wrapPopulate(clazz._populate)
            clazz._dispose = wrapDispose(clazz._dispose)
            clazz.__stored_window__ = True
        else:
            LOG_WARNING('Class already wrapped', clazz)
        return clazz


class WindowStoredData(object):
    __slots__ = ('_trusted', '_geometry')

    def __init__(self, *args):
        super(WindowStoredData, self).__init__()
        self._trusted = True
        if len(args) > 3:
            self._geometry = WindowGeometry(*args[:4])
        else:
            self._geometry = None
        return

    @classmethod
    def _make(cls, window):
        raise NotImplementedError

    @classmethod
    def getDataType(cls):
        return NotImplementedError

    def pack(self):
        raise NotImplementedError

    def getFindCriteria(self):
        raise NotImplementedError

    def isRequiredWindow(self, window):
        return False

    def isTrusted(self):
        return self._trusted

    def setTrusted(self, value):
        self._trusted = value

    def getGeometry(self):
        return self._geometry

    def setGeometry(self, value):
        self._geometry = value


class UniqueWindowStoredData(WindowStoredData):
    __slots__ = ('_uniqueName',)

    def __init__(self, name, *args):
        super(UniqueWindowStoredData, self).__init__(*args)
        if type(name) not in types.StringTypes:
            LOG_WARNING('Unique name must be string. It is ignored', name)
            name = ''
            self._trusted = False
        self._uniqueName = name

    def __repr__(self):
        return 'UniqueWindowStoredData(uniqueName = {0:>s}, geometry = {1!r:s}, trusted = {2!r:s})'.format(self._uniqueName, self._geometry, self._trusted)

    @classmethod
    def _make(cls, window):
        return UniqueWindowStoredData(window.uniqueName)

    @classmethod
    def getDataType(cls):
        return DATA_TYPE.UNIQUE_WINDOW

    def pack(self):
        if not self._uniqueName:
            return
        elif self._geometry is None:
            return
        else:
            return (self._uniqueName,) + self._geometry

    def getFindCriteria(self):
        return self._uniqueName

    def isRequiredWindow(self, window):
        return window.uniqueName == self._uniqueName


class CarouselWindowStoredData(WindowStoredData):
    __slots__ = ('_clientID',)

    def __init__(self, clientID, *args):
        super(CarouselWindowStoredData, self).__init__(*args)
        self._clientID = clientID
        self._trusted = isClientIDValid(clientID)

    def __repr__(self):
        return 'CarouselWindowStoredData(clientID = {0:n}, geometry = {1!r:s}, trusted = {2!r:s})'.format(self._clientID, self._geometry, self._trusted)

    @classmethod
    def _make(cls, window):
        getter = getattr(window, 'getClientID', None)
        if getter and callable(getter):
            clientID = getter()
        else:
            LOG_ERROR('Can not get clientID', window)
            return
        return CarouselWindowStoredData(clientID)

    @classmethod
    def getDataType(cls):
        return DATA_TYPE.CAROUSEL_WINDOW

    def pack(self):
        if not self._clientID:
            return
        elif self._geometry is None:
            return
        else:
            return (self._clientID,) + self._geometry

    def getFindCriteria(self):
        return self._clientID

    def isRequiredWindow(self, window):
        result = False
        getter = getattr(window, 'getClientID', None)
        if getter and callable(getter):
            result = getter() == self._clientID
        return result


class ChannelWindowStoredData(WindowStoredData):
    __slots__ = ('_protoType', '_channelID')

    def __init__(self, protoType, channelID, *args):
        super(ChannelWindowStoredData, self).__init__(*args)
        self._protoType = protoType
        self._channelID = channelID
        self._trusted = False

    def __repr__(self):
        return 'ChannelWindowStoredData(protoType = {0:n}, channelID = {1!r:s}, geometry = {2!r:s}, trusted = {3!r:s})'.format(self._protoType, self._channelID, self._geometry, self._trusted)

    @classmethod
    def _make(cls, window):
        getter = getattr(window, 'getProtoType', None)
        if getter and callable(getter):
            protoType = getter()
        else:
            LOG_ERROR('Can not get protoType', window)
            return
        getter = getattr(window, 'getChannelID', None)
        if getter and callable(getter):
            channelID = getter()
        else:
            LOG_ERROR('Can not get protoType', window)
            return
        return ChannelWindowStoredData(protoType, channelID)

    @classmethod
    def getDataType(cls):
        return DATA_TYPE.CHANNEL_WINDOW

    def pack(self):
        if not self._protoType:
            return
        elif not self._channelID:
            return
        elif self._geometry is None:
            return
        else:
            return (self._protoType, self._channelID) + self._geometry

    def getFindCriteria(self):
        return (self._protoType, self._channelID)

    def isRequiredWindow(self, window):
        result = False
        getter = getattr(window, 'getProtoType', None)
        if getter and callable(getter):
            result = getter() == self._protoType
        if result:
            getter = getattr(window, 'getChannelID', None)
            if getter and callable(getter):
                result = getter() == self._channelID
        return result


class _WindowsStoredDataManager(object):

    def __init__(self, supported):
        super(_WindowsStoredDataManager, self).__init__()
        self.__storedData = defaultdict(list)
        self.__targetMask = DEF_TARGET_MASK
        self.__loader = None
        self.__supported = dict(((clazz.getDataType(), clazz) for clazz in supported))
        self.__isStarted = False
        return

    def start(self):
        if self.__isStarted:
            return
        self.__isStarted = True
        self.__loader = WindowsStoredDataLoader(STORED_DATA_REV, STORED_DATA_MAX_LENGTH, DEF_TARGET_MASK)
        mask, records = self.__loader.load()
        mask |= TARGET_ID.CHAT_MANAGEMENT
        mask |= TARGET_ID.CHANNEL_CAROUSEL
        self.__targetMask = mask & TARGET_ID.ALL
        for record in records:
            if len(record) < 2:
                LOG_ERROR('Invalid record', record)
                continue
            targetID, dataType = record[:2]
            if not targetID & TARGET_ID.ALL:
                LOG_ERROR('Invalid target ID', record)
                continue
            if not self.isTargetEnabled(targetID):
                LOG_WARNING('Target is not enabled. Records are ignored to load', self.__targetMask, record)
                continue
            if dataType not in DATA_TYPE.RANGE:
                LOG_ERROR('Invalid data type', record)
                continue
            if dataType not in self.__supported:
                LOG_ERROR('Data type is not supported', dataType)
                continue
            try:
                self.__storedData[targetID].append(self.__supported[dataType](*record[2:]))
            except TypeError:
                LOG_ERROR('Invalid record', record)

    def stop(self):
        if not self.__isStarted:
            return
        else:
            self.__isStarted = False
            records = []
            for targetID, windowsData in self.__storedData.iteritems():
                if not self.__targetMask & targetID and len(windowsData):
                    LOG_WARNING('Target is not enabled. Records are ignored to flush', targetID, self.__targetMask)
                    continue
                for data in windowsData:
                    if not data.isTrusted():
                        LOG_DEBUG('Data is not trusted. It do not write to file', data)
                        continue
                    record = data.pack()
                    if record is None:
                        continue
                    records.append((targetID, data.getDataType()) + record)

            self.__loader.flush(self.__targetMask, records)
            self.__loader = None
            self.__storedData.clear()
            return

    def isTargetEnabled(self, targetID):
        return self.__isStarted and self.__targetMask & targetID > 0

    def addTarget(self, targetID):
        if self.__targetMask & targetID > 0:
            return
        if not targetID & TARGET_ID.ALL:
            return
        self.__targetMask |= targetID

    def removeTarget(self, targetID):
        if not self.__targetMask & targetID:
            return
        elif not targetID & TARGET_ID.ALL:
            return
        else:
            self.__targetMask ^= targetID
            self.__storedData.pop(targetID, None)
            return

    def addData(self, targetID, dataType, window):
        if not self.isTargetEnabled(targetID):
            return
        elif dataType not in self.__supported:
            LOG_ERROR('Data type is not supported', dataType)
            return
        else:
            clazz = self.__supported[dataType]
            data = clazz._make(window)
            if data is not None:
                self.__storedData[targetID].append(data)
            return data

    def getData(self, targetID, window):
        if not self.isTargetEnabled(targetID):
            return
        else:
            result = None
            for data in self.__storedData[targetID]:
                if data.isRequiredWindow(window):
                    result = data
                    break

            return result

    def getMap(self, targetID, dataType):
        result = {}
        for item in self.__storedData[targetID]:
            if item.getDataType() == dataType:
                result[item.getFindCriteria()] = item

        return result


g_windowsStoredData = _WindowsStoredDataManager((UniqueWindowStoredData, CarouselWindowStoredData, ChannelWindowStoredData))
