# Embedded file name: scripts/client/AreaDestructibles.py
import BigWorld
from debug_utils import *
import Math
import math
import random
import ResMgr
from DestructiblesCache import *
from time import clock
from functools import partial
from constants import DESTRUCTIBLE_MATKIND
from helpers import isPlayerAccount
import re
import physics_shared
import FMOD
g_cache = None
g_destructiblesManager = None
g_destructiblesAnimator = None
MODULE_DEPENDENCY_HIDING_DELAY_CONSTANT = 0.25
MODULE_DEPENDENCY_HIDING_DELAY = MODULE_DEPENDENCY_HIDING_DELAY_CONSTANT
DESTRUCTIBLE_HIDING_DELAY_CONSTANT = 0.2
DESTRUCTIBLE_HIDING_DELAY = DESTRUCTIBLE_HIDING_DELAY_CONSTANT
_TREE_EFFECTS_SCALE_RATIO = 0.7
_MAX_PITCH_TO_CHECK_TERRAIN = math.radians(87)
_SHOT_EXPLOSION_SYNC_TIMEOUT = 0.11

def init():
    global g_destructiblesManager
    global g_cache
    global g_destructiblesAnimator
    g_cache = ClientDestructiblesCache()
    if BigWorld.wg_getDrawModelSelector() == 0:
        g_destructiblesManager = DestructiblesManagerStaticModel()
        g_destructiblesAnimator = _DestructiblesStaticModelAnimator()
    else:
        g_destructiblesManager = DestructiblesManager()
        g_destructiblesAnimator = _DestructiblesAnimator()


def clear():
    g_destructiblesManager.clear()
    g_destructiblesAnimator.clear()


class ClientDestructiblesCache(DestructiblesCache):

    def getDestructibleDesc(self, spaceID, chunkID, destrIndex):
        filename = BigWorld.wg_getDestructibleFilename(spaceID, chunkID, destrIndex)
        return self.getDescByFilename(filename)


class DestructiblesManager():

    def __init__(self):
        self.__spaceID = None
        self.__loadedChunkIDs = {}
        self.__savedLoadedChunkIDs = None
        self.__savedSpaceID = None
        self.__destructiblesWaitDestroy = {}
        self.__effectsResourceRefs = {}
        self.__structuresEffects = {}
        self.__lifetimeEffects = {}
        self.forceNoAnimation = False
        self.__damagedModules = set()
        self.__destrInitialMatrices = {}
        self.__ctrls = {}
        self.__destroyCallbacks = {}
        self.__projectileExplosions = []
        self.__explodedDestructibles = []
        return

    def clear(self):
        self.__spaceID = None
        self.__loadedChunkIDs = {}
        self.__destructiblesWaitDestroy = {}
        self.__effectsResourceRefs = {}
        self.__structuresEffects = {}
        self.__lifetimeEffects = {}
        self.__damagedModules = set()
        self.__destrInitialMatrices = {}
        self.__ctrls = {}
        self.__destroyCallbacks = {}
        self.__projectileExplosions = []
        self.__explodedDestructibles = []
        return

    def startSpace(self, spaceID):
        self.clear()
        self.__spaceID = spaceID

    def getSpaceID(self):
        return self.__spaceID

    def getController(self, chunkID):
        return self.__ctrls.get(chunkID)

    def onChunkLoad(self, chunkID, numDestructibles):
        if self.__spaceID is None:
            LOG_ERROR('Notification about chunk load came when no space started')
            return
        else:
            if numDestructibles > 256:
                if not isPlayerAccount():
                    self.__logErrorTooMuchDestructibles(chunkID)
            destrFilenames = BigWorld.wg_getChunkDestrFilenames(self.__spaceID, chunkID)
            if destrFilenames is None:
                LOG_ERROR("Can't get destructibles filenames list for space %s, chunk %s" % (self.__spaceID, chunkID))
                return
            for destrIndex in xrange(numDestructibles):
                self.__setDestructibleInitialState(chunkID, destrIndex)

            self.__loadedChunkIDs[chunkID] = numDestructibles
            chunkEntries = self.__destructiblesWaitDestroy.get(chunkID)
            if chunkEntries is not None:
                for dmgType, destrData, isNeedAnimation in chunkEntries:
                    self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation)

                del self.__destructiblesWaitDestroy[chunkID]
            consideredNames = set()
            prereqs = set()
            for fname in destrFilenames:
                if fname not in consideredNames:
                    consideredNames.add(fname)
                    desc = g_cache.getDescByFilename(fname)
                    if desc is not None:
                        effLists = _extractEffectLists(desc)
                        for effList in effLists:
                            prereqs.update(effList.prerequisites())

            if prereqs:
                BigWorld.loadResourceListBG(list(prereqs), partial(self.__onResourceLoad, self.__spaceID, chunkID))
            return

    def onChunkLoose(self, chunkID):
        if self.__loadedChunkIDs.has_key(chunkID):
            del self.__loadedChunkIDs[chunkID]
        if self.__effectsResourceRefs.has_key(chunkID):
            del self.__effectsResourceRefs[chunkID]

    def isChunkLoaded(self, chunkID):
        return self.__loadedChunkIDs.has_key(chunkID)

    def onProjectileExploded(self, hitParams, damagedDestructibles):
        self.__reduceExplosionCacheByTimeout()
        explosionInfo = [hitParams, True]
        explDestrs = self.__explodedDestructibles
        gotDestrs = False
        restDamagedDestructibles = []
        for chunkID, itemIndex, matKind in damagedDestructibles:
            found = False
            for destr in explDestrs:
                time, itemInfo = destr
                chunkID_, itemIndex_, matKind_, dmgType, destrData = itemInfo
                if chunkID_ == chunkID and itemIndex_ == itemIndex and (dmgType == DESTR_TYPE_FRAGILE or matKind_ == matKind):
                    self.__destroyDestructible(chunkID, dmgType, destrData, True, explosionInfo)
                    explDestrs.remove(destr)
                    found = True
                    gotDestrs = True
                    break

            if not found:
                restDamagedDestructibles.append((chunkID, itemIndex, matKind))

        if restDamagedDestructibles:
            newExpl = (BigWorld.time(), explosionInfo, restDamagedDestructibles)
            self.__projectileExplosions.append(newExpl)
        if not gotDestrs:
            BigWorld.callback(_SHOT_EXPLOSION_SYNC_TIMEOUT + DESTRUCTIBLE_HIDING_DELAY, partial(self.__delayedHavokExplosion, self.__spaceID, explosionInfo))

    def orderDestructibleDestroy(self, chunkID, dmgType, destrData, isNeedAnimation, syncWithProjectile = False):
        if self.forceNoAnimation:
            isNeedAnimation = False
        if self.__loadedChunkIDs.has_key(chunkID):
            if isNeedAnimation and syncWithProjectile:
                if dmgType == DESTR_TYPE_FRAGILE:
                    itemIndex, _ = decodeFragile(destrData)
                    matKind = 0
                elif dmgType == DESTR_TYPE_STRUCTURE:
                    itemIndex, matKind, _ = decodeDestructibleModule(destrData)
                else:
                    LOG_CODEPOINT_WARNING()
                    return
                self.__reduceExplosionCacheByTimeout()
                for expl in reversed(self.__projectileExplosions):
                    time, explInfo, damagedDestrs = expl
                    for destr in damagedDestrs:
                        chunkID_, itemIndex_, matKind_ = destr
                        if chunkID == chunkID_ and itemIndex == itemIndex_ and (dmgType == DESTR_TYPE_FRAGILE or matKind == matKind_):
                            self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation, explInfo)
                            damagedDestrs.remove(destr)
                            if not damagedDestrs:
                                self.__projectileExplosions.remove(expl)
                            return

                itemInfo = (chunkID,
                 itemIndex,
                 matKind,
                 dmgType,
                 destrData)
                self.__explodedDestructibles.append((BigWorld.time(), itemInfo))
                BigWorld.callback(_SHOT_EXPLOSION_SYNC_TIMEOUT + 0.01, self.__reduceExplosionCacheByTimeout)
            else:
                self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation)
        else:
            entry = (dmgType, destrData, isNeedAnimation)
            self.__destructiblesWaitDestroy.setdefault(chunkID, []).append(entry)

    def onBeforeReplayTimeWarp(self, rewind):
        for functor, callbackID in self.__destroyCallbacks.iteritems():
            if not rewind:
                functor(False)
            BigWorld.cancelCallback(callbackID)

        self.__destroyCallbacks.clear()
        if rewind:
            self.__savedLoadedChunkIDs = self.__loadedChunkIDs
            self.__savedSpaceID = self.__spaceID
            for (chunkID, destrIndex), m in self.__destrInitialMatrices.iteritems():
                BigWorld.wg_setDestructibleMatrix(self.__spaceID, chunkID, destrIndex, m, 1.0)

    def onAfterReplayTimeWarp(self):
        if self.__savedLoadedChunkIDs is None:
            return
        else:
            g_destructiblesAnimator.clear()
            self.__spaceID = self.__savedSpaceID
            for chunkID, numDestructibles in self.__savedLoadedChunkIDs.iteritems():
                self.onChunkLoad(chunkID, numDestructibles)

            self.__savedSpaceID = None
            self.__savedLoadedChunkIDs = None
            return

    def _addController(self, chunkID, ctrl):
        self.__ctrls[chunkID] = ctrl

    def _delController(self, chunkID):
        if self.__ctrls.has_key(chunkID):
            del self.__ctrls[chunkID]

    def __reduceExplosionCacheByTimeout(self):
        currTime = BigWorld.time()
        newExplCache = []
        for expl in self.__projectileExplosions:
            time, explInfo, _ = expl
            if currTime - time < _SHOT_EXPLOSION_SYNC_TIMEOUT:
                newExplCache.append(expl)

        self.__projectileExplosions = newExplCache
        newItemCache = []
        for destr in self.__explodedDestructibles:
            time, itemInfo = destr
            if currTime - time < _SHOT_EXPLOSION_SYNC_TIMEOUT:
                newItemCache.append(destr)
            else:
                chunkID, _, _, dmgType, destrData = itemInfo
                self.__destroyDestructible(chunkID, dmgType, destrData, True)

        self.__explodedDestructibles = newItemCache

    def __logErrorTooMuchDestructibles(self, chunkID):
        x, y = chunkIndexesFromChunkID(chunkID)
        player = BigWorld.player()
        if player is None:
            LOG_ERROR('Number of destructibles more than 256, chunk: %i %i' % (x, y))
        else:
            if x >= 0:
                xh = hex(x)[2:]
                xh = '0000'[:4 - len(xh)] + xh
            else:
                xh = hex(65535 + x + 1)[2:]
            if y >= 0:
                yh = hex(y)[2:]
                yh = '0000'[:4 - len(yh)] + yh
            else:
                yh = hex(65535 + y + 1)[2:]
            arenaTypeID = player.arenaTypeID
            LOG_ERROR('Number of destructibles more than 256, arena: %s, chunk: %s' % (arenaTypeID, xh + yh + 'o'))
        return

    def __onResourceLoad(self, spaceID, chunkID, resourceRefs):
        if spaceID == self.__spaceID:
            self.__effectsResourceRefs[chunkID] = resourceRefs

    def __destroyDestructible(self, chunkID, dmgType, destData, isNeedAnimation, explosionInfo = None):
        if self.forceNoAnimation:
            isNeedAnimation = False
        if dmgType == DESTR_TYPE_FALLING_ATOM:
            destrIndex, fallDirYaw, fallSpeed = decodeFallenColumn(destData)
            pitchConstr, collisionFlags = BigWorld.wg_getDestructibleFallPitchConstr(self.__spaceID, chunkID, destrIndex, fallDirYaw)
            if pitchConstr is None:
                pitchConstr = math.pi / 2.0
            self.__dropDestructible(chunkID, destrIndex, fallDirYaw, pitchConstr, fallSpeed, isNeedAnimation, collisionFlags)
        if dmgType == DESTR_TYPE_TREE:
            destrIndex, fallDirYaw, pitchConstr, fallSpeed = decodeFallenTree(destData)
            _, collisionFlags = BigWorld.wg_getDestructibleFallPitchConstr(self.__spaceID, chunkID, destrIndex, fallDirYaw)
            self.__dropDestructible(chunkID, destrIndex, fallDirYaw, pitchConstr, fallSpeed, isNeedAnimation, collisionFlags)
            if FMOD.enabled:
                FMOD.lightSoundRemove(self.__spaceID, chunkID, destrIndex)
        elif dmgType == DESTR_TYPE_FRAGILE:
            destrIndex, isShotDamage = decodeFragile(destData)
            self.__destroyFragile(chunkID, destrIndex, isNeedAnimation, isShotDamage, explosionInfo)
            if FMOD.enabled:
                FMOD.lightSoundRemove(self.__spaceID, chunkID, destrIndex)
        elif dmgType == DESTR_TYPE_STRUCTURE:
            destrIndex, matKind, isShotDamage = decodeDestructibleModule(destData)
            self.__destroyModule(chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage, explosionInfo)
        return

    def __setDestructibleInitialState(self, chunkID, destrIndex):
        filename = BigWorld.wg_getDestructibleFilename(self.__spaceID, chunkID, destrIndex)
        if filename is None:
            return
        else:
            filename = re.sub('/lod./', '/lod0/', filename)
            desc = g_cache.getDescByFilename(filename)
            if desc is None:
                _getOrCreateStaticHavokFashion(self.__spaceID, chunkID, destrIndex)
                return
            type = desc['type']
            if type == DESTR_TYPE_FALLING_ATOM:
                fashion = _getOrCreateFashion(self.__spaceID, chunkID, destrIndex, True)
                fashion.isDestroyed = False
            if type == DESTR_TYPE_FRAGILE or type == DESTR_TYPE_STRUCTURE:
                fashion = _getOrCreateFashion(self.__spaceID, chunkID, destrIndex, True)
                fashion.isDestroyed = False
            if type == DESTR_TYPE_STRUCTURE:
                for moduleKind, moduleDesc in desc['modules'].iteritems():
                    self.__startLifetimeEffect(chunkID, destrIndex, moduleKind, moduleDesc, desc['filename'])

            else:
                self.__startLifetimeEffect(chunkID, destrIndex, 0, desc, desc['filename'])
            return

    def __destroyFragile(self, chunkID, destrIndex, isNeedAnimation, isShotDamage, explosionInfo = None):
        self.__stopLifetimeEffect(chunkID, destrIndex, 0)
        isHavokVisible = self.__havokWillSetDestructibleState(self.__spaceID, chunkID, destrIndex, True, explosionInfo)
        if isNeedAnimation:
            functor = partial(self.__setDestructibleState, self.__spaceID, chunkID, destrIndex, True, explosionInfo)
            callbackID = BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, functor)
            self.__destroyCallbacks[functor] = callbackID
        else:
            self.__setDestructibleState(self.__spaceID, chunkID, destrIndex, True, explosionInfo, False)
        desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
        if desc is None:
            _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
            return
        else:
            if isNeedAnimation:
                self.__launchEffect(chunkID, destrIndex, desc, 'decayEffect', desc['filename'], isHavokVisible)
                if isShotDamage and desc.get('hitEffect'):
                    coreEffectType = 'hitEffect'
                else:
                    coreEffectType = 'effect'
                self.__launchEffect(chunkID, destrIndex, desc, coreEffectType, desc['filename'], isHavokVisible)
            return

    def __destroyModule(self, chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage, explosionInfo = None):
        if self.__isModuleDamaged(chunkID, destrIndex, matKind):
            return
        else:
            self.__stopLifetimeEffect(chunkID, destrIndex, matKind)
            desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
            if desc is None:
                _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
                return
            moduleDesc = desc['modules'][matKind]
            destroyedMat = moduleDesc['destroyedMat']
            destroyDepends = desc['destroyDepends'].get(matKind, [])
            dependKinds = list(destroyDepends)
            for kind in destroyDepends:
                dependModuleDesc = desc['modules'][kind]
                dependKinds.append(dependModuleDesc['destroyedMat'])

            isHavokVisible = self.__havokWillSetDestructibleMaterialsVisible(self.__spaceID, chunkID, destrIndex, [destroyedMat], [matKind] + dependKinds, explosionInfo)
            moduleDependencyHidingDelay = MODULE_DEPENDENCY_HIDING_DELAY if isHavokVisible else 0.0
            if isNeedAnimation:
                functor = partial(self.__setDestructibleMaterialsVisible, self.__spaceID, chunkID, destrIndex, [destroyedMat], [matKind], explosionInfo)
                callbackID = BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, functor)
                self.__destroyCallbacks[functor] = callbackID
                functor = partial(self.__setDestructibleMaterialsVisible, self.__spaceID, chunkID, destrIndex, [], dependKinds, explosionInfo)
                callbackID = BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY + moduleDependencyHidingDelay, functor)
                self.__destroyCallbacks[functor] = callbackID
            else:
                self.__setDestructibleMaterialsVisible(self.__spaceID, chunkID, destrIndex, [destroyedMat], [matKind] + dependKinds, explosionInfo, False)
            if isShotDamage:
                unregisterCallback = partial(self.__unregisterModuleEffect, self.__spaceID, chunkID, destrIndex, matKind)
                decayEffectID = self.__launchEffect(chunkID, destrIndex, moduleDesc, 'decayEffect', desc['filename'], isHavokVisible, unregisterCallback)
                if decayEffectID is not None:
                    self.__registerModuleEffect(chunkID, destrIndex, matKind, decayEffectID)
            damagedDepands = []
            undamagedDepands = []
            for kind in destroyDepends:
                if self.__isModuleDamaged(chunkID, destrIndex, kind):
                    damagedDepands.append(kind)
                else:
                    undamagedDepands.append(kind)

            for kind in damagedDepands:
                staticEffectID = self.__getModuleEffectID(chunkID, destrIndex, kind)
                if staticEffectID is not None:
                    self.__unregisterModuleEffect(self.__spaceID, chunkID, destrIndex, kind)
                    player = BigWorld.player()
                    if player is not None and not isPlayerAccount():
                        player.terrainEffects.stop(staticEffectID)

            if isNeedAnimation:
                if isShotDamage:
                    coreEffectType = 'hitEffect'
                else:
                    coreEffectType = 'ramEffect'
                self.__launchEffect(chunkID, destrIndex, moduleDesc, coreEffectType, desc['filename'], isHavokVisible)
                for kind in undamagedDepands:
                    self.__launchEffect(chunkID, destrIndex, desc['modules'][kind], 'ramEffect', desc['filename'], isHavokVisible)

            damagedKinds = [matKind]
            damagedKinds += destroyDepends
            self.__registerDamagedModules(chunkID, destrIndex, damagedKinds)
            allUndamagedKinds = self.__getUndamagedKinds(chunkID, destrIndex)
            allDamagedKinds = self.__getDamagedKinds(chunkID, destrIndex)
            if len(allUndamagedKinds) == 2 and len(allDamagedKinds) >= 6:
                for kind in allUndamagedKinds:
                    depends = desc['destroyDepends'].get(kind, [])
                    for dependKind in depends:
                        if dependKind in allUndamagedKinds:
                            BigWorld.callback(moduleDependencyHidingDelay, partial(self.__destroyModule, chunkID, destrIndex, dependKind, isNeedAnimation, False, explosionInfo))
                            return

            if len(allUndamagedKinds) == 1 and len(allDamagedKinds) >= 7:
                kind = allUndamagedKinds[0]
                depends = desc['destroyDepends'].get(kind, [])
                kindsToHide = []
                for dependKind in depends:
                    dependModuleDesc = desc['modules'][dependKind]
                    kindsToHide.append(dependModuleDesc['destroyedMat'])
                    self.__stopLifetimeEffect(chunkID, destrIndex, kind)
                    staticEffectID = self.__getModuleEffectID(chunkID, destrIndex, kind)
                    if staticEffectID is not None:
                        self.__unregisterModuleEffect(self.__spaceID, chunkID, destrIndex, kind)
                        player = BigWorld.player()
                        if player is not None and not isPlayerAccount():
                            player.terrainEffects.stop(staticEffectID)

                if isNeedAnimation:
                    functor = partial(self.__setDestructibleMaterialsVisible, self.__spaceID, chunkID, destrIndex, [], kindsToHide)
                    callbackID = BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY + moduleDependencyHidingDelay, functor)
                    self.__destroyCallbacks[functor] = callbackID
                else:
                    self.__setDestructibleMaterialsVisible(self.__spaceID, chunkID, destrIndex, [], kindsToHide, False)
            return

    def __getDamagedKinds(self, chunkID, destrIndex):
        desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
        if desc is None:
            _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
            return
        else:
            damagedKinds = []
            for kind in desc['modules'].iterkeys():
                if self.__isModuleDamaged(chunkID, destrIndex, kind):
                    damagedKinds.append(kind)

            return damagedKinds

    def __getUndamagedKinds(self, chunkID, destrIndex):
        desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
        if desc is None:
            _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
            return
        else:
            undamagedKinds = []
            for kind in desc['modules'].iterkeys():
                if not self.__isModuleDamaged(chunkID, destrIndex, kind):
                    undamagedKinds.append(kind)

            return undamagedKinds

    def __launchEffect(self, chunkID, destrIndex, desc, effectType, modelFile, isHavokVisible, callbackOnStop = None):
        effectVars = desc.get(effectType)
        if effectVars is None:
            return
        else:
            type = desc.get('type')
            if type == DESTR_TYPE_TREE or type == DESTR_TYPE_FALLING_ATOM:
                chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
                destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
                dir = destrMatrix.applyVector((0, 0, 1))
                pos = chunkMatrix.translation + destrMatrix.translation
                if type == DESTR_TYPE_TREE:
                    treeScale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
                    scale = 1.0 + (treeScale - 1.0) * _TREE_EFFECTS_SCALE_RATIO
                else:
                    scale = desc['effectScale']
            else:
                hpMatrix = BigWorld.wg_getHardPointMatrix(self.__spaceID, chunkID, destrIndex, desc['effectHP'])
                if hpMatrix is None:
                    LOG_ERROR("Can't find hardpoint %s in model %s" % (desc['effectHP'], modelFile))
                    return
                dir = hpMatrix.applyVector((0, 0, 1))
                pos = hpMatrix.translation
                scale = desc['effectScale']
            player = BigWorld.player()
            if player is None or isPlayerAccount():
                return
            effectStuff = random.choice(effectVars)
            effectID = player.terrainEffects.addNew(pos, effectStuff.effectsList, effectStuff.keyPoints, callbackOnStop, dir=dir, scale=scale, havokEnabled=isHavokVisible)
            return effectID

    def __startLifetimeEffect(self, chunkID, destrIndex, moduleKind, desc, modelFile):
        chance = desc.get('lifetimeEffectChance')
        if chance is None or random.random() > chance:
            return
        else:
            lifetimeEffectID = self.__launchEffect(chunkID, destrIndex, desc, 'lifetimeEffect', modelFile, False)
            if lifetimeEffectID is not None:
                code = _encodeModule(chunkID, destrIndex, moduleKind)
                self.__lifetimeEffects[code] = lifetimeEffectID
            return

    def __stopLifetimeEffect(self, chunkID, destrIndex, moduleKind):
        code = _encodeModule(chunkID, destrIndex, moduleKind)
        lifetimeEffectID = self.__lifetimeEffects.get(code)
        if lifetimeEffectID is None:
            return
        else:
            del self.__lifetimeEffects[code]
            player = BigWorld.player()
            if player is not None and not isPlayerAccount():
                player.terrainEffects.stop(lifetimeEffectID)
            return

    def __registerDamagedModules(self, chunkID, structureIndex, moduleKinds):
        for kind in moduleKinds:
            code = _encodeModule(chunkID, structureIndex, kind)
            self.__damagedModules.add(code)

    def __isModuleDamaged(self, chunkID, structureIndex, moduleKind):
        code = _encodeModule(chunkID, structureIndex, moduleKind)
        return code in self.__damagedModules

    def __getModuleEffectID(self, chunkID, structureIndex, moduleKind):
        code = _encodeModule(chunkID, structureIndex, moduleKind)
        return self.__structuresEffects.get(code)

    def __registerModuleEffect(self, chunkID, structureIndex, moduleKind, effectID):
        code = _encodeModule(chunkID, structureIndex, moduleKind)
        self.__structuresEffects[code] = effectID

    def __unregisterModuleEffect(self, spaceID, chunkID, structureIndex, moduleKind):
        if spaceID != self.__spaceID:
            return
        code = _encodeModule(chunkID, structureIndex, moduleKind)
        if self.__structuresEffects.has_key(code):
            del self.__structuresEffects[code]

    def __havokWillSetDestructibleMaterialsVisible(self, spaceID, chunkID, destrIndex, kindsToShow, kindsToHide, explosionInfo = None, delCallback = True):
        fashion = _getOrCreateFashion(spaceID, chunkID, destrIndex, True)
        for kind in kindsToHide:
            if fashion.havokDestructionVisible(kind):
                return True

        return False

    def __setDestructibleMaterialsVisible(self, spaceID, chunkID, destrIndex, kindsToShow, kindsToHide, explosionInfo = None, delCallback = True):
        if spaceID != self.__spaceID:
            return
        else:
            fashion = _getOrCreateFashion(spaceID, chunkID, destrIndex, True)
            for kind in kindsToShow:
                fashion.setMaterialKindVisible(kind, True)
                if kind >= DESTRUCTIBLE_MATKIND.DAMAGED_MIN and kind <= DESTRUCTIBLE_MATKIND.DAMAGED_MAX:
                    fashion.setEnableDrawMergedModel(False)

            if explosionInfo is not None:
                hitParams, createExplosion = explosionInfo
                endPoint, hitDir, shellVelocity, shellMass, splashRadius, splashStrength = hitParams
                for kind in kindsToHide:
                    fashion.setMaterialKindVisible(kind, False)
                    fashion.havokDestroyMaterialExp(kind, endPoint, hitDir, shellVelocity, shellMass)

                if createExplosion:
                    BigWorld.wg_havokExplosion(endPoint, splashStrength, splashRadius)
                    explosionInfo[1] = False
            else:
                for kind in kindsToHide:
                    fashion.setMaterialKindVisible(kind, False)
                    fashion.havokDestroyMaterial(kind)

            for kind in kindsToHide:
                if kind >= DESTRUCTIBLE_MATKIND.NORMAL_MIN and kind <= DESTRUCTIBLE_MATKIND.NORMAL_MAX:
                    fashion.setEnableDrawMergedModel(False)

            if delCallback:
                for functor in self.__destroyCallbacks:
                    args = functor.args
                    if args[1] == chunkID and args[2] == destrIndex and args[3] == kindsToShow and args[4] == kindsToHide:
                        del self.__destroyCallbacks[functor]
                        break

            return

    def __havokWillSetDestructibleState(self, spaceID, chunkID, destrIndex, isDestroyed, explosionInfo = None):
        fashion = _getOrCreateFashion(spaceID, chunkID, destrIndex, True)
        if isDestroyed and explosionInfo is not None:
            if fashion.havokDestructionVisible(0):
                return True
        return False

    def __setDestructibleState(self, spaceID, chunkID, destrIndex, isDestroyed, explosionInfo = None, delCallback = True):
        if spaceID != self.__spaceID:
            return
        else:
            fashion = _getOrCreateFashion(spaceID, chunkID, destrIndex, True)
            if isDestroyed and explosionInfo is not None:
                hitParams, createExplosion = explosionInfo
                endPoint, hitDir, shellVelocity, shellMass, splashRadius, splashStrength = hitParams
                fashion.havokDestroyAllExp(endPoint, hitDir, shellVelocity, shellMass)
                if createExplosion:
                    BigWorld.wg_havokExplosion(endPoint, splashStrength, splashRadius)
                    explosionInfo[1] = False
            else:
                fashion.isDestroyed = isDestroyed
            fashion.setEnableDrawMergedModel(not isDestroyed)
            if delCallback:
                for functor in self.__destroyCallbacks:
                    functorArgs = functor.args
                    if functorArgs[1] == chunkID and functorArgs[2] == destrIndex:
                        del self.__destroyCallbacks[functor]
                        break

            return

    def __dropDestructible(self, chunkID, destrIndex, fallDirYaw, pitchConstr, fallSpeed, isAnimate, obstacleCollisionFlags):
        self.__stopLifetimeEffect(chunkID, destrIndex, 0)
        if isAnimate:
            self.__launchFallEffect(chunkID, destrIndex, 'fractureEffect', fallDirYaw)
        useEffectsOnTouchDown = obstacleCollisionFlags & 8 or pitchConstr > _MAX_PITCH_TO_CHECK_TERRAIN
        desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
        if desc is None:
            _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
            return
        else:
            if 'preferredTiltDirections' in desc:
                fallDirYaw = self.__pickPrefferedTiltAngle(chunkID, destrIndex, fallDirYaw, desc)
            fashion = _getOrCreateFashion(self.__spaceID, chunkID, destrIndex, False)
            fashion.havokRemove()
            destrType = desc['type']
            if destrType == DESTR_TYPE_FALLING_ATOM:
                if isAnimate:
                    if useEffectsOnTouchDown:
                        touchdownCallback = partial(self.__touchDownWithEffect, chunkID, destrIndex, fallDirYaw, 'touchdownEffect', 'touchdownBreakEffect', fashion)
                    else:
                        touchdownCallback = partial(self.__touchDown, fashion)
                else:
                    self.__touchDown(fashion)
                    touchdownCallback = None
            elif isAnimate and useEffectsOnTouchDown:
                touchdownCallback = partial(self.__launchFallEffect, chunkID, destrIndex, 'touchdownEffect', fallDirYaw)
            else:
                touchdownCallback = None
            initialMatrix = self.__getDestrInitialMatrix(chunkID, destrIndex)
            g_destructiblesAnimator.showFall(self.__spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, fallSpeed, isAnimate, initialMatrix, touchdownCallback)
            return

    def __pickPrefferedTiltAngle(self, chunkID, destrIndex, hitDirYaw, desc):
        transformation = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
        dYaw = transformation.yaw
        hitYaw_localFrame = hitDirYaw - dYaw
        tiltYaw_localFrame = min(desc['preferredTiltDirections'] or [hitYaw_localFrame], key=lambda angle: abs(angle - hitYaw_localFrame))
        if tiltYaw_localFrame > math.pi:
            tiltYaw_localFrame -= 2 * math.pi
        elif tiltYaw_localFrame < -math.pi:
            tiltYaw_localFrame += 2 * math.pi
        tiltYaw_worldFrame = tiltYaw_localFrame + dYaw
        return tiltYaw_worldFrame

    def __touchDownWithEffect(self, chunkID, destrIndex, fallDirYaw, touchEffect, breakEffect, fashion):
        self.__launchFallEffect(chunkID, destrIndex, touchEffect, fallDirYaw)
        self.__launchFallEffect(chunkID, destrIndex, breakEffect, fallDirYaw)
        self.__touchDown(fashion)

    def __touchDown(self, fashion):
        if fashion.hasDamagedMaterial():
            fashion.isDestroyed = True

    def __delayedHavokExplosion(self, spaceID, explosionInfo):
        if spaceID != self.__spaceID:
            return
        if explosionInfo[1]:
            endPoint, _, _, _, radius, impact = explosionInfo[0]
            BigWorld.wg_havokExplosion(endPoint, impact, radius)
            explosionInfo[1] = False

    def __launchFallEffect(self, chunkID, destrIndex, effectName, fallDirYaw):
        player = BigWorld.player()
        if player is None or isPlayerAccount():
            return
        else:
            desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
            if desc is None:
                _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
                return
            effectVars = desc.get(effectName)
            if effectVars is None:
                return
            effectStuff = random.choice(effectVars)
            chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
            destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
            pos = chunkMatrix.translation + destrMatrix.translation
            dir = Math.Vector3(math.sin(fallDirYaw), 0.0, math.cos(fallDirYaw))
            if desc['type'] == DESTR_TYPE_TREE:
                treeScale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
                scale = 1.0 + (treeScale - 1.0) * _TREE_EFFECTS_SCALE_RATIO
            else:
                scale = desc['effectScale']
            player.terrainEffects.addNew(pos, effectStuff.effectsList, effectStuff.keyPoints, None, dir=dir, scale=scale)
            return

    def __getDestrInitialMatrix(self, chunkID, destrIndex):
        return self.__destrInitialMatrices.setdefault((chunkID, destrIndex), BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex))


def _extractEffectLists(desc):
    type = desc['type']
    effectLists = []
    if type == DESTR_TYPE_TREE:
        effTypes = ('fractureEffect', 'touchdownEffect')
        effDescs = [desc]
    elif type == DESTR_TYPE_FALLING_ATOM:
        effTypes = ('fractureEffect', 'touchdownEffect', 'touchdownBreakEffect')
        effDescs = [desc]
    elif type == DESTR_TYPE_STRUCTURE:
        effTypes = ('ramEffect', 'hitEffect', 'decayEffect')
        effDescs = desc['modules'].itervalues()
    else:
        effTypes = ('effect', 'decayEffect')
        effDescs = [desc]
    for effDesc in effDescs:
        for effType in effTypes:
            vars = effDesc.get(effType)
            if vars is not None:
                for stuff in vars:
                    effectLists.append(stuff[1])

    return effectLists


def _encodeModule(chunkID, structureIndex, moduleKind):
    return chunkID << 16 | structureIndex << 8 | moduleKind


def _getOrCreateFashion(spaceID, chunkID, destrIndex, enableHavok):
    fashion = BigWorld.wg_getChunkModelFashion(spaceID, chunkID, destrIndex)
    if fashion is None:
        fashion = BigWorld.WGMaterialDisabler()
        BigWorld.wg_setChunkModelFashion(spaceID, chunkID, destrIndex, fashion, enableHavok)
    return fashion


def _getOrCreateStaticHavokFashion(spaceID, chunkID, destrIndex):
    fashion = BigWorld.wg_getChunkModelFashion(spaceID, chunkID, destrIndex)
    if fashion is None:
        fashion = BigWorld.WGStaticModelFashion()
        BigWorld.wg_setChunkModelFashion(spaceID, chunkID, destrIndex, fashion, True)
    return fashion


class AreaDestructibles(BigWorld.Entity):

    def __init__(self):
        pass

    def onEnterWorld(self, prereqs):
        if g_destructiblesManager.getSpaceID() != self.spaceID:
            g_destructiblesManager.startSpace(self.spaceID)
        chunkID = chunkIDFromPosition(self.position)
        self.__chunkID = chunkID
        g_destructiblesManager._addController(chunkID, self)
        self.__prevFallenColumns = frozenset(self.fallenColumns)
        for fallData in self.fallenColumns:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DESTR_TYPE_FALLING_ATOM, fallData, False)

        self.__prevFallenTrees = frozenset(self.fallenTrees)
        for fallData in self.fallenTrees:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DESTR_TYPE_TREE, fallData, False)

        self.__prevDestroyedFragiles = frozenset(self.destroyedFragiles)
        for fragileData in self.destroyedFragiles:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DESTR_TYPE_FRAGILE, fragileData, False)

        self.__prevDestroyedModules = frozenset(self.destroyedModules)
        for moduleData in self.destroyedModules:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DESTR_TYPE_STRUCTURE, moduleData, False)

    def onLeaveWorld(self):
        g_destructiblesManager._delController(self.__chunkID)

    def isDestructibleBroken(self, itemIndex, matKind, destrType = None):
        if destrType is None:
            for t in (DESTR_TYPE_FRAGILE,
             DESTR_TYPE_STRUCTURE,
             DESTR_TYPE_FALLING_ATOM,
             DESTR_TYPE_TREE):
                if self.isDestructibleBroken(itemIndex, matKind, t):
                    return True

            return False
        else:
            if destrType == DESTR_TYPE_FRAGILE:
                for fragileData in self.destroyedFragiles:
                    itemIndex_, _ = decodeFragile(fragileData)
                    if itemIndex_ == itemIndex:
                        return True

            elif destrType == DESTR_TYPE_STRUCTURE:
                for moduleData in self.destroyedModules:
                    itemIndex_, matKind_, _ = decodeDestructibleModule(moduleData)
                    if itemIndex_ == itemIndex and matKind_ == matKind:
                        return True

            elif destrType == DESTR_TYPE_TREE:
                for fallData in self.fallenTrees:
                    itemIndex_, _, _, _ = decodeFallenTree(fallData)
                    if itemIndex_ == itemIndex:
                        return True

            else:
                for fallData in self.fallenColumns:
                    itemIndex_, _, _ = decodeFallenColumn(fallData)
                    if itemIndex_ == itemIndex:
                        return True

            return False

    def set_fallenTrees(self, prev):
        prev = self.__prevFallenTrees
        curr = frozenset(self.fallenTrees)
        self.__prevFallenTrees = curr
        for fallData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DESTR_TYPE_TREE, fallData, True)

    def set_fallenColumns(self, prev):
        prev = self.__prevFallenColumns
        curr = frozenset(self.fallenColumns)
        self.__prevFallenColumns = curr
        for fallData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DESTR_TYPE_FALLING_ATOM, fallData, True)

    def set_destroyedFragiles(self, prev):
        prev = self.__prevDestroyedFragiles
        curr = frozenset(self.destroyedFragiles)
        self.__prevDestroyedFragiles = curr
        for fragileData in curr.difference(prev):
            _, isShotDamage = decodeFragile(fragileData)
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DESTR_TYPE_FRAGILE, fragileData, True, isShotDamage)

    def set_destroyedModules(self, prev):
        prev = self.__prevDestroyedModules
        curr = frozenset(self.destroyedModules)
        self.__prevDestroyedModules = curr
        for moduleData in curr.difference(prev):
            _, _, isShotDamage = decodeDestructibleModule(moduleData)
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DESTR_TYPE_STRUCTURE, moduleData, True, isShotDamage)


class _DestructiblesAnimator():
    __UPDATE_INTERVAL = 0.016666
    __MAX_PHYS_UPDATE_DELAY = 0.02
    __INIT_SPEED_NORMALISER = 0.45
    __STOP_SIMULATION_EPSILON = math.pi / 500
    __MAX_SIMULATION_DURATION = 8.0

    def __init__(self):
        self.__updateCallbackID = None
        self.__isUpdating = False
        self.__bodies = []
        return

    def __del__(self):
        self.clear()

    def clear(self):
        self.__stopUpdate()
        self.__bodies = []

    def showFall(self, spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, discreteInitSpeed, isNeedAnimation, initialMatrix, touchdownCallback = None):
        desc = g_cache.getDestructibleDesc(spaceID, chunkID, destrIndex)
        if desc is None:
            _printErrDescNotAvailable(spaceID, chunkID, destrIndex)
            return
        else:
            destrMatrix = Math.Matrix(initialMatrix)
            scale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
            height = desc['height'] * scale
            mass = desc['mass'] * scale * scale * scale
            stiffness = desc['springStiffnes'] * scale * scale
            pitch = 0.0
            pitchSpeed = (discreteInitSpeed + 1) * self.__INIT_SPEED_NORMALISER
            inertiaMoment = mass * height * height / 3.0
            translation = destrMatrix.translation
            destrMatrix.translation = Math.Vector3(0, 0, 0)
            invFallYawRot = Math.Matrix()
            invFallYawRot.setRotateY(-fallDirYaw)
            destrMatrix.postMultiply(invFallYawRot)
            fallYawRot = Math.Matrix()
            fallYawRot.setRotateY(fallDirYaw)
            body = {'pitch': pitch,
             'pitchSpeed': pitchSpeed,
             'inertiaMoment': inertiaMoment,
             'mass': mass,
             'height': height,
             'springAngle': desc['springAngle'],
             'springStiffnes': stiffness,
             'springResist': desc['springResist'] * scale * scale,
             'airResist': desc['airResist'] * scale * scale,
             'pitchConstr': pitchConstr,
             'preRot': destrMatrix,
             'postRot': fallYawRot,
             'translation': translation,
             'chunkID': chunkID,
             'spaceID': spaceID,
             'destrIndex': destrIndex,
             'simulationTime': 0.0,
             'buryDepth': desc['buryDepth'] * scale}
            if touchdownCallback is not None:
                body['touchdownCallback'] = touchdownCallback
            if isNeedAnimation:
                self.__bodies.append(body)
                self.__startUpdate()
            else:
                weight = physics_shared.G * mass
                angStiffness = 0.5 * height * stiffness
                approxPitch = pitchConstr - 0.5 * desc['springAngle']
                body['pitch'] = BigWorld.wg_solveDestructibleFallPitch(weight, angStiffness, pitchConstr - desc['springAngle'], approxPitch)
                self.__positionBodyModel(body)
            return

    def __detectPitchConstraint(self, spaceID, chunkID, root, fallDir, scanOffs, scanRange, destrIndex):
        testsCount = min(15, max(5, int(scanRange / 0.7)))
        rootUp = root + (0, 100, 0)
        rootDown = root - (0, 100, 0)
        fallNormal = Math.Vector3(fallDir)
        fallNormal.normalise()
        cb = partial(_fallCollideCallback, destrIndex, chunkID)
        rootTestRes = BigWorld.wg_collideSegment(spaceID, rootUp, rootDown, 128, cb)
        if rootTestRes is None:
            return math.pi * 0.5
        else:
            rootPoint = rootTestRes[0]
            minPitch = math.pi
            sumPitch = 0.0
            scanStep = scanRange / (testsCount - 1)
            succsessTestCnt = 0
            for i in xrange(testsCount):
                fallVector = fallNormal * (scanOffs + i * scanStep)
                res = BigWorld.wg_collideSegment(spaceID, rootUp + fallVector, rootDown + fallVector, 128, cb)
                if res is not None:
                    p = res[0]
                    pitch = math.pi * 0.5 + (p - rootPoint).pitch
                    sumPitch += pitch
                    succsessTestCnt += 1
                    if pitch < minPitch:
                        minPitch = pitch

            return minPitch * 0.8 + sumPitch * 0.2 / succsessTestCnt

    def __moveBody(self, body, dt):
        pitch = body['pitch']
        if pitch < 0.0:
            body['pitchSpeed'] = 0.0
            body['pitch'] = 0.0
            pitch = 0.0
        pitchConstr = body['pitchConstr']
        if pitch > pitchConstr:
            body['pitchSpeed'] = 0.0
            body['pitch'] = pitchConstr
            pitch = pitchConstr
        height = body['height']
        mp = height * height * 0.25
        torque = 0.5 * height * physics_shared.G * body['mass'] * math.sin(pitch)
        torque -= body['pitchSpeed'] * body['airResist'] * mp
        if pitch + body['springAngle'] > pitchConstr:
            touchdownCallback = body.get('touchdownCallback')
            if touchdownCallback is not None:
                touchdownCallback()
                del body['touchdownCallback']
            anglePen = pitch + body['springAngle'] - pitchConstr
            torque -= anglePen * body['springStiffnes'] * mp
            torque -= body['pitchSpeed'] * body['springResist'] * mp
        body['pitchSpeed'] += dt * torque / body['inertiaMoment']
        body['simulationTime'] += dt
        if abs(body['pitchSpeed']) + abs(torque) < self.__STOP_SIMULATION_EPSILON or body['simulationTime'] > self.__MAX_SIMULATION_DURATION:
            return False
        else:
            body['pitch'] += dt * body['pitchSpeed']
            return True

    def __positionBodyModel(self, body):
        m = Math.Matrix()
        m.setRotateX(body['pitch'])
        m.preMultiply(body['preRot'])
        m.postMultiply(body['postRot'])
        m.translation = body['translation'] - (0.0, body['buryDepth'] * math.sin(body['pitch']), 0.0)
        windK = max(1.0 - body['simulationTime'] / 2.0, 0)
        spaceID = body['spaceID']
        BigWorld.wg_setDestructibleMatrix(spaceID, body['chunkID'], body['destrIndex'], m, windK)

    def __update(self, dt):
        removedBodies = []
        cnt = int(math.ceil(dt / self.__MAX_PHYS_UPDATE_DELAY))
        step = dt / cnt
        for body in self.__bodies:
            for i in xrange(cnt):
                if not self.__moveBody(body, step):
                    removedBodies.append(body)
                    break

        for body in removedBodies:
            self.__bodies.remove(body)

        if len(self.__bodies) == 0:
            self.__stopUpdate()
        for body in self.__bodies:
            self.__positionBodyModel(body)

    def __startUpdate(self):
        if not self.__isUpdating:
            self.__isUpdating = True
            self.__lastUpdateTime = clock() - self.__UPDATE_INTERVAL
            self.__updateCallback()

    def __stopUpdate(self):
        self.__isUpdating = False
        if self.__updateCallbackID is not None:
            BigWorld.cancelCallback(self.__updateCallbackID)
            self.__updateCallbackID = None
        return

    def __updateCallback(self):
        self.__updateCallbackID = None
        curTime = clock()
        self.__update(curTime - self.__lastUpdateTime)
        self.__lastUpdateTime = curTime
        if self.__isUpdating:
            self.__updateCallbackID = BigWorld.callback(self.__UPDATE_INTERVAL, self.__updateCallback)
        return


def _fallCollideCallback(curItemIndex, curChunkID, matKind, collFlags, itemIndex, chunkID):
    return curChunkID != chunkID or curItemIndex != itemIndex


def _printErrDescNotAvailable(spaceID, chunkID, destrIndex):
    p = BigWorld.player()
    if p:
        spaceName = p.arena.arenaType.geometryName
    else:
        spaceName = 'unknown'
    objName = BigWorld.wg_getDestructibleFilename(spaceID, chunkID, destrIndex)
    if not objName:
        objName = 'unknown'
    LOG_ERROR('Destructible descriptor is not available, space: %s, object: %s' % (spaceName, objName))


class DestructiblesManagerStaticModel():

    def __init__(self):
        self.__spaceID = None
        self.__loadedChunkIDs = {}
        self.__savedLoadedChunkIDs = None
        self.__savedSpaceID = None
        self.__destructiblesWaitDestroy = {}
        self.__effectsResourceRefs = {}
        self.__structuresEffects = {}
        self.__lifetimeEffects = {}
        self.forceNoAnimation = False
        self.__damagedModules = set()
        self.__destrInitialMatrices = {}
        self.__ctrls = {}
        self.__destroyCallbacks = {}
        self.__projectileExplosions = []
        self.__explodedDestructibles = []
        return

    def clear(self):
        self.__spaceID = None
        self.__loadedChunkIDs = {}
        self.__destructiblesWaitDestroy = {}
        self.__effectsResourceRefs = {}
        self.__structuresEffects = {}
        self.__lifetimeEffects = {}
        self.__damagedModules = set()
        self.__destrInitialMatrices = {}
        self.__ctrls = {}
        self.__destroyCallbacks = {}
        self.__projectileExplosions = []
        self.__explodedDestructibles = []
        return

    def startSpace(self, spaceID):
        self.clear()
        self.__spaceID = spaceID

    def getSpaceID(self):
        return self.__spaceID

    def getController(self, chunkID):
        return self.__ctrls.get(chunkID)

    def onChunkLoad(self, chunkID, numDestructibles):
        if self.__spaceID is None:
            LOG_ERROR('Notification about chunk load came when no space started')
            return
        else:
            if numDestructibles > 256:
                if not isPlayerAccount():
                    self.__logErrorTooMuchDestructibles(chunkID)
            self.__loadedChunkIDs[chunkID] = numDestructibles
            chunkEntries = self.__destructiblesWaitDestroy.get(chunkID)
            if chunkEntries is not None:
                for dmgType, destrData, isNeedAnimation in chunkEntries:
                    self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation)

                del self.__destructiblesWaitDestroy[chunkID]
            return

    def onChunkLoose(self, chunkID):
        if self.__loadedChunkIDs.has_key(chunkID):
            del self.__loadedChunkIDs[chunkID]
        if self.__effectsResourceRefs.has_key(chunkID):
            del self.__effectsResourceRefs[chunkID]

    def isChunkLoaded(self, chunkID):
        return self.__loadedChunkIDs.has_key(chunkID)

    def onProjectileExploded(self, hitParams, damagedDestructibles):
        self.__reduceExplosionCacheByTimeout()
        explosionInfo = [hitParams, True]
        explDestrs = self.__explodedDestructibles
        gotDestrs = False
        restDamagedDestructibles = []
        for chunkID, itemIndex, matKind in damagedDestructibles:
            found = False
            for destr in explDestrs:
                time, itemInfo = destr
                chunkID_, itemIndex_, matKind_, dmgType, destrData = itemInfo
                if chunkID_ == chunkID and itemIndex_ == itemIndex and (dmgType == DESTR_TYPE_FRAGILE or matKind_ == matKind):
                    self.__destroyDestructible(chunkID, dmgType, destrData, True, explosionInfo)
                    explDestrs.remove(destr)
                    found = True
                    gotDestrs = True
                    break

            if not found:
                restDamagedDestructibles.append((chunkID, itemIndex, matKind))

        if restDamagedDestructibles:
            newExpl = (BigWorld.time(), explosionInfo, restDamagedDestructibles)
            self.__projectileExplosions.append(newExpl)
        if not gotDestrs:
            BigWorld.callback(_SHOT_EXPLOSION_SYNC_TIMEOUT + DESTRUCTIBLE_HIDING_DELAY, partial(self.__delayedHavokExplosion, self.__spaceID, explosionInfo))

    def orderDestructibleDestroy(self, chunkID, dmgType, destrData, isNeedAnimation, syncWithProjectile = False):
        if self.forceNoAnimation:
            isNeedAnimation = False
        if self.__loadedChunkIDs.has_key(chunkID):
            if isNeedAnimation and syncWithProjectile:
                if dmgType == DESTR_TYPE_FRAGILE:
                    itemIndex, _ = decodeFragile(destrData)
                    matKind = 0
                elif dmgType == DESTR_TYPE_STRUCTURE:
                    itemIndex, matKind, _ = decodeDestructibleModule(destrData)
                else:
                    LOG_CODEPOINT_WARNING()
                    return
                self.__reduceExplosionCacheByTimeout()
                for expl in reversed(self.__projectileExplosions):
                    time, explInfo, damagedDestrs = expl
                    for destr in damagedDestrs:
                        chunkID_, itemIndex_, matKind_ = destr
                        if chunkID == chunkID_ and itemIndex == itemIndex_ and (dmgType == DESTR_TYPE_FRAGILE or matKind == matKind_):
                            self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation, explInfo)
                            damagedDestrs.remove(destr)
                            if not damagedDestrs:
                                self.__projectileExplosions.remove(expl)
                            return

                itemInfo = (chunkID,
                 itemIndex,
                 matKind,
                 dmgType,
                 destrData)
                self.__explodedDestructibles.append((BigWorld.time(), itemInfo))
                BigWorld.callback(_SHOT_EXPLOSION_SYNC_TIMEOUT + 0.01, self.__reduceExplosionCacheByTimeout)
            else:
                self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation)
        else:
            entry = (dmgType, destrData, isNeedAnimation)
            self.__destructiblesWaitDestroy.setdefault(chunkID, []).append(entry)

    def onBeforeReplayTimeWarp(self, rewind):
        for functor, callbackID in self.__destroyCallbacks.iteritems():
            if not rewind:
                functor(False)
            BigWorld.cancelCallback(callbackID)

        self.__destroyCallbacks.clear()
        if rewind:
            self.__savedLoadedChunkIDs = self.__loadedChunkIDs
            self.__savedSpaceID = self.__spaceID
            for (chunkID, destrIndex), m in self.__destrInitialMatrices.iteritems():
                BigWorld.wg_setDestructibleMatrix(self.__spaceID, chunkID, destrIndex, m, 1.0)

    def onAfterReplayTimeWarp(self):
        if self.__savedLoadedChunkIDs is None:
            return
        else:
            g_destructiblesAnimator.clear()
            self.__spaceID = self.__savedSpaceID
            for chunkID, numDestructibles in self.__savedLoadedChunkIDs.iteritems():
                self.onChunkLoad(chunkID, numDestructibles)

            self.__savedSpaceID = None
            self.__savedLoadedChunkIDs = None
            return

    def _addController(self, chunkID, ctrl):
        self.__ctrls[chunkID] = ctrl

    def _delController(self, chunkID):
        if self.__ctrls.has_key(chunkID):
            del self.__ctrls[chunkID]

    def __reduceExplosionCacheByTimeout(self):
        currTime = BigWorld.time()
        newExplCache = []
        for expl in self.__projectileExplosions:
            time, explInfo, _ = expl
            if currTime - time < _SHOT_EXPLOSION_SYNC_TIMEOUT:
                newExplCache.append(expl)

        self.__projectileExplosions = newExplCache
        newItemCache = []
        for destr in self.__explodedDestructibles:
            time, itemInfo = destr
            if currTime - time < _SHOT_EXPLOSION_SYNC_TIMEOUT:
                newItemCache.append(destr)
            else:
                chunkID, _, _, dmgType, destrData = itemInfo
                self.__destroyDestructible(chunkID, dmgType, destrData, True)

        self.__explodedDestructibles = newItemCache

    def __logErrorTooMuchDestructibles(self, chunkID):
        x, y = chunkIndexesFromChunkID(chunkID)
        player = BigWorld.player()
        if player is None:
            LOG_ERROR('Number of destructibles more than 256, chunk: %i %i' % (x, y))
        else:
            if x >= 0:
                xh = hex(x)[2:]
                xh = '0000'[:4 - len(xh)] + xh
            else:
                xh = hex(65535 + x + 1)[2:]
            if y >= 0:
                yh = hex(y)[2:]
                yh = '0000'[:4 - len(yh)] + yh
            else:
                yh = hex(65535 + y + 1)[2:]
            arenaTypeID = player.arenaTypeID
            LOG_ERROR('Number of destructibles more than 256, arena: %s, chunk: %s' % (arenaTypeID, xh + yh + 'o'))
        return

    def __onResourceLoad(self, spaceID, chunkID, resourceRefs):
        if spaceID == self.__spaceID:
            self.__effectsResourceRefs[chunkID] = resourceRefs

    def __destroyDestructible(self, chunkID, dmgType, destData, isNeedAnimation, explosionInfo = None):
        if self.forceNoAnimation:
            isNeedAnimation = False
        if dmgType == DESTR_TYPE_FALLING_ATOM:
            destrIndex, fallDirYaw, fallSpeed = decodeFallenColumn(destData)
            pitchConstr, collisionFlags = BigWorld.wg_getDestructibleFallPitchConstr(self.__spaceID, chunkID, destrIndex, fallDirYaw)
            if pitchConstr is None:
                pitchConstr = math.pi / 2.0
            self.__dropDestructible(chunkID, destrIndex, dmgType, fallDirYaw, pitchConstr, fallSpeed, isNeedAnimation, collisionFlags)
        if dmgType == DESTR_TYPE_TREE:
            destrIndex, fallDirYaw, pitchConstr, fallSpeed = decodeFallenTree(destData)
            _, collisionFlags = BigWorld.wg_getDestructibleFallPitchConstr(self.__spaceID, chunkID, destrIndex, fallDirYaw)
            self.__dropDestructible(chunkID, destrIndex, dmgType, fallDirYaw, pitchConstr, fallSpeed, isNeedAnimation, collisionFlags)
            if FMOD.enabled:
                FMOD.lightSoundRemove(self.__spaceID, chunkID, destrIndex)
        elif dmgType == DESTR_TYPE_FRAGILE:
            destrIndex, isShotDamage = decodeFragile(destData)
            self.__destroyFragile(chunkID, destrIndex, isNeedAnimation, isShotDamage, explosionInfo)
            if FMOD.enabled:
                FMOD.lightSoundRemove(self.__spaceID, chunkID, destrIndex)
        elif dmgType == DESTR_TYPE_STRUCTURE:
            destrIndex, matKind, isShotDamage = decodeDestructibleModule(destData)
            self.__destroyModule(chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage)
        return

    def __setDestructibleInitialState(self, chunkID, destrIndex):
        if type == DESTR_TYPE_STRUCTURE:
            for moduleKind, moduleDesc in desc['modules'].iteritems():
                self.__startLifetimeEffect(chunkID, destrIndex, moduleKind)

        else:
            self.__startLifetimeEffect(chunkID, destrIndex, -1)

    def __destroyFragile(self, chunkID, destrIndex, isNeedAnimation, isShotDamage, explosionInfo = None):
        self.__stopLifetimeEffect(chunkID, destrIndex, -1)
        isHavokVisible = False
        if isNeedAnimation:
            functor = partial(self.__setFragileDestroyed, self.__spaceID, chunkID, destrIndex, isNeedAnimation, isShotDamage, isHavokVisible, explosionInfo)
            callbackID = BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, functor)
            self.__destroyCallbacks[functor] = callbackID
        else:
            self.__setFragileDestroyed(self.__spaceID, chunkID, destrIndex, isNeedAnimation, isShotDamage, isHavokVisible, explosionInfo, False)
        if isNeedAnimation:
            self.__launchEffect(chunkID, destrIndex, -1, 'decayEffect', isHavokVisible)
            if isShotDamage:
                coreEffectType = 'hitEffect'
            else:
                coreEffectType = 'effect'
            self.__launchEffect(chunkID, destrIndex, -1, coreEffectType, isHavokVisible)

    def onPlayModuleDestructionAnimation(self, chunkID, destrIndex, moduleIndex, isShotDamage, isHavokVisible):
        self.__playModuleDestructionAnimation(chunkID, destrIndex, moduleIndex, isShotDamage, isHavokVisible)

    def __playModuleDestructionAnimation(self, chunkID, destrIndex, moduleIndex, isShotDamage, isHavokVisible):
        self.__stopLifetimeEffect(chunkID, destrIndex, moduleIndex)
        if isShotDamage:
            coreEffectType = 'hitEffect'
        else:
            coreEffectType = 'ramEffect'
        self.__launchEffect(chunkID, destrIndex, moduleIndex, coreEffectType, isHavokVisible)

    def __destroyModule(self, chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage, explosionInfo = None):
        moduleIndex = matKind - DESTRUCTIBLE_MATKIND.NORMAL_MIN
        isHavokVisible = False
        moduleDependencyHidingDelay = MODULE_DEPENDENCY_HIDING_DELAY if isHavokVisible else 0.0
        if isNeedAnimation:
            self.__playModuleDestructionAnimation(chunkID, destrIndex, moduleIndex, isShotDamage, isHavokVisible)
            functor = partial(self.__setModuleDestroyed, self.__spaceID, chunkID, destrIndex, moduleIndex, isNeedAnimation, isShotDamage, isHavokVisible)
            callbackID = BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, functor)
            self.__destroyCallbacks[functor] = callbackID
        else:
            self.__stopLifetimeEffect(chunkID, destrIndex, moduleIndex)
            self.__setModuleDestroyed(self.__spaceID, chunkID, destrIndex, moduleIndex, isNeedAnimation, isShotDamage, isHavokVisible, False)

    def __setFragileDestroyed(self, spaceID, chunkID, destrIndex, isNeedAnimation, isShotDamage, isHavokVisible, explosionInfo = None, delCallback = True):
        if spaceID != self.__spaceID:
            return
        BigWorld.wg_destroyFragile(spaceID, chunkID, destrIndex, isNeedAnimation, isShotDamage, isHavokVisible)
        if delCallback:
            for functor in self.__destroyCallbacks:
                functorArgs = functor.args
                if functorArgs[1] == chunkID and functorArgs[2] == destrIndex:
                    del self.__destroyCallbacks[functor]
                    break

    def __setModuleDestroyed(self, spaceID, chunkID, destrIndex, moduleIndex, isNeedAnimation, isShotDamage, isHavokVisible, delCallback = True):
        if spaceID != self.__spaceID:
            return
        BigWorld.wg_destroyModule(spaceID, chunkID, destrIndex, moduleIndex, isNeedAnimation, isShotDamage, isHavokVisible)
        if delCallback:
            for functor in self.__destroyCallbacks:
                functorArgs = functor.args
                if functorArgs[1] == chunkID and functorArgs[2] == destrIndex:
                    del self.__destroyCallbacks[functor]
                    break

    def __dropDestructible(self, chunkID, destrIndex, dmgType, fallDirYaw, pitchConstr, fallSpeed, isAnimate, obstacleCollisionFlags):
        self.__stopLifetimeEffect(chunkID, destrIndex, 0)
        useEffectsOnTouchDown = obstacleCollisionFlags & 8 or pitchConstr > _MAX_PITCH_TO_CHECK_TERRAIN
        if dmgType == DESTR_TYPE_FALLING_ATOM:
            if isAnimate:
                self.__launchFallEffect(chunkID, destrIndex, 'fractureEffect', fallDirYaw)
                if useEffectsOnTouchDown:
                    touchdownCallback = partial(self.__touchDownWithEffect, chunkID, destrIndex, fallDirYaw, 'touchdownEffect', 'touchdownBreakEffect')
                else:
                    touchdownCallback = partial(self.__touchDown)
            else:
                self.__touchDown()
                touchdownCallback = None
            initialMatrix = self.__getDestrInitialMatrix(chunkID, destrIndex)
            g_destructiblesAnimator.showFall(self.__spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, fallSpeed, isAnimate, initialMatrix, touchdownCallback)
        else:
            if isAnimate:
                self.__launchTreeFallEffect(chunkID, destrIndex, 'fractureEffect', fallDirYaw)
            if isAnimate and useEffectsOnTouchDown:
                touchdownCallback = partial(self.__launchTreeFallEffect, chunkID, destrIndex, 'touchdownEffect', fallDirYaw)
            else:
                touchdownCallback = None
            initialMatrix = self.__getDestrInitialMatrix(chunkID, destrIndex)
            g_destructiblesAnimator.showFallTree(self.__spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, fallSpeed, isAnimate, initialMatrix, touchdownCallback)
        return

    def __launchEffect(self, chunkID, destrIndex, moduleIndex, effectType, isHavokVisible, callbackOnStop = None):
        destrType = BigWorld.wg_getDestructibleEffectCategory(self.__spaceID, chunkID, destrIndex, moduleIndex)
        effectCat = ''
        if destrType == DESTR_TYPE_TREE:
            effectCat = 'trees'
        elif destrType == DESTR_TYPE_FALLING_ATOM:
            effectCat = 'fallingAtoms'
        elif destrType == DESTR_TYPE_FRAGILE:
            effectCat = 'fragiles'
        elif destrType == DESTR_TYPE_STRUCTURE:
            effectCat = 'structures'
        effectName = BigWorld.wg_getDestructibleEffectName(self.__spaceID, chunkID, destrIndex, moduleIndex, effectType)
        if effectName == 'none':
            return
        else:
            effectVars = g_cache._getEffect(effectName, effectCat, False)
            if effectVars is None:
                print 'Could not find any effects vars for: ' + str(effectName) + ' - type: ' + str(effectType) + ' - cat: ' + str(effectCat) + ' (' + str(destrType) + ')'
                return
            if destrType == DESTR_TYPE_TREE or destrType == DESTR_TYPE_FALLING_ATOM:
                chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
                destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
                dir = destrMatrix.applyVector((0, 0, 1))
                pos = chunkMatrix.translation + destrMatrix.translation
                if destrType == DESTR_TYPE_TREE:
                    treeScale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
                    scale = 1.0 + (treeScale - 1.0) * _TREE_EFFECTS_SCALE_RATIO
                else:
                    scale = BigWorld.wg_getDestructibleEffectScale(self.__spaceID, chunkID, destrIndex, moduleIndex)
            else:
                hpMatrix = BigWorld.wg_getNMHardPointMatrix(self.__spaceID, chunkID, destrIndex, moduleIndex)
                dir = hpMatrix.applyVector((0, 0, 1))
                pos = hpMatrix.translation
                scale = BigWorld.wg_getDestructibleEffectScale(self.__spaceID, chunkID, destrIndex, moduleIndex)
            player = BigWorld.player()
            if player is None or isPlayerAccount():
                return
            effectStuff = random.choice(effectVars)
            effectID = player.terrainEffects.addNew(pos, effectStuff.effectsList, effectStuff.keyPoints, callbackOnStop, dir=dir, scale=scale, havokEnabled=isHavokVisible)
            return effectID

    def __startLifetimeEffect(self, chunkID, destrIndex, moduleKind):
        chance = BigWorld.wg_getDestructibleLifetimeEffectChance(chunkID, destrIndex, moduleKind)
        if chance is None or random.random() > chance:
            return
        else:
            lifetimeEffectID = self.__launchEffect(chunkID, destrIndex, moduleKind, 'lifetimeEffect', False)
            if lifetimeEffectID is not None:
                code = _encodeModule(chunkID, destrIndex, moduleKind)
                self.__lifetimeEffects[code] = lifetimeEffectID
            return

    def __stopLifetimeEffect(self, chunkID, destrIndex, moduleKind):
        code = _encodeModule(chunkID, destrIndex, moduleKind)
        lifetimeEffectID = self.__lifetimeEffects.get(code)
        if lifetimeEffectID is None:
            return
        else:
            del self.__lifetimeEffects[code]
            player = BigWorld.player()
            if player is not None and not isPlayerAccount():
                player.terrainEffects.stop(lifetimeEffectID)
            return

    def __pickPrefferedTiltAngle(self, chunkID, destrIndex, hitDirYaw, desc):
        transformation = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
        dYaw = transformation.yaw
        hitYaw_localFrame = hitDirYaw - dYaw
        tiltYaw_localFrame = min(desc['preferredTiltDirections'] or [hitYaw_localFrame], key=lambda angle: abs(angle - hitYaw_localFrame))
        if tiltYaw_localFrame > math.pi:
            tiltYaw_localFrame -= 2 * math.pi
        elif tiltYaw_localFrame < -math.pi:
            tiltYaw_localFrame += 2 * math.pi
        tiltYaw_worldFrame = tiltYaw_localFrame + dYaw
        return tiltYaw_worldFrame

    def __touchDownWithEffect(self, chunkID, destrIndex, fallDirYaw, touchEffect, breakEffect):
        self.__launchFallEffect(chunkID, destrIndex, touchEffect, fallDirYaw)
        self.__launchFallEffect(chunkID, destrIndex, breakEffect, fallDirYaw)
        self.__touchDown()

    def __touchDown(self):
        pass

    def __delayedHavokExplosion(self, spaceID, explosionInfo):
        if spaceID != self.__spaceID:
            return
        if explosionInfo[1]:
            endPoint, _, _, _, radius, impact = explosionInfo[0]
            BigWorld.wg_havokExplosion(endPoint, impact, radius)
            explosionInfo[1] = False

    def __launchFallEffect(self, chunkID, destrIndex, effectType, fallDirYaw):
        player = BigWorld.player()
        if player is None or isPlayerAccount():
            return
        else:
            effectName = BigWorld.wg_getDestructibleEffectName(self.__spaceID, chunkID, destrIndex, -1, effectType)
            if effectName == 'none':
                return
            effectVars = g_cache._getEffect(effectName, 'fallingAtoms', False)
            if effectVars is None:
                return
            effectStuff = random.choice(effectVars)
            chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
            destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
            pos = chunkMatrix.translation + destrMatrix.translation
            dir = Math.Vector3(math.sin(fallDirYaw), 0.0, math.cos(fallDirYaw))
            scale = BigWorld.wg_getDestructibleEffectScale(self.__spaceID, chunkID, destrIndex, -1)
            player.terrainEffects.addNew(pos, effectStuff.effectsList, effectStuff.keyPoints, None, dir=dir, scale=scale)
            return

    def __launchTreeFallEffect(self, chunkID, destrIndex, effectName, fallDirYaw):
        player = BigWorld.player()
        if player is None or isPlayerAccount():
            return
        else:
            desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
            if desc is None:
                _printErrDescNotAvailable(self.__spaceID, chunkID, destrIndex)
                return
            effectVars = desc.get(effectName)
            if effectVars is None:
                return
            effectStuff = random.choice(effectVars)
            chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
            destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
            pos = chunkMatrix.translation + destrMatrix.translation
            dir = Math.Vector3(math.sin(fallDirYaw), 0.0, math.cos(fallDirYaw))
            treeScale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
            scale = 1.0 + (treeScale - 1.0) * _TREE_EFFECTS_SCALE_RATIO
            player.terrainEffects.addNew(pos, effectStuff.effectsList, effectStuff.keyPoints, None, dir=dir, scale=scale)
            return

    def __getDestrInitialMatrix(self, chunkID, destrIndex):
        return self.__destrInitialMatrices.setdefault((chunkID, destrIndex), BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex))


class _DestructiblesStaticModelAnimator():
    __UPDATE_INTERVAL = 0.016666
    __MAX_PHYS_UPDATE_DELAY = 0.02
    __INIT_SPEED_NORMALISER = 0.45
    __STOP_SIMULATION_EPSILON = math.pi / 500
    __MAX_SIMULATION_DURATION = 8.0

    def __init__(self):
        self.__updateCallbackID = None
        self.__isUpdating = False
        self.__bodies = []
        return

    def __del__(self):
        self.clear()

    def clear(self):
        self.__stopUpdate()
        self.__bodies = []

    def showFall(self, spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, discreteInitSpeed, isNeedAnimation, initialMatrix, touchdownCallback = None):
        fallingParams = BigWorld.wg_getFallingParams(spaceID, chunkID, destrIndex)
        destrMatrix = Math.Matrix(initialMatrix)
        scale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
        height = fallingParams.get(0, 1) * scale
        mass = fallingParams.get(0, 0) * scale * scale * scale
        stiffness = fallingParams.get(1, 0) * scale * scale
        pitch = 0.0
        pitchSpeed = (discreteInitSpeed + 1) * self.__INIT_SPEED_NORMALISER
        inertiaMoment = mass * height * height / 3.0
        translation = destrMatrix.translation
        destrMatrix.translation = Math.Vector3(0, 0, 0)
        invFallYawRot = Math.Matrix()
        invFallYawRot.setRotateY(-fallDirYaw)
        destrMatrix.postMultiply(invFallYawRot)
        fallYawRot = Math.Matrix()
        fallYawRot.setRotateY(fallDirYaw)
        body = {'pitch': pitch,
         'pitchSpeed': pitchSpeed,
         'inertiaMoment': inertiaMoment,
         'mass': mass,
         'height': height,
         'springAngle': fallingParams.get(1, 1),
         'springStiffnes': stiffness,
         'springResist': fallingParams.get(1, 2) * scale * scale,
         'airResist': fallingParams.get(0, 2) * scale * scale,
         'pitchConstr': pitchConstr,
         'preRot': destrMatrix,
         'postRot': fallYawRot,
         'translation': translation,
         'chunkID': chunkID,
         'spaceID': spaceID,
         'destrIndex': destrIndex,
         'simulationTime': 0.0,
         'buryDepth': fallingParams.get(0, 3) * scale}
        if touchdownCallback is not None:
            body['touchdownCallback'] = touchdownCallback
        if isNeedAnimation:
            self.__bodies.append(body)
            self.__startUpdate()
        else:
            weight = physics_shared.G * mass
            angStiffness = 0.5 * height * stiffness
            approxPitch = pitchConstr - 0.5 * fallingParams.get(1, 1)
            body['pitch'] = BigWorld.wg_solveDestructibleFallPitch(weight, angStiffness, pitchConstr - fallingParams.get(1, 1), approxPitch)
            self.__positionBodyModel(body)
        return

    def showFallTree(self, spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, discreteInitSpeed, isNeedAnimation, initialMatrix, touchdownCallback = None):
        desc = g_cache.getDestructibleDesc(spaceID, chunkID, destrIndex)
        if desc is None:
            _printErrDescNotAvailable(spaceID, chunkID, destrIndex)
            return
        else:
            destrMatrix = Math.Matrix(initialMatrix)
            scale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
            height = desc['height'] * scale
            mass = desc['mass'] * scale * scale * scale
            stiffness = desc['springStiffnes'] * scale * scale
            pitch = 0.0
            pitchSpeed = (discreteInitSpeed + 1) * self.__INIT_SPEED_NORMALISER
            inertiaMoment = mass * height * height / 3.0
            translation = destrMatrix.translation
            destrMatrix.translation = Math.Vector3(0, 0, 0)
            invFallYawRot = Math.Matrix()
            invFallYawRot.setRotateY(-fallDirYaw)
            destrMatrix.postMultiply(invFallYawRot)
            fallYawRot = Math.Matrix()
            fallYawRot.setRotateY(fallDirYaw)
            body = {'pitch': pitch,
             'pitchSpeed': pitchSpeed,
             'inertiaMoment': inertiaMoment,
             'mass': mass,
             'height': height,
             'springAngle': desc['springAngle'],
             'springStiffnes': stiffness,
             'springResist': desc['springResist'] * scale * scale,
             'airResist': desc['airResist'] * scale * scale,
             'pitchConstr': pitchConstr,
             'preRot': destrMatrix,
             'postRot': fallYawRot,
             'translation': translation,
             'chunkID': chunkID,
             'spaceID': spaceID,
             'destrIndex': destrIndex,
             'simulationTime': 0.0,
             'buryDepth': desc['buryDepth'] * scale}
            if touchdownCallback is not None:
                body['touchdownCallback'] = touchdownCallback
            if isNeedAnimation:
                self.__bodies.append(body)
                self.__startUpdate()
            else:
                weight = physics_shared.G * mass
                angStiffness = 0.5 * height * stiffness
                approxPitch = pitchConstr - 0.5 * desc['springAngle']
                body['pitch'] = BigWorld.wg_solveDestructibleFallPitch(weight, angStiffness, pitchConstr - desc['springAngle'], approxPitch)
                self.__positionBodyModel(body)
            return

    def __detectPitchConstraint(self, spaceID, chunkID, root, fallDir, scanOffs, scanRange, destrIndex):
        testsCount = min(15, max(5, int(scanRange / 0.7)))
        rootUp = root + (0, 100, 0)
        rootDown = root - (0, 100, 0)
        fallNormal = Math.Vector3(fallDir)
        fallNormal.normalise()
        cb = partial(_fallCollideCallback, destrIndex, chunkID)
        rootTestRes = BigWorld.wg_collideSegment(spaceID, rootUp, rootDown, 128, cb)
        if rootTestRes is None:
            return math.pi * 0.5
        else:
            rootPoint = rootTestRes[0]
            minPitch = math.pi
            sumPitch = 0.0
            scanStep = scanRange / (testsCount - 1)
            succsessTestCnt = 0
            for i in xrange(testsCount):
                fallVector = fallNormal * (scanOffs + i * scanStep)
                res = BigWorld.wg_collideSegment(spaceID, rootUp + fallVector, rootDown + fallVector, 128, cb)
                if res is not None:
                    p = res[0]
                    pitch = math.pi * 0.5 + (p - rootPoint).pitch
                    sumPitch += pitch
                    succsessTestCnt += 1
                    if pitch < minPitch:
                        minPitch = pitch

            return minPitch * 0.8 + sumPitch * 0.2 / succsessTestCnt

    def __moveBody(self, body, dt):
        pitch = body['pitch']
        if pitch < 0.0:
            body['pitchSpeed'] = 0.0
            body['pitch'] = 0.0
            pitch = 0.0
        pitchConstr = body['pitchConstr']
        if pitch > pitchConstr:
            body['pitchSpeed'] = 0.0
            body['pitch'] = pitchConstr
            pitch = pitchConstr
        height = body['height']
        mp = height * height * 0.25
        torque = 0.5 * height * physics_shared.G * body['mass'] * math.sin(pitch)
        torque -= body['pitchSpeed'] * body['airResist'] * mp
        if pitch + body['springAngle'] > pitchConstr:
            touchdownCallback = body.get('touchdownCallback')
            if touchdownCallback is not None:
                touchdownCallback()
                del body['touchdownCallback']
            anglePen = pitch + body['springAngle'] - pitchConstr
            torque -= anglePen * body['springStiffnes'] * mp
            torque -= body['pitchSpeed'] * body['springResist'] * mp
        body['pitchSpeed'] += dt * torque / body['inertiaMoment']
        body['simulationTime'] += dt
        if abs(body['pitchSpeed']) + abs(torque) < self.__STOP_SIMULATION_EPSILON or body['simulationTime'] > self.__MAX_SIMULATION_DURATION:
            return False
        else:
            body['pitch'] += dt * body['pitchSpeed']
            return True

    def __positionBodyModel(self, body):
        m = Math.Matrix()
        m.setRotateX(body['pitch'])
        m.preMultiply(body['preRot'])
        m.postMultiply(body['postRot'])
        m.translation = body['translation'] - (0.0, body['buryDepth'] * math.sin(body['pitch']), 0.0)
        windK = max(1.0 - body['simulationTime'] / 2.0, 0)
        spaceID = body['spaceID']
        BigWorld.wg_setDestructibleMatrix(spaceID, body['chunkID'], body['destrIndex'], m, windK)

    def __update(self, dt):
        removedBodies = []
        cnt = int(math.ceil(dt / self.__MAX_PHYS_UPDATE_DELAY))
        step = dt / cnt
        for body in self.__bodies:
            for i in xrange(cnt):
                if not self.__moveBody(body, step):
                    removedBodies.append(body)
                    break

        for body in removedBodies:
            self.__bodies.remove(body)

        if len(self.__bodies) == 0:
            self.__stopUpdate()
        for body in self.__bodies:
            self.__positionBodyModel(body)

    def __startUpdate(self):
        if not self.__isUpdating:
            self.__isUpdating = True
            self.__lastUpdateTime = clock() - self.__UPDATE_INTERVAL
            self.__updateCallback()

    def __stopUpdate(self):
        self.__isUpdating = False
        if self.__updateCallbackID is not None:
            BigWorld.cancelCallback(self.__updateCallbackID)
            self.__updateCallbackID = None
        return

    def __updateCallback(self):
        self.__updateCallbackID = None
        curTime = clock()
        self.__update(curTime - self.__lastUpdateTime)
        self.__lastUpdateTime = curTime
        if self.__isUpdating:
            self.__updateCallbackID = BigWorld.callback(self.__UPDATE_INTERVAL, self.__updateCallback)
        return
