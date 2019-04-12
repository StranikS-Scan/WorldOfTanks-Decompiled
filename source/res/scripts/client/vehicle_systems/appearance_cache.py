# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/appearance_cache.py
import weakref
from collections import namedtuple
import BigWorld
from debug_utils import LOG_DEBUG, LOG_WARNING
from vehicle_systems import vehicle_assembler
from vehicle_systems.stricted_loading import loadingPriority, makeCallbackWeak
_ENABLE_CACHE_TRACKER = False
_ENABLE_PRECACHE = True
_g_cache = None
d_cacheInfo = None
_VehicleInfo = namedtuple('_VehicleInfo', ['typeDescr',
 'health',
 'isCrewActive',
 'isTurretDetached',
 'outfitCD'])
_AssemblerData = namedtuple('_AssemblerData', ['compoundAssembler',
 'assembler',
 'info',
 'prereqsNames'])

class _AppearanceCache(object):
    __slots__ = ('__arena', '__appearanceCache', '__assemblersCache', '__spaceLoaded')

    @property
    def cache(self):
        return self.__appearanceCache

    def __init__(self, arena):
        global d_cacheInfo
        self.__arena = weakref.proxy(arena)
        self.__appearanceCache = dict()
        self.__assemblersCache = dict()
        self.__spaceLoaded = False
        self.__arena.onNewVehicleListReceived += self.onVehicleListReceived
        self.__arena.onVehicleAdded += self.onVehicleAddedUpdate
        self.__arena.onVehicleUpdated += self.onVehicleAddedUpdate
        if getattr(self.__arena.componentSystem, 'playerDataComponent', None):
            self.__arena.componentSystem.playerDataComponent.onPlayerGroupsUpdated += self.__onPlayerGroupsUpdated
        if _ENABLE_CACHE_TRACKER:
            d_cacheInfo = dict()
        return

    def destroy(self):
        global d_cacheInfo
        self.__arena.onVehicleAdded -= self.onVehicleAddedUpdate
        self.__arena.onVehicleUpdated -= self.onVehicleAddedUpdate
        self.__arena.onNewVehicleListReceived -= self.onVehicleListReceived
        if getattr(self.__arena.componentSystem, 'playerDataComponent', None):
            self.__arena.componentSystem.playerDataComponent.onPlayerGroupsUpdated -= self.__onPlayerGroupsUpdated
        for _, appearance in self.__appearanceCache.iteritems():
            appearance[0].destroy()

        self.__arena = None
        self.__appearanceCache = None
        self.__assemblersCache = None
        if _ENABLE_CACHE_TRACKER:
            d_cacheInfo = None
        return

    def onVehicleListReceived(self):
        if not self.__spaceLoaded or not _ENABLE_PRECACHE:
            return
        self.__precacheVehicle(self.__arena.vehicles)

    def onVehicleAddedUpdate(self, vId):
        if _ENABLE_PRECACHE:
            vInfo = self.__arena.vehicles[vId]
            self.__precacheVehicle({vId: vInfo})

    def onSpaceLoaded(self):
        self.__spaceLoaded = True
        if _ENABLE_PRECACHE:
            self.__precacheVehicle(self.__arena.vehicles)

    def cacheApperance(self, vId, info):
        if vId in self.__assemblersCache or vId in self.__appearanceCache:
            return
        else:
            typeDescriptor = info['vehicleType']
            if typeDescriptor is None:
                return
            isAlive = info['isAlive']
            outfitCD = info['outfitCD']
            self.__cacheApperance(vId, _VehicleInfo(typeDescriptor, 1 if isAlive else 0, True if isAlive else False, False, outfitCD))
            return

    def createAppearance(self, vId, vInfo, forceReloadingFromCache):
        appearanceInfo = self.__appearanceCache.get(vId, None)
        appearance = None
        compoundAssembler = None
        prereqsNames = []
        if appearanceInfo is None or not self.__validate(appearanceInfo[1], vInfo) or not self.__validateAppearanceWithInfo(appearanceInfo[0], vInfo) or forceReloadingFromCache:
            assemblerData = self.__assemblersCache.get(vId, None)
            if assemblerData is None or not self.__validate(assemblerData.info, vInfo) or forceReloadingFromCache:
                compoundAssembler, prereqsNames = self.__cacheApperance(vId, vInfo)
            else:
                compoundAssembler = assemblerData.compoundAssembler
                prereqsNames = assemblerData.prereqsNames
        else:
            appearance, _ = appearanceInfo
        return (appearance, compoundAssembler, prereqsNames)

    def getAppearance(self, vId, resourceRefs):
        if _ENABLE_CACHE_TRACKER:
            LOG_DEBUG('Appearance cache. Get appearance vID = {0}'.format(vId))
        appearance, _ = self.__appearanceCache.get(vId, (None, None))
        return self.constructAppearance(vId, resourceRefs) if appearance is None else appearance

    def constructAppearance(self, vId, resourceRefs):
        assemblerData = self.__assemblersCache.get(vId, None)
        if assemblerData is None:
            return
        else:
            assembler = assemblerData.assembler
            if assemblerData.compoundAssembler is None:
                if _ENABLE_CACHE_TRACKER:
                    LOG_DEBUG("Appearance cache. Can't find assembler vID = {0}".format(vId))
                return
            if _ENABLE_CACHE_TRACKER:
                LOG_DEBUG('Appearance cache. Constructed vID = {0}'.format(vId))
            if not resourceRefs.has_key(assemblerData.info.typeDescr.name):
                LOG_WARNING('Loaded appearance is not latest requested appearance, construction of the appearance is skipped ', assemblerData.info.typeDescr.name, resourceRefs)
                return
            assemblerData.info.typeDescr.keepPrereqs(resourceRefs)
            assembler.appearance.start(resourceRefs)
            assembler.constructAppearance(BigWorld.player().playerVehicleID == vId, resourceRefs)
            appearance = assembler.appearance
            oldAppearance = self.__appearanceCache.get(vId, None)
            if oldAppearance is not None:
                oldAppearance[0].destroy()
                self.__appearanceCache[vId] = None
                if _ENABLE_CACHE_TRACKER:
                    LOG_DEBUG('Appearance cache. Deleting old appearance vID = {0}'.format(vId))
            self.__appearanceCache[vId] = (appearance, assemblerData.info)
            del self.__assemblersCache[vId]
            del assembler
            if _ENABLE_CACHE_TRACKER:
                d_cacheInfo[vId] = BigWorld.time()
            return appearance

    def __cacheApperance(self, vId, info):
        assembler = vehicle_assembler.createAssembler()
        prereqs = info.typeDescr.prerequisites(True)
        compoundAssembler, assemblerPrereqs = assembler.prerequisites(info.typeDescr, vId, info.health, info.isCrewActive, info.isTurretDetached, info.outfitCD)
        prereqs += assemblerPrereqs
        if vId in self.__assemblersCache:
            assemblerData = self.__assemblersCache.get(vId, None)
            if assemblerData is not None:
                oldAssembler = assemblerData.assembler
                LOG_WARNING('The latest resources for the vehicle are not loaded yet, deleting old assember and creating new one %s %s' % (info.typeDescr.name, assemblerData.info.typeDescr))
                del oldAssembler
            del self.__assemblersCache[vId]
        self.__assemblersCache[vId] = _AssemblerData(compoundAssembler, assembler, info, prereqs)
        if self.__spaceLoaded:
            BigWorld.loadResourceListBG(prereqs, makeCallbackWeak(_resourceLoaded, prereqs, vId), loadingPriority(vId))
        return (compoundAssembler, prereqs)

    def __validateAppearanceWithInfo(self, appearance, info):
        isAlive = 1 if info.health > 0 else 0
        return appearance and appearance.isAlive == isAlive

    def __validate(self, cachedInfo, newInfo):
        valid = cachedInfo.typeDescr.type.name == newInfo.typeDescr.type.name and cachedInfo.outfitCD == newInfo.outfitCD
        return valid

    def __onPlayerGroupsUpdated(self, vIds):
        if not _ENABLE_PRECACHE or not self.__arena.vehicles or not self.__spaceLoaded:
            return
        else:
            playerVehicleId = getattr(BigWorld.player(), 'playerVehicleID', 0)
            if playerVehicleId <= 0:
                return
            groupIDs = None
            if playerVehicleId in vIds:
                vehicleInfos = self.__arena.vehicles
            else:
                vehicleInfos = dict(((vId, self.__arena.vehicles[vId]) for vId in vIds))
                groupIDs = vIds
            self.__precacheVehicle(vehicleInfos, groupIDs)
            return

    def __precacheVehicle(self, vehicleIDs, groupIDs=None):
        playerGroupId = -1
        if self.__arena.arenaType.numPlayerGroups > 0 and getattr(self.__arena.componentSystem, 'playerDataComponent', None):
            playerGroupId = self.__arena.componentSystem.playerDataComponent.getPlayerGroupForPlayer()
        for vId, vInfo in vehicleIDs.iteritems():
            if playerGroupId > 0:
                groupId = groupIDs[vId] if groupIDs else self.__arena.componentSystem.playerDataComponent.getPlayerGroupForVehicle(vId)
                if groupId != playerGroupId:
                    continue
            cacheApperance(vId, vInfo)

        return


def _resourceLoaded(resNames, vId, resourceRefs):
    global _g_cache
    if _g_cache is None:
        return
    else:
        failedRefs = resourceRefs.failedIDs
        for resName in resNames:
            if resName in failedRefs:
                LOG_WARNING('Resource is not found', resName)

        _g_cache.constructAppearance(vId, resourceRefs)
        return


def init(clientArena):
    global _g_cache
    _g_cache = _AppearanceCache(clientArena)


def destroy():
    global _g_cache
    _g_cache.destroy()
    _g_cache = None
    return


def onSpaceLoaded():
    _g_cache.onSpaceLoaded()


def createAppearance(vId, typeDescr, health, isCrewActive, isTurretDetached, outfitCD, forceReloadingFromCache=False):
    newInfo = _VehicleInfo(typeDescr, health, isCrewActive, isTurretDetached, outfitCD)
    return _g_cache.createAppearance(vId, newInfo, forceReloadingFromCache)


def getAppearance(vId, resourceRefs):
    return _g_cache.getAppearance(vId, resourceRefs)


def cacheApperance(vID, info):
    _g_cache.cacheApperance(vID, info)


def dCacheStatus():
    if _ENABLE_CACHE_TRACKER:
        cache = _g_cache.cache
        LOG_DEBUG('VehicleID cachedTime   Activated  VehicleType')
        for vId, appearance in cache.iteritems():
            cachedTime = d_cacheInfo.get(vId, None)
            LOG_DEBUG('{0}     {1}    {2}   {3}'.format(vId, cachedTime, appearance[0].activated, appearance[0].typeDescriptor.type.name))

    return
