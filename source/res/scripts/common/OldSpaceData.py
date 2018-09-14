# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/OldSpaceData.py
import BigWorld
import logging
import struct
NewAPINotice = '\nInstead of old SpaceData API, please use space properties:\nBigWorld.spaces[ spaceID ].property_name.\nUser level space properties must be defined in space .def file.\n'
WarningFlag = True

def ShowWarningOnce():
    global WarningFlag
    if WarningFlag:
        WarningFlag = False
        import inspect
        func_name = inspect.stack()[1][3]
        logging.warning(func_name + ': This API will be deprecated soon, please use the new API.' + ' All deprecated functions: delSpaceDataForKey,' + ' getSpaceDataFirstForKey, setSpaceData, setSpaceTimeOfDay,' + ' timeOfDay, setSpaceArtificialMinLoad')


def getPropertyNameForKey(key):
    supportedKeys = {0: 'timeOfDay',
     1: 'mappingKeyClientServer',
     2: 'mappingKeyClientOnly',
     32768: 'isRecording',
     32769: 'artificialMinLoad',
     32770: 'serverLoadBounds',
     300: 'itemsVisibilityMask',
     17408: 'recorderFragment',
     16384: 'geometryLoaded',
     16385: 'spaceLoader'}
    try:
        return supportedKeys[key]
    except KeyError:
        raise ValueError('SpaceData key ', key, ' is unsupported', NewAPINotice)


def addSpaceData(spaceID, key, value):
    raise ValueError('addSpaceData is unsupported', NewAPINotice)


def delSpaceData(spaceID, entryID):
    raise ValueError('delSpaceData is unsupported', NewAPINotice)


def delSpaceDataForKey(spaceID, key):
    ShowWarningOnce()
    setSpaceData(spaceID, key, '')


def getSpaceData(spaceID, entryID, key):
    raise ValueError('getSpaceData is unsupported', NewAPINotice)


def getSpaceDataFirstForKey(spaceID, key):
    try:
        ShowWarningOnce()
        if key == 0:
            tod = BigWorld.spaces[spaceID].timeOfDay
            return struct.pack('ff', tod.initialTimeOfDay, tod.gameSecondsPerSecond)
        return getattr(BigWorld.spaces[spaceID], getPropertyNameForKey(key))
    except AttributeError:
        raise AttributeError('SpaceDataObject has no property: ' + getPropertyNameForKey(key) + '. User level space property must be defined' + ' in the space .def file.', NewAPINotice)


def getSpaceDataForKey(spaceID, key):
    raise ValueError('getSpaceDataForKey is unsupported', NewAPINotice)


def setSpaceData(spaceID, key, value):
    try:
        ShowWarningOnce()
        setattr(BigWorld.spaces[spaceID], getPropertyNameForKey(key), value)
        return key
    except AttributeError:
        raise AttributeError('SpaceDataObject has no property: ' + getPropertyNameForKey(key) + '. User level space property must be defined' + ' in the space .def file.', NewAPINotice)


def timeOfDay(spaceID):
    ShowWarningOnce()
    try:
        tod = BigWorld.spaces[spaceID].timeOfDay
        return BigWorld.time() * tod.gameSecondsPerSecond + tod.initialTimeOfDay
    except KeyError:
        logging.warning('BigWorld.timeOfDay( spaceID ): Space is not found, spaceID=' + str(spaceID))
        return -1.0


def setSpaceTimeOfDay(spaceID, initialTimeOfDay, gameSecondsPerSecond):
    ShowWarningOnce()
    BigWorld.spaces[spaceID].timeOfDay = {'initialTimeOfDay': initialTimeOfDay,
     'gameSecondsPerSecond': gameSecondsPerSecond}


def addSpaceGeometryMapping(spaceID, mapper, path, shouldLoadOnServer=True):
    ShowWarningOnce()
    return BigWorld.spaces[spaceID].geometryMappings.add(path, mapper, shouldLoadOnServer)


def setSpaceArtificialMinLoad(spaceID, artificialMinLoad):
    ShowWarningOnce()
    BigWorld.spaces[spaceID].artificialMinLoad = artificialMinLoad


def getSpaceGeometryMappings(spaceID):
    ShowWarningOnce()
    return BigWorld.spaces[spaceID].geometryMappings.values()


BigWorld.addSpaceData = addSpaceData
BigWorld.delSpaceData = delSpaceData
BigWorld.delSpaceDataForKey = delSpaceDataForKey
BigWorld.getSpaceData = getSpaceData
BigWorld.getSpaceDataFirstForKey = getSpaceDataFirstForKey
BigWorld.getSpaceDataForKey = getSpaceDataForKey
BigWorld.setSpaceData = setSpaceData
BigWorld.timeOfDay = timeOfDay
BigWorld.setSpaceTimeOfDay = setSpaceTimeOfDay
BigWorld.addSpaceGeometryMapping = addSpaceGeometryMapping
BigWorld.getSpaceGeometryMappings = getSpaceGeometryMappings
BigWorld.setSpaceArtificialMinLoad = setSpaceArtificialMinLoad
