# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/appearance_cache.py
import weakref
from collections import namedtuple
import BigWorld
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_DEBUG, LOG_WARNING
from items import vehicles
from gui.shared.utils.MethodsRules import MethodsRules
from vehicle_systems.CompoundAppearance import CompoundAppearance
from vehicle_systems.stricted_loading import loadingPriority, makeCallbackWeak
_ENABLE_CACHE_TRACKER = False
_ENABLE_PRECACHE = True
_VehicleInfo = namedtuple('_VehicleInfo', ['typeDescr',
 'health',
 'isCrewActive',
 'isTurretDetached',
 'outfitCD'])
_AssemblerData = namedtuple('_AssemblerData', ['appearance', 'info', 'prereqsNames'])

def isPrecacheEnabled():
    return _ENABLE_PRECACHE


class _AppearanceCache(MethodsRules):
    __slots__ = ('__arena', '__appearanceCache', '__assemblersCache', '__spaceLoaded', '__wholeVehResources', '__dCacheInfo', '__currentLoadingVehicles')

    @property
    def cache(self):
        return self.__appearanceCache

    @property
    def dCacheInfo(self):
        return self.__dCacheInfo

    def __init__(self):
        super(_AppearanceCache, self).__init__()
        self.__arena = None
        self.__appearanceCache = {}
        self.__assemblersCache = {}
        self.__dCacheInfo = {}
        self.__spaceLoaded = False
        self.__wholeVehResources = None
        self.__currentLoadingVehicles = {}
        return

    def isArenaSet(self):
        return self.__arena is not None

    def nextLoadingID(self, vehicleID):
        nextID = self.__currentLoadingVehicles.get(vehicleID, 0) + 1
        self.__currentLoadingVehicles[vehicleID] = nextID
        return nextID

    def currentLoadingID(self, vehicleID):
        return self.__currentLoadingVehicles.get(vehicleID, 0)

    @MethodsRules.delayable()
    def setArena(self, arena):
        self.__arena = weakref.proxy(arena)
        self.__arena.onNewVehicleListReceived += self.onVehicleListReceived
        self.__arena.onVehicleAdded += self.onVehicleAddedUpdate
        self.__arena.onVehicleUpdated += self.onVehicleAddedUpdate
        if getattr(self.__arena.componentSystem, 'playerDataComponent', None):
            self.__arena.componentSystem.playerDataComponent.onPlayerGroupsUpdated += self.__onPlayerGroupsUpdated
        return

    def delArena(self):
        if not self.isArenaSet():
            return
        else:
            if getattr(self.__arena.componentSystem, 'playerDataComponent', None):
                self.__arena.componentSystem.playerDataComponent.onPlayerGroupsUpdated -= self.__onPlayerGroupsUpdated
            self.__arena.onVehicleAdded -= self.onVehicleAddedUpdate
            self.__arena.onVehicleUpdated -= self.onVehicleAddedUpdate
            self.__arena.onNewVehicleListReceived -= self.onVehicleListReceived
            self.__arena = None
            return

    def clear(self):
        super(_AppearanceCache, self).clear()
        self.delArena()
        for _, appearance in self.__appearanceCache.iteritems():
            appearance[0].destroy()

        self.__dCacheInfo.clear()
        self.__appearanceCache.clear()
        self.__assemblersCache.clear()
        self.__wholeVehResources = None
        self.__spaceLoaded = False
        self.__currentLoadingVehicles.clear()
        return

    def onVehicleListReceived(self):
        if not self.__spaceLoaded or not _ENABLE_PRECACHE:
            return
        self.__precacheVehicle(self.__arena.vehicles)

    def onVehicleAddedUpdate(self, vId):
        if _ENABLE_PRECACHE:
            vInfo = self.__arena.vehicles[vId]
            self.__precacheVehicle({vId: vInfo})

    @MethodsRules.delayable('setArena')
    def onSpaceLoaded(self):
        self.__spaceLoaded = True
        if _ENABLE_PRECACHE:
            self.__precacheVehicle(self.__arena.vehicles)
        if self.__arena.guiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
            brprereqs = set()
            cachedDescs = set()
            for veh in self.__arena.vehicles.values():
                vDesc = veh['vehicleType']
                if vDesc.name in cachedDescs:
                    continue
                cachedDescs.add(vDesc.name)
                brprereqs.update(self.__getWholeVehModels(vDesc))

            BigWorld.loadResourceListBG(list(brprereqs), makeCallbackWeak(_wholeVehicleResourcesLoaded, brprereqs))

    def __getWholeVehModels(self, vDesc):
        nationID, vehicleTypeID = vehicles.g_list.getIDsByName(vDesc.name)
        vType = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
        brprereqs = set(vDesc.prerequisites(True))
        bspModels = set()
        index = 0
        for chassie in vType.chassis:
            brprereqs.add(chassie.models.undamaged)
            splineDesc = chassie.splineDesc
            if splineDesc is not None:
                brprereqs.add(splineDesc.segmentModelLeft())
                brprereqs.add(splineDesc.segmentModelRight())
                brprereqs.add(splineDesc.segment2ModelLeft())
                brprereqs.add(splineDesc.segment2ModelRight())
            bspModels.add((index, chassie.hitTester.bspModelName))
            index = index + 1

        for hull in vType.hulls:
            brprereqs.add(hull.models.undamaged)
            bspModels.add((index, hull.hitTester.bspModelName))
            index = index + 1

        for turrets in vType.turrets:
            for turret in turrets:
                brprereqs.add(turret.models.undamaged)
                bspModels.add((index, turret.hitTester.bspModelName))
                index = index + 1
                for gun in turret.guns:
                    brprereqs.add(gun.models.undamaged)
                    bspModels.add((index, gun.hitTester.bspModelName))
                    index = index + 1

        brprereqs.add(BigWorld.CollisionAssembler(tuple(bspModels), BigWorld.player().spaceID))
        return brprereqs

    def saveWholeVehicleResources(self, resources):
        self.__wholeVehResources = resources

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

    def removeAppearance(self, vId):
        if vId in self.__appearanceCache:
            self.__appearanceCache[vId][0].destroy()
            del self.__appearanceCache[vId]
            if _ENABLE_CACHE_TRACKER:
                LOG_DEBUG('Appearance cache. Removing appearance vID = {0}'.format(vId))

    def createAppearance(self, vId, vInfo, forceReloadingFromCache):
        appearanceInfo = self.__appearanceCache.get(vId, None)
        appearance = None
        prereqsNames = []
        if appearanceInfo is None or not self.__validate(appearanceInfo[1], vInfo) or not self.__validateAppearanceWithInfo(appearanceInfo[0], vInfo) or forceReloadingFromCache:
            assemblerData = self.__assemblersCache.get(vId, None)
            if assemblerData is None or not self.__validate(assemblerData.info, vInfo) or forceReloadingFromCache:
                prereqsNames = self.__cacheApperance(vId, vInfo)
            else:
                prereqsNames = assemblerData.prereqsNames
        else:
            appearance, _ = appearanceInfo
        return (appearance, prereqsNames)

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
            appearance = assemblerData.appearance
            if _ENABLE_CACHE_TRACKER:
                LOG_DEBUG('Appearance cache. Constructed vID = {0}'.format(vId))
            if not resourceRefs.has_key(assemblerData.info.typeDescr.name):
                LOG_WARNING('Loaded appearance is not latest requested appearance, construction of the appearance is skipped ', assemblerData.info.typeDescr.name, resourceRefs)
                return
            assemblerData.info.typeDescr.keepPrereqs(resourceRefs)
            appearance.construct(BigWorld.player().playerVehicleID == vId, resourceRefs)
            oldAppearance = self.__appearanceCache.get(vId, None)
            apperanceOwner = None
            if oldAppearance is not None:
                apperanceOwner = oldAppearance[0].getVehicle()
                if apperanceOwner is not None:
                    apperanceOwner.stopVisual()
                oldAppearance[0].destroy()
                self.__appearanceCache[vId] = None
                if _ENABLE_CACHE_TRACKER:
                    LOG_DEBUG('Appearance cache. Deleting old appearance vID = {0}'.format(vId))
            self.__appearanceCache[vId] = (appearance, assemblerData.info)
            if apperanceOwner is not None:
                apperanceOwner.startVisual()
            del self.__assemblersCache[vId]
            if _ENABLE_CACHE_TRACKER:
                self.__dCacheInfo[vId] = BigWorld.time()
            return appearance

    def __cacheApperance(self, vId, info):
        appearance = CompoundAppearance()
        prereqs = appearance.prerequisites(info.typeDescr, vId, info.health, info.isCrewActive, info.isTurretDetached, info.outfitCD)
        if vId in self.__assemblersCache:
            assemblerData = self.__assemblersCache.get(vId, None)
            if assemblerData is not None:
                oldAppearance = assemblerData.appearance
                LOG_WARNING('The latest resources for the vehicle are not loaded yet, deleting old appearance and creating new one %s %s' % (info.typeDescr.name, assemblerData.info.typeDescr))
                del oldAppearance
            del self.__assemblersCache[vId]
        self.__assemblersCache[vId] = _AssemblerData(appearance, info, prereqs)
        if self.__spaceLoaded:
            _loadResource(prereqs, vId)
        return prereqs

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
                vehicleInfos = {vId:self.__arena.vehicles[vId] for vId in vIds}
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


_g_cache = _AppearanceCache()

def _loadResource(prereqs, vId):
    BigWorld.loadResourceListBG(prereqs, makeCallbackWeak(_resourceLoaded, prereqs, vId, _g_cache.nextLoadingID(vId)), loadingPriority(vId))


def _resourceLoaded(resNames, vId, loadedResourceId, resourceRefs):
    if not _g_cache.isArenaSet():
        return
    if _g_cache.currentLoadingID(vId) != loadedResourceId:
        return
    failedRefs = resourceRefs.failedIDs
    for resName in resNames:
        if resName in failedRefs:
            LOG_WARNING('Resource is not found', resName)

    _g_cache.constructAppearance(vId, resourceRefs)


def _wholeVehicleResourcesLoaded(resNames, resourceRefs):
    if not _g_cache.isArenaSet():
        return
    _g_cache.saveWholeVehicleResources(resourceRefs)


def init(clientArena):
    _g_cache.setArena(clientArena)


def destroy():
    _g_cache.clear()


def onSpaceLoaded():
    _g_cache.onSpaceLoaded()


def createAppearance(vId, typeDescr, health, isCrewActive, isTurretDetached, outfitCD, forceReloadingFromCache=False):
    newInfo = _VehicleInfo(typeDescr, health, isCrewActive, isTurretDetached, outfitCD)
    return _g_cache.createAppearance(vId, newInfo, forceReloadingFromCache)


def getAppearance(vId, resourceRefs):
    return _g_cache.getAppearance(vId, resourceRefs)


def cacheApperance(vID, info):
    _g_cache.cacheApperance(vID, info)


def removeAppearance(vID):
    _g_cache.removeAppearance(vID)


def dCacheStatus():
    if _ENABLE_CACHE_TRACKER:
        cache = _g_cache.cache
        LOG_DEBUG('VehicleID cachedTime   Activated  VehicleType')
        for vId, appearance in cache.iteritems():
            cachedTime = _g_cache.dCacheInfo.get(vId, None)
            LOG_DEBUG('{0}     {1}    {2}   {3}'.format(vId, cachedTime, appearance[0].activated, appearance[0].typeDescriptor.type.name))

    return
