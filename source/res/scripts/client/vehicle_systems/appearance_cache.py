# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/appearance_cache.py
import functools
import logging
from collections import namedtuple
import BigWorld
import Event
from skeletons.vehicle_appearance_cache import IAppearanceCache
from soft_exception import SoftException
from vehicle_systems.CompoundAppearance import CompoundAppearance
from vehicle_systems.stricted_loading import loadingPriority
_logger = logging.getLogger(__name__)
VehicleAppearanceCacheInfo = namedtuple('VehicleAppearanceCacheInfo', ['typeDescr',
 'health',
 'isCrewActive',
 'isTurretDetached',
 'outfitCD'])
_AssemblerData = namedtuple('_AssemblerData', ['appearance', 'typeDescr', 'prereqsNames'])

class _LoadInfo(object):
    __slots__ = ('appearance', 'onConstructed', 'taskId', 'typeDescr')

    def __init__(self, appearance, taskId, typeDescr, onConstructedCallback):
        self.appearance = appearance
        self.taskId = taskId
        self.typeDescr = typeDescr
        self.onConstructed = Event.Event()
        if onConstructedCallback is not None:
            self.onConstructed += onConstructedCallback
        return

    def destroy(self):
        self.onConstructed.clear()


class AppearanceCache(IAppearanceCache):
    __slots__ = ('__arena', '__appearanceCache', '__assemblerCache', '__loadingAssemblerQueue')

    def __init__(self):
        self.__appearanceCache = {}
        self.__assemblerCache = {}
        self.__resourceCache = {}
        self.__loadingAssemblerQueue = {}
        self.__loadingResourceQueue = {}

    def getAppearance(self, vId, info, onCreatedCallback=None, strCD=None):
        _logger.debug('getAppearance(%d)', vId)
        key = self.__makeUniqueKey(vId, strCD)
        self.__validateAppearanceCache(key)
        if key in self.__appearanceCache:
            _logger.debug('getAppearance of (%d) is in __appearanceCache', vId)
            appearance = self.__appearanceCache.get(key)
            if onCreatedCallback is not None:
                onCreatedCallback(appearance)
            return appearance
        else:
            return self.__construct(key, onCreatedCallback) if key in self.__assemblerCache else self.__load(key, info, onCreatedCallback)

    def removeAppearance(self, vId, strCD=None):
        _logger.debug('removeAppearance(%d)', vId)
        if strCD is None:
            for vehicleID, compactDescr in self.__appearanceCache.iterkeys():
                if vehicleID == vId:
                    strCD = compactDescr
                    break

        key = self.__makeUniqueKey(vId, strCD)
        self.__validateAppearanceCache(key)
        appearance = self.__appearanceCache.pop(key, None)
        self.__assemblerCache.pop(key, None)
        self.stopLoading(vId, strCD)
        return appearance

    def stopLoading(self, vId, strCD=None):
        _logger.debug('stopLoading(%d)', vId)
        key = self.__makeUniqueKey(vId, strCD)
        info = self.__loadingAssemblerQueue.pop(key, None)
        if info is not None:
            _logger.debug('stopLoadResourceListBGTask vehicle = (%d), task = (%d)', vId, info.taskId)
            info.onConstructed.clear()
            BigWorld.stopLoadResourceListBGTask(info.taskId)
        return

    def loadResources(self, compactDescr, prereqs):
        _logger.debug('loadResources(%s)', repr(compactDescr))
        self.__validateResourceCache(compactDescr)
        if compactDescr in self.__resourceCache or compactDescr in self.__loadingResourceQueue:
            return
        self.__loadingResourceQueue[compactDescr] = BigWorld.loadResourceListBG(prereqs, functools.partial(self.__onResourceLoaded, compactDescr))

    def unloadResources(self, compactDescr):
        _logger.debug('unloadResources(%s)', repr(compactDescr))
        self.__validateResourceCache(compactDescr)
        taskId = self.__loadingResourceQueue.pop(compactDescr)
        BigWorld.stopLoadResourceListBGTask(taskId)
        self.__resourceCache.pop(compactDescr, None)
        return

    def clear(self):
        _logger.debug('clear')
        for appearance in self.__appearanceCache.itervalues():
            appearance.destroy()

        self.__appearanceCache.clear()
        self.__assemblerCache.clear()
        for task in self.__loadingAssemblerQueue.itervalues():
            BigWorld.stopLoadResourceListBGTask(task.taskId)
            task.onConstructed.clear()

        self.__loadingAssemblerQueue.clear()
        self.__resourceCache.clear()
        for taskId in self.__loadingResourceQueue.itervalues():
            BigWorld.stopLoadResourceListBGTask(taskId)

        self.__loadingResourceQueue.clear()

    def __validateAppearanceCache(self, key):
        checker = 0
        if key in self.__loadingAssemblerQueue:
            checker += 1
        if key in self.__assemblerCache:
            checker += 1
        if key in self.__appearanceCache:
            checker += 1
        if checker > 1:
            raise SoftException('Invalid appearance cache state for id = {}!'.format(key))

    def __validateResourceCache(self, compactDescr):
        checker = 0
        if compactDescr in self.__loadingResourceQueue:
            checker += 1
        if compactDescr in self.__resourceCache:
            checker += 1
        if checker > 1:
            raise SoftException('Invalid resource cache state for id = {}!'.format(repr(compactDescr)))

    def __construct(self, key, onFinishedCallback):
        _logger.debug('__construct(%d)', key[0])
        data = self.__assemblerCache.pop(key, None)
        if data is None:
            return
        else:
            data.typeDescr.keepPrereqs(data.prereqsNames)
            appearance = data.appearance
            appearance.construct(BigWorld.player().playerVehicleID == key[0], data.prereqsNames)
            self.__appearanceCache[key] = appearance
            onFinishedCallback(appearance)
            return appearance

    def __load(self, key, info, onLoadedCallback=None):
        _logger.debug('__load(%d)', key[0])
        loadInfo = self.__loadingAssemblerQueue.get(key)
        if loadInfo is not None:
            if onLoadedCallback is not None:
                loadInfo.onConstructed += onLoadedCallback
            return loadInfo.appearance
        else:
            appearance = CompoundAppearance()
            prereqs = appearance.prerequisites(info.typeDescr, key[0], info.health, info.isCrewActive, info.isTurretDetached, info.outfitCD)
            taskId = BigWorld.loadResourceListBG(prereqs, functools.partial(self.__onAppearanceLoaded, key), loadingPriority(key[0]))
            _logger.debug('loadResourceListBG vehicle = (%d), task = (%d)', key[0], taskId)
            self.__loadingAssemblerQueue[key] = _LoadInfo(appearance, taskId, info.typeDescr, onLoadedCallback)
            return appearance

    def __onAppearanceLoaded(self, key, resourceRefs):
        _logger.debug('__onAppearanceLoaded(%d)', key[0])
        info = self.__loadingAssemblerQueue.pop(key, None)
        if info is None:
            raise SoftException('appearance {} is loaded but is missing from loadingQueue! info = {}'.format(key, info))
        self.__assemblerCache[key] = _AssemblerData(info.appearance, info.typeDescr, resourceRefs)
        self.__construct(key, info.onConstructed)
        return

    def __onResourceLoaded(self, compactDescr, resourceRefs):
        _logger.debug('__onResourceLoaded(%s)', repr(compactDescr))
        if compactDescr in self.__resourceCache:
            raise SoftException('resource {} is already loaded!'.format(repr(compactDescr)))
        self.__resourceCache[compactDescr] = resourceRefs

    @staticmethod
    def __makeUniqueKey(vehID, strCD):
        return (vehID, strCD)
