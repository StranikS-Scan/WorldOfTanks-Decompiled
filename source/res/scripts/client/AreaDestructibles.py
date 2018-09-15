# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AreaDestructibles.py
import math
import random
from functools import partial
from time import clock
import BigWorld
import Math
import DestructiblesCache
from constants import DESTRUCTIBLE_MATKIND
from debug_utils import LOG_ERROR, LOG_CODEPOINT_WARNING
from helpers import isPlayerAccount
import physics_shared
import WWISE
g_cache = None
g_destructiblesManager = None
g_destructiblesAnimator = None
MODULE_DEPENDENCY_HIDING_DELAY_CONSTANT = 0.25
MODULE_DEPENDENCY_HIDING_DELAY = MODULE_DEPENDENCY_HIDING_DELAY_CONSTANT
DESTRUCTIBLE_HIDING_DELAY_CONSTANT = 0.2
DESTRUCTIBLE_HIDING_DELAY = DESTRUCTIBLE_HIDING_DELAY_CONSTANT
_TREE_EFFECTS_SCALE_RATIO = 0.7
_MAX_PITCH_TO_CHECK_TERRAIN = math.radians(60)
_SHOT_EXPLOSION_SYNC_TIMEOUT = 0.11

def init():
    global g_destructiblesManager
    global g_cache
    global g_destructiblesAnimator
    g_cache = ClientDestructiblesCache()
    g_destructiblesManager = DestructiblesManager()
    g_destructiblesAnimator = _DestructiblesAnimator()


def clear():
    g_destructiblesManager.clear()
    g_destructiblesAnimator.clear()


class ClientDestructiblesCache(DestructiblesCache.DestructiblesCache):

    def getDestructibleDesc(self, spaceID, chunkID, destrIndex):
        filename = BigWorld.wg_getDestructibleFilename(spaceID, chunkID, destrIndex)
        return self.getDescByFilename(filename)


def _extractEffectLists(desc):
    type = desc['type']
    effectLists = []
    if type == DestructiblesCache.DESTR_TYPE_TREE:
        effTypes = ('fractureEffect', 'touchdownEffect')
        effDescs = [desc]
    elif type == DestructiblesCache.DESTR_TYPE_FALLING_ATOM:
        effTypes = ('fractureEffect', 'touchdownEffect', 'touchdownBreakEffect')
        effDescs = [desc]
    elif type == DestructiblesCache.DESTR_TYPE_STRUCTURE:
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
        chunkID = DestructiblesCache.chunkIDFromPosition(self.position)
        self.__chunkID = chunkID
        g_destructiblesManager._addController(chunkID, self)
        self.__prevFallenColumns = frozenset(self.fallenColumns)
        for fallData in self.fallenColumns:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DestructiblesCache.DESTR_TYPE_FALLING_ATOM, fallData, False)

        self.__prevFallenTrees = frozenset(self.fallenTrees)
        for fallData in self.fallenTrees:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DestructiblesCache.DESTR_TYPE_TREE, fallData, False)

        self.__prevDestroyedFragiles = frozenset(self.destroyedFragiles)
        for fragileData in self.destroyedFragiles:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DestructiblesCache.DESTR_TYPE_FRAGILE, fragileData, False)

        self.__prevDestroyedModules = frozenset(self.destroyedModules)
        for moduleData in self.destroyedModules:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, DestructiblesCache.DESTR_TYPE_STRUCTURE, moduleData, False)

    def onLeaveWorld(self):
        g_destructiblesManager._delController(self.__chunkID)

    def isDestructibleBroken(self, itemIndex, matKind, destrType=None):
        if destrType is None:
            for t in (DestructiblesCache.DESTR_TYPE_FRAGILE,
             DestructiblesCache.DESTR_TYPE_STRUCTURE,
             DestructiblesCache.DESTR_TYPE_FALLING_ATOM,
             DestructiblesCache.DESTR_TYPE_TREE):
                if self.isDestructibleBroken(itemIndex, matKind, t):
                    return True

            return False
        else:
            if destrType == DestructiblesCache.DESTR_TYPE_FRAGILE:
                for fragileData in self.destroyedFragiles:
                    itemIndex_, _ = DestructiblesCache.decodeFragile(fragileData)
                    if itemIndex_ == itemIndex:
                        return True

            elif destrType == DestructiblesCache.DESTR_TYPE_STRUCTURE:
                for moduleData in self.destroyedModules:
                    itemIndex_, matKind_, _ = DestructiblesCache.decodeDestructibleModule(moduleData)
                    if itemIndex_ == itemIndex and matKind_ == matKind:
                        return True

            elif destrType == DestructiblesCache.DESTR_TYPE_TREE:
                for fallData in self.fallenTrees:
                    itemIndex_, _, _, _ = DestructiblesCache.decodeFallenTree(fallData)
                    if itemIndex_ == itemIndex:
                        return True

            else:
                for fallData in self.fallenColumns:
                    itemIndex_, _, _ = DestructiblesCache.decodeFallenColumn(fallData)
                    if itemIndex_ == itemIndex:
                        return True

            return False

    def set_fallenTrees(self, prev):
        prev = self.__prevFallenTrees
        curr = frozenset(self.fallenTrees)
        self.__prevFallenTrees = curr
        for fallData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DestructiblesCache.DESTR_TYPE_TREE, fallData, True)

    def set_fallenColumns(self, prev):
        prev = self.__prevFallenColumns
        curr = frozenset(self.fallenColumns)
        self.__prevFallenColumns = curr
        for fallData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DestructiblesCache.DESTR_TYPE_FALLING_ATOM, fallData, True)

    def set_destroyedFragiles(self, prev):
        prev = self.__prevDestroyedFragiles
        curr = frozenset(self.destroyedFragiles)
        self.__prevDestroyedFragiles = curr
        for fragileData in curr.difference(prev):
            _, isShotDamage = DestructiblesCache.decodeFragile(fragileData)
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DestructiblesCache.DESTR_TYPE_FRAGILE, fragileData, True, isShotDamage)

    def set_destroyedModules(self, prev):
        prev = self.__prevDestroyedModules
        curr = frozenset(self.destroyedModules)
        self.__prevDestroyedModules = curr
        for moduleData in curr.difference(prev):
            _, _, isShotDamage = DestructiblesCache.decodeDestructibleModule(moduleData)
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, DestructiblesCache.DESTR_TYPE_STRUCTURE, moduleData, True, isShotDamage)


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
    LOG_ERROR('Destructible descriptor is not available, space: %s, object: %s, id: %d' % (spaceName, objName, destrIndex))


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
                if chunkID_ == chunkID and itemIndex_ == itemIndex and (dmgType == DestructiblesCache.DESTR_TYPE_FRAGILE or matKind_ == matKind):
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

    def orderDestructibleDestroy(self, chunkID, dmgType, destrData, isNeedAnimation, syncWithProjectile=False):
        if self.forceNoAnimation:
            isNeedAnimation = False
        if self.__loadedChunkIDs.has_key(chunkID):
            if isNeedAnimation and syncWithProjectile:
                if dmgType == DestructiblesCache.DESTR_TYPE_FRAGILE:
                    itemIndex, _ = DestructiblesCache.decodeFragile(destrData)
                    matKind = 0
                elif dmgType == DestructiblesCache.DESTR_TYPE_STRUCTURE:
                    itemIndex, matKind, _ = DestructiblesCache.decodeDestructibleModule(destrData)
                else:
                    LOG_CODEPOINT_WARNING()
                    return
                self.__reduceExplosionCacheByTimeout()
                for expl in reversed(self.__projectileExplosions):
                    time, explInfo, damagedDestrs = expl
                    for destr in damagedDestrs:
                        chunkID_, itemIndex_, matKind_ = destr
                        if chunkID == chunkID_ and itemIndex == itemIndex_ and (dmgType == DestructiblesCache.DESTR_TYPE_FRAGILE or matKind == matKind_):
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
            chunkID, _, _, dmgType, destrData = itemInfo
            self.__destroyDestructible(chunkID, dmgType, destrData, True)

        self.__explodedDestructibles = newItemCache

    def __logErrorTooMuchDestructibles(self, chunkID):
        x, y = DestructiblesCache.chunkIndexesFromChunkID(chunkID)
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

    def __destroyDestructible(self, chunkID, dmgType, destData, isNeedAnimation, explosionInfo=None):
        if self.forceNoAnimation:
            isNeedAnimation = False
        if dmgType == DestructiblesCache.DESTR_TYPE_FALLING_ATOM:
            destrIndex, fallDirYaw, fallSpeed = DestructiblesCache.decodeFallenColumn(destData)
            pitchConstr, collisionFlags = BigWorld.wg_getDestructibleFallPitchConstr(self.__spaceID, chunkID, destrIndex, fallDirYaw)
            if pitchConstr is None:
                pitchConstr = math.pi / 2.0
            self.__dropDestructible(chunkID, destrIndex, dmgType, fallDirYaw, pitchConstr, fallSpeed, isNeedAnimation, collisionFlags)
        if dmgType == DestructiblesCache.DESTR_TYPE_TREE:
            destrIndex, fallDirYaw, pitchConstr, fallSpeed = DestructiblesCache.decodeFallenTree(destData)
            _, collisionFlags = BigWorld.wg_getDestructibleFallPitchConstr(self.__spaceID, chunkID, destrIndex, fallDirYaw)
            self.__dropDestructible(chunkID, destrIndex, dmgType, fallDirYaw, pitchConstr, fallSpeed, isNeedAnimation, collisionFlags)
            WWISE.WG_lightSoundRemove(self.__spaceID, chunkID, destrIndex)
        elif dmgType == DestructiblesCache.DESTR_TYPE_FRAGILE:
            destrIndex, isShotDamage = DestructiblesCache.decodeFragile(destData)
            self.__destroyFragile(chunkID, destrIndex, isNeedAnimation, isShotDamage, explosionInfo)
            WWISE.WG_lightSoundRemove(self.__spaceID, chunkID, destrIndex)
        elif dmgType == DestructiblesCache.DESTR_TYPE_STRUCTURE:
            destrIndex, matKind, isShotDamage = DestructiblesCache.decodeDestructibleModule(destData)
            self.__destroyModule(chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage)
        return

    def __destroyFragile(self, chunkID, destrIndex, isNeedAnimation, isShotDamage, explosionInfo=None):
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

    def __destroyModule(self, chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage, explosionInfo=None):
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

    def __setFragileDestroyed(self, spaceID, chunkID, destrIndex, isNeedAnimation, isShotDamage, isHavokVisible, explosionInfo=None, delCallback=True):
        if spaceID != self.__spaceID:
            return
        BigWorld.wg_destroyFragile(spaceID, chunkID, destrIndex, isNeedAnimation, isShotDamage, isHavokVisible)
        if delCallback:
            for functor in self.__destroyCallbacks:
                functorArgs = functor.args
                if functorArgs[1] == chunkID and functorArgs[2] == destrIndex:
                    del self.__destroyCallbacks[functor]
                    break

    def __setModuleDestroyed(self, spaceID, chunkID, destrIndex, moduleIndex, isNeedAnimation, isShotDamage, isHavokVisible, delCallback=True):
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
        if dmgType == DestructiblesCache.DESTR_TYPE_FALLING_ATOM:
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

    def __launchEffect(self, chunkID, destrIndex, moduleIndex, effectType, isHavokVisible, callbackOnStop=None):
        destrType = BigWorld.wg_getDestructibleEffectCategory(self.__spaceID, chunkID, destrIndex, moduleIndex)
        effectCat = ''
        if destrType == DestructiblesCache.DESTR_TYPE_TREE:
            effectCat = 'trees'
        elif destrType == DestructiblesCache.DESTR_TYPE_FALLING_ATOM:
            effectCat = 'fallingAtoms'
        elif destrType == DestructiblesCache.DESTR_TYPE_FRAGILE:
            effectCat = 'fragiles'
        elif destrType == DestructiblesCache.DESTR_TYPE_STRUCTURE:
            effectCat = 'structures'
        effectName = BigWorld.wg_getDestructibleEffectName(self.__spaceID, chunkID, destrIndex, moduleIndex, effectType)
        if effectName == 'none':
            return
        else:
            effectVars = g_cache._getEffect(effectName, effectCat, False)
            if effectVars is None:
                LOG_ERROR('Could not find any effects vars for: ' + str(effectName) + ' - type: ' + str(effectType) + ' - cat: ' + str(effectCat) + ' (' + str(destrType) + ')')
                return
            if destrType == DestructiblesCache.DESTR_TYPE_TREE or destrType == DestructiblesCache.DESTR_TYPE_FALLING_ATOM:
                chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
                destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
                dir = destrMatrix.applyVector((0, 0, 1))
                pos = chunkMatrix.translation + destrMatrix.translation
                if destrType == DestructiblesCache.DESTR_TYPE_TREE:
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

    def showFall(self, spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, discreteInitSpeed, isNeedAnimation, initialMatrix, touchdownCallback=None):
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

    def showFallTree(self, spaceID, chunkID, destrIndex, fallDirYaw, pitchConstr, discreteInitSpeed, isNeedAnimation, initialMatrix, touchdownCallback=None):
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
        inertialMoment = body['inertiaMoment']
        if inertialMoment != 0.0:
            body['pitchSpeed'] += dt * torque / inertialMoment
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

        if not self.__bodies:
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
