# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AreaDestructibles.py
# Compiled at: 2011-03-17 17:45:45
import BigWorld
from debug_utils import *
from math import floor
import Math
import math
import game
import random
import ResMgr
import constants
from DestructiblesCache import *
from time import clock
from functools import partial
from helpers import bound_effects
from constants import DESTRUCTIBLE_MATKIND
import re
g_cache = None
g_destructiblesManager = None
g_destructiblesAnimator = None
DESTRUCTIBLE_HIDING_DELAY = 0.2
_TREE_EFFECTS_SCALE_RATIO = 0.7
_DAMAGE_TYPE_FALL = 0
_DAMAGE_TYPE_FRAGILE = 1
_DAMAGE_TYPE_MODULE = 2

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


class ClientDestructiblesCache(DestructiblesCache):

    def getDestructibleDesc(self, spaceID, chunkID, destrIndex):
        filename = BigWorld.wg_getDestructibleFilename(spaceID, chunkID, destrIndex)
        return self.getDescByFilename(filename)


class DestructiblesManager():

    def __init__(self):
        self.__spaceID = None
        self.__loadedChunkIDs = set()
        self.__destructiblesWaitDestroy = {}
        self.__effectsResourceRefs = {}
        self.__structuresEffects = {}
        self.__lifetimeEffects = {}
        self.__damagedModules = set()
        self.__destrInitialMatrices = {}
        self.__ctrls = {}
        return

    def clear(self):
        self.__spaceID = None
        self.__loadedChunkIDs = set()
        self.__destructiblesWaitDestroy = {}
        self.__effectsResourceRefs = {}
        self.__structuresEffects = {}
        self.__lifetimeEffects = {}
        self.__damagedModules = set()
        self.__destrInitialMatrices = {}
        self.__ctrls = {}
        return

    def startSpace(self, spaceID):
        self.clear()
        self.__spaceID = spaceID

    def getSpaceID(self):
        return self.__spaceID

    def getController(self, chunkID):
        return self.__ctrls.get(chunkID)

    def onChunkLoad(self, chunkID, numDestructibles):
        if numDestructibles > 256:
            self.__logErrorTooMuchDestructibles(chunkID)
        if self.__spaceID is None:
            LOG_ERROR('Notification about chunk load came when no space started')
            return
        else:
            destrFilenames = BigWorld.wg_getChunkDestrFilenames(self.__spaceID, chunkID)
            if destrFilenames is None:
                LOG_ERROR("Can't get destructibles filenames list for space %s, chunk %s" % (self.__spaceID, chunkID))
                return
            for destrIndex in xrange(numDestructibles):
                self.__setDestructibleInitialState(chunkID, destrIndex)

            self.__loadedChunkIDs.add(chunkID)
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
        if chunkID in self.__loadedChunkIDs:
            self.__loadedChunkIDs.remove(chunkID)
        if self.__effectsResourceRefs.has_key(chunkID):
            del self.__effectsResourceRefs[chunkID]

    def isChunkLoaded(self, chunkID):
        return chunkID in self.__loadedChunkIDs

    def orderDestructibleDestroy(self, chunkID, dmgType, destrData, isNeedAnimation):
        if chunkID in self.__loadedChunkIDs:
            self.__destroyDestructible(chunkID, dmgType, destrData, isNeedAnimation)
        else:
            entry = (dmgType, destrData, isNeedAnimation)
            self.__destructiblesWaitDestroy.setdefault(chunkID, []).append(entry)

    def _addController(self, chunkID, ctrl):
        self.__ctrls[chunkID] = ctrl

    def _delController(self, chunkID):
        if self.__ctrls.has_key(chunkID):
            del self.__ctrls[chunkID]

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

    def __destroyDestructible(self, chunkID, dmgType, destData, isNeedAnimation):
        if dmgType == _DAMAGE_TYPE_FALL:
            destrIndex, fallDirYaw, fallSpeed = decodeFallenDestructible(destData)
            self.__dropDestructible(chunkID, destrIndex, fallDirYaw, fallSpeed, isNeedAnimation)
        elif dmgType == _DAMAGE_TYPE_FRAGILE:
            self.__destroyFragile(chunkID, destData, isNeedAnimation)
        elif dmgType == _DAMAGE_TYPE_MODULE:
            destrIndex, matKind, isShotDamage = decodeDestructibleModule(destData)
            self.__destroyModule(chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage)

    def __setDestructibleInitialState(self, chunkID, destrIndex):
        filename = BigWorld.wg_getDestructibleFilename(self.__spaceID, chunkID, destrIndex)
        if filename is None:
            return
        else:
            filename = re.sub('/lod./', '/lod0/', filename)
            desc = g_cache.getDescByFilename(filename)
            if desc is None:
                return
            type = desc['type']
            if type == DESTR_TYPE_FRAGILE or type == DESTR_TYPE_STRUCTURE:
                fashion = _getOrCreateFashion(self.__spaceID, chunkID, destrIndex)
                fashion.isDestroyed = False
            if type == DESTR_TYPE_STRUCTURE:
                for moduleKind, moduleDesc in desc['modules'].iteritems():
                    self.__startLifetimeEffect(chunkID, destrIndex, moduleKind, moduleDesc)

            else:
                self.__startLifetimeEffect(chunkID, destrIndex, 0, desc)
            return

    def __destroyFragile(self, chunkID, destrIndex, isNeedAnimation):
        self.__stopLifetimeEffect(chunkID, destrIndex, 0)
        BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, partial(self.__setDestructibleState, self.__spaceID, chunkID, destrIndex, True))
        desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
        if desc is None:
            LOG_ERROR('Destructible descriptor is not available, chunkID: %i, destrIndex: %i' % (chunkID, destrIndex))
            return
        else:
            self.__launchEffect(chunkID, destrIndex, desc, 'decayEffect')
            if isNeedAnimation:
                self.__launchEffect(chunkID, destrIndex, desc, 'effect')
            return

    def __destroyModule(self, chunkID, destrIndex, matKind, isNeedAnimation, isShotDamage):
        if self.__isModuleDamaged(chunkID, destrIndex, matKind):
            return
        else:
            self.__stopLifetimeEffect(chunkID, destrIndex, matKind)
            desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
            if desc is None:
                LOG_ERROR('Destructible descriptor is not available, chunkID: %i, destrIndex: %i' % (chunkID, destrIndex))
                return
            destroyDepends = desc['destroyDepends'].get(matKind, [])
            kindsToHide = [matKind]
            kindsToHide += destroyDepends
            for kind in destroyDepends:
                dependModuleDesc = desc['modules'][kind]
                kindsToHide.append(dependModuleDesc['destroyedMat'])

            moduleDesc = desc['modules'][matKind]
            destroyedMat = moduleDesc['destroyedMat']
            BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, partial(self.__setDestructibleMaterialsVisible, self.__spaceID, chunkID, destrIndex, [destroyedMat], kindsToHide))
            if isShotDamage:
                unregisterCallback = partial(self.__unregisterModuleEffect, self.__spaceID, chunkID, destrIndex, matKind)
                decayEffectID = self.__launchEffect(chunkID, destrIndex, moduleDesc, 'decayEffect', unregisterCallback)
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
                    if player is not None:
                        player.terrainEffects.stop(staticEffectID)

            if isNeedAnimation:
                if isShotDamage:
                    coreEffectType = 'hitEffect'
                else:
                    coreEffectType = 'ramEffect'
                self.__launchEffect(chunkID, destrIndex, moduleDesc, coreEffectType)
                for kind in undamagedDepands:
                    self.__launchEffect(chunkID, destrIndex, moduleDesc, 'ramEffect')

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
                            self.__destroyModule(chunkID, destrIndex, dependKind, isNeedAnimation, False)
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
                        if player is not None:
                            player.terrainEffects.stop(staticEffectID)

                BigWorld.callback(DESTRUCTIBLE_HIDING_DELAY, partial(self.__setDestructibleMaterialsVisible, self.__spaceID, chunkID, destrIndex, [], kindsToHide))
            return

    def __getDamagedKinds(self, chunkID, destrIndex):
        desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
        if desc is None:
            LOG_ERROR('Destructible descriptor is not available, chunkID: %i, destrIndex: %i' % (chunkID, destrIndex))
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
            LOG_ERROR('Destructible descriptor is not available, chunkID: %i, destrIndex: %i' % (chunkID, destrIndex))
            return
        else:
            undamagedKinds = []
            for kind in desc['modules'].iterkeys():
                if not self.__isModuleDamaged(chunkID, destrIndex, kind):
                    undamagedKinds.append(kind)

            return undamagedKinds

    def __launchEffect(self, chunkID, destrIndex, desc, effectType, callbackOnStop=None):
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
                    LOG_ERROR("Can't find hardpoint %s in model %s" % (desc['effectHP'], desc['filename']))
                    return
                dir = hpMatrix.applyVector((0, 0, 1))
                pos = hpMatrix.translation
                scale = desc['effectScale']
            player = BigWorld.player()
            if player is None:
                return
            effectStuff = random.choice(effectVars)
            stages, effectList = effectStuff
            effectID = player.terrainEffects.addNew(pos, effectList, stages, callbackOnStop, dir=dir, scale=scale)
            return effectID

    def __startLifetimeEffect(self, chunkID, destrIndex, moduleKind, desc):
        chance = desc.get('lifetimeEffectChance')
        if chance is None or random.random() > chance:
            return
        else:
            lifetimeEffectID = self.__launchEffect(chunkID, destrIndex, desc, 'lifetimeEffect')
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
            if player is not None:
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

    def __setDestructibleMaterialsVisible(self, spaceID, chunkID, destrIndex, kindsToShow, kindsToHide):
        if spaceID != self.__spaceID:
            return
        fashion = _getOrCreateFashion(spaceID, chunkID, destrIndex)
        for kind in kindsToShow:
            fashion.setMaterialKindVisible(kind, True)
            if kind >= DESTRUCTIBLE_MATKIND.DAMAGED_MIN and kind <= DESTRUCTIBLE_MATKIND.DAMAGED_MAX:
                fashion.setEnableDrawMergedModel(False)

        for kind in kindsToHide:
            fashion.setMaterialKindVisible(kind, False)
            if kind >= DESTRUCTIBLE_MATKIND.NORMAL_MIN and kind <= DESTRUCTIBLE_MATKIND.NORMAL_MAX:
                fashion.setEnableDrawMergedModel(False)

    def __setDestructibleState(self, spaceID, chunkID, destrIndex, isDestroyed):
        if spaceID != self.__spaceID:
            return
        fashion = _getOrCreateFashion(spaceID, chunkID, destrIndex)
        fashion.isDestroyed = isDestroyed
        fashion.setEnableDrawMergedModel(not isDestroyed)

    def __dropDestructible(self, chunkID, destrIndex, fallDirYaw, fallSpeed, isNeedAnimation):
        self.__stopLifetimeEffect(chunkID, destrIndex, 0)
        if isNeedAnimation:
            self.__launchFallEffect(chunkID, destrIndex, 'fractureEffect', fallDirYaw)
            touchdownCallback = partial(self.__launchFallEffect, chunkID, destrIndex, 'touchdownEffect', fallDirYaw)
        else:
            touchdownCallback = None
        fashion = _getOrCreateFashion(self.__spaceID, chunkID, destrIndex)
        fashion.enableModelCompound = False
        initialMatrix = self.__getDestrInitialMatrix(chunkID, destrIndex)
        g_destructiblesAnimator.showFall(self.__spaceID, chunkID, destrIndex, fallDirYaw, fallSpeed, isNeedAnimation, initialMatrix, touchdownCallback)
        return

    def __launchFallEffect(self, chunkID, destrIndex, effectName, fallDirYaw):
        player = BigWorld.player()
        if player is None:
            return
        else:
            desc = g_cache.getDestructibleDesc(self.__spaceID, chunkID, destrIndex)
            if desc is None:
                LOG_ERROR('Destructible descriptor is not available, chunkID: %i, destrIndex: %i' % (chunkID, destrIndex))
                return
            effectVars = desc.get(effectName)
            if effectVars is None:
                return
            effectStuff = random.choice(effectVars)
            stages, effectList = effectStuff
            chunkMatrix = BigWorld.wg_getChunkMatrix(self.__spaceID, chunkID)
            destrMatrix = BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex)
            pos = chunkMatrix.translation + destrMatrix.translation
            dir = Math.Vector3(math.sin(fallDirYaw), 0.0, math.cos(fallDirYaw))
            if desc['type'] == DESTR_TYPE_TREE:
                treeScale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
                scale = 1.0 + (treeScale - 1.0) * _TREE_EFFECTS_SCALE_RATIO
            else:
                scale = desc['effectScale']
            player.terrainEffects.addNew(pos, effectList, stages, None, dir=dir, scale=scale)
            return

    def __getDestrInitialMatrix(self, chunkID, destrIndex):
        return self.__destrInitialMatrices.setdefault((chunkID, destrIndex), BigWorld.wg_getDestructibleMatrix(self.__spaceID, chunkID, destrIndex))


def _extractEffectLists(desc):
    type = desc['type']
    effectLists = []
    if type == DESTR_TYPE_TREE or type == DESTR_TYPE_FALLING_ATOM:
        effTypes = ('fractureEffect', 'touchdownEffect')
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


def _getOrCreateFashion(spaceID, chunkID, destrIndex):
    fashion = BigWorld.wg_getChunkModelFashion(spaceID, chunkID, destrIndex)
    if fashion is None:
        fashion = BigWorld.WGMaterialDisabler()
        BigWorld.wg_setChunkModelFashion(spaceID, chunkID, destrIndex, fashion)
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
        self.__prevFallenDestructibles = frozenset(self.fallenDestructibles)
        for fallData in self.fallenDestructibles:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, _DAMAGE_TYPE_FALL, fallData, False)

        self.__prevDestroyedFragiles = frozenset(self.destroyedFragiles)
        for fragileData in self.destroyedFragiles:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, _DAMAGE_TYPE_FRAGILE, fragileData, False)

        self.__prevDestroyedModules = frozenset(self.destroyedModules)
        for moduleData in self.destroyedModules:
            g_destructiblesManager.orderDestructibleDestroy(chunkID, _DAMAGE_TYPE_MODULE, moduleData, False)

    def onLeaveWorld(self):
        g_destructiblesManager._delController(self.__chunkID)

    def isDestructibleBroken(self, itemIndex, matKind, destrType):
        if destrType == DESTR_TYPE_FRAGILE:
            for fragileData in self.destroyedFragiles:
                if fragileData == itemIndex:
                    return True

        elif destrType == DESTR_TYPE_STRUCTURE:
            for moduleData in self.destroyedModules:
                itemIndex_, matKind_, _ = decodeDestructibleModule(moduleData)
                if itemIndex_ == itemIndex and matKind_ == matKind:
                    return True

        else:
            for fallData in self.fallenDestructibles:
                if fallData >> 8 == itemIndex:
                    return True

        return False

    def set_fallenDestructibles(self, prev):
        prev = self.__prevFallenDestructibles
        curr = frozenset(self.fallenDestructibles)
        self.__prevFallenDestructibles = curr
        for fallData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, _DAMAGE_TYPE_FALL, fallData, True)

    def set_destroyedFragiles(self, prev):
        prev = self.__prevDestroyedFragiles
        curr = frozenset(self.destroyedFragiles)
        self.__prevDestroyedFragiles = curr
        for fragileData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, _DAMAGE_TYPE_FRAGILE, fragileData, True)

    def set_destroyedModules(self, prev):
        prev = self.__prevDestroyedModules
        curr = frozenset(self.destroyedModules)
        self.__prevDestroyedModules = curr
        for moduleData in curr.difference(prev):
            g_destructiblesManager.orderDestructibleDestroy(self.__chunkID, _DAMAGE_TYPE_MODULE, moduleData, True)


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

    def showFall(self, spaceID, chunkID, destrIndex, fallDirYaw, discreteInitSpeed, isNeedAnimation, initialMatrix, touchdownCallback=None):
        desc = g_cache.getDestructibleDesc(spaceID, chunkID, destrIndex)
        if desc is None:
            LOG_ERROR('Destructible descriptor is not available, chunkID: %i, destrIndex: %i' % (chunkID, destrIndex))
            return
        else:
            destrMatrix = Math.Matrix(initialMatrix)
            chunkMatrix = BigWorld.wg_getChunkMatrix(spaceID, chunkID)
            scale = destrMatrix.applyVector((0.0, 1.0, 0.0)).length
            height = desc['height'] * scale
            mass = desc['mass'] * scale * scale * scale
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
            root = translation + chunkMatrix.translation
            fallDir = fallYawRot.applyVector((0.0, 0.0, 1.0))
            collisionHeight = BigWorld.wg_getDestructibleHeight(spaceID, chunkID, destrIndex)
            if not collisionHeight:
                collisionHeight = height
            pitchConstr = self.__detectPitchConstraint(spaceID, chunkID, root, fallDir, collisionHeight * 0.15, collisionHeight * 0.85, destrIndex)
            body = {'pitch': pitch,
             'pitchSpeed': pitchSpeed,
             'inertiaMoment': inertiaMoment,
             'mass': mass,
             'height': height,
             'springAngle': desc['springAngle'],
             'springStiffnes': desc['springStiffnes'] * scale * scale,
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
                k = 0.5 * height * body['springStiffnes']
                pitch = (9.8 * mass * math.sin(pitchConstr) - k * (body['springAngle'] - pitchConstr)) / k
                body['pitch'] = pitch
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
        torque = 4.9 * body['height'] * body['mass'] * math.sin(pitch) - body['pitchSpeed'] * body['airResist'] * mp
        if pitch + body['springAngle'] > pitchConstr:
            touchdownCallback = body.get('touchdownCallback')
            if touchdownCallback is not None:
                touchdownCallback()
                del body['touchdownCallback']
            anglePen = pitch + body['springAngle'] - pitchConstr
            torque -= anglePen * body['springStiffnes'] * mp + body['pitchSpeed'] * body['springResist'] * mp
        body['pitchSpeed'] += dt * torque / body['inertiaMoment']
        body['simulationTime'] += dt
        if abs(body['pitchSpeed'] + torque) < self.__STOP_SIMULATION_EPSILON or body['simulationTime'] > self.__MAX_SIMULATION_DURATION:
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
        spaceID = body['spaceID']
        BigWorld.wg_setDestructibleMatrix(spaceID, body['chunkID'], body['destrIndex'], m)

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
