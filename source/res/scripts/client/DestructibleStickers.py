# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DestructibleStickers.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
import CGF
import GpuDecals
import math_utils
import VehicleStickers
from VehicleEffects import DamageFromShotDecoder
from constants import VEHICLE_HIT_EFFECT
from items.components.component_constants import INVALID_EFFECT_INDEX
from helpers.prefab_effects import resolvePrefabStickerID, resolveDamageStickerPrefab
from cgf_modules import game_events
if typing.TYPE_CHECKING:
    from VehicleStickers import DamageStickerData
    from Compound import Compound
_logger = logging.getLogger(__name__)

class DestructibleStickers(object):
    __LOD_DISTANCE = 1000.0

    def __init__(self, spaceID, compound, partIdx, gameObject):
        self.__model = compound.getPartGeometryLink(partIdx)
        cgfQueue = CGF.CommandQueue(spaceID)
        cgfQueue.createComponent(gameObject, GpuDecals.GpuDecalsReceiverComponent)
        self.__gameObject = gameObject
        self.__stickerModel = BigWorld.WGStickerModel(spaceID)
        self.__stickerModel.setLODDistance(self.__LOD_DISTANCE)
        self.__stickerModel.setupSuperModel(self.__model, math_utils.createIdentityMatrix())
        self.__nodeToAttach = compound.node('root')
        self.__nodeToAttach.attach(self.__stickerModel)
        self.__damageStickers = {}
        self.__parametrizedDamageStickers = {}

    def destroy(self):
        if self.__model is None:
            return
        else:
            self.__damageStickers.clear()
            self.__parametrizedDamageStickers.clear()
            if self.__stickerModel.attached and self.__nodeToAttach is not None:
                self.__nodeToAttach.detach(self.__stickerModel)
            self.__stickerModel.clear()
            self.__stickerModel = None
            self.__nodeToAttach = None
            self.__gameObject.removeComponent(GpuDecals.GpuDecalsReceiverComponent)
            self.__gameObject = None
            self.__model = None
            return

    def addDamageSticker(self, code, stickerID, prefabEffIndex, data, collisionComponent, isActive):
        prefabEffIndex, hitType = resolveDamageStickerPrefab(prefabEffIndex, data.hitType)
        prefabEffIndex = INVALID_EFFECT_INDEX
        if prefabEffIndex != INVALID_EFFECT_INDEX and hitType != VEHICLE_HIT_EFFECT.INVALID:
            self.__addParametrizedDamageSticker(code, prefabEffIndex, hitType, data, collisionComponent, isActive)
        else:
            self.__addLegacyDamageSticker(code, stickerID, data)

    def delDamageSticker(self, code):
        uid = self.__parametrizedDamageStickers.pop(code, None)
        if uid is not None:
            CGF.postEvent(self.__gameObject.spaceID, game_events.RemoveDamageStickerEvent(uid))
            return
        else:
            damageSticker = self.__damageStickers.pop(code, None)
            if damageSticker is not None:
                self.__delLegacyDamageSticker(damageSticker)
            return

    def __addParametrizedDamageSticker(self, code, prefabEffIndex, hitType, data, collisionComponent, isActive):
        stickerID = resolvePrefabStickerID(prefabEffIndex, hitType)
        if stickerID == INVALID_EFFECT_INDEX:
            return
        elif code in self.__parametrizedDamageStickers:
            return
        else:
            collisionResult = DamageFromShotDecoder.collideHitPoint(data.componentIdx, data.segStart, data.segEnd, collisionComponent)
            if collisionResult is None:
                _logger.warning('Unable to add parametrized damage sticker. Collision result is None.')
                return
            uid = hash(code)
            hitPoint, hitDir, normal = collisionResult
            CGF.postEvent(self.__gameObject.spaceID, game_events.AddDamageStickerEvent(uid, self.__gameObject, hitPoint, hitDir, normal, game_events.GunShellInfo(data.caliber, data.shellType), hitType, isActive, stickerID))
            _logger.debug('Parametrized damage sticker add with uid: %i', uid)
            self.__parametrizedDamageStickers[code] = uid
            return

    def __addLegacyDamageSticker(self, code, stickerID, data):
        if self.__stickerModel is None:
            return
        elif code in self.__damageStickers:
            return
        else:
            handle = self.__stickerModel.addDamageSticker(stickerID, data.segStart, data.segEnd)
            if handle is not None:
                self.__damageStickers[code] = VehicleStickers.DamageSticker(stickerID, handle, data)
            return

    def __delLegacyDamageSticker(self, damageSticker):
        if self.__stickerModel is None:
            return
        else:
            if damageSticker.handle:
                self.__stickerModel.delSticker(damageSticker.handle)
            return
