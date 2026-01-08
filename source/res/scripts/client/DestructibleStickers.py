# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DestructibleStickers.py
import logging
import typing
import BigWorld
import CGF
import GpuDecals
import math_utils
import VehicleStickers
from VehicleEffects import DamageFromShotDecoder
from cgf_modules import game_events
if typing.TYPE_CHECKING:
    from VehicleStickers import DamageStickerData
    from Compound import Compound
_logger = logging.getLogger(__name__)

class DestructibleStickers(object):
    __LOD_DISTANCE = 1000.0

    def __init__(self, spaceID, compound, partIdx, gameObject):
        self.__model = compound.getPartGeometryLink(partIdx)
        self.__gameObject = gameObject
        self.__gameObject.createComponent(GpuDecals.GpuDecalsReceiverComponent)
        self.__stickerModel = BigWorld.WGStickerModel(spaceID)
        self.__stickerModel.setLODDistance(self.__LOD_DISTANCE)
        self.__stickerModel.setupSuperModel(self.__model, math_utils.createIdentityMatrix())
        self.__nodeToAttach = compound.node('root')
        self.__nodeToAttach.attach(self.__stickerModel)
        self.__damageStickers = {}

    def destroy(self):
        if self.__model is None:
            return
        else:
            self.__damageStickers.clear()
            if self.__stickerModel.attached and self.__nodeToAttach is not None:
                self.__nodeToAttach.detach(self.__stickerModel)
            self.__stickerModel.clear()
            self.__stickerModel = None
            self.__nodeToAttach = None
            self.__gameObject.removeComponentByType(GpuDecals.GpuDecalsReceiverComponent)
            self.__gameObject = None
            self.__model = None
            return

    def addDamageSticker(self, code, stickerID, data, collisionComponent, isActive):
        if data.isParametrized:
            handle = self.__addParametrizedDamageSticker(code, stickerID, data, collisionComponent, isActive)
        else:
            handle = self.__addDamageSticker(code, stickerID, data)
        if handle is not None:
            self.__damageStickers[code] = VehicleStickers.DamageSticker(stickerID, handle, data)
        return

    def delDamageSticker(self, code):
        damageSticker = self.__damageStickers.pop(code, None)
        if damageSticker is not None:
            if damageSticker.data.isParametrized:
                self.__delParametrizedDamageSticker(damageSticker)
            else:
                self.__delDamageSticker(damageSticker)
        return

    def __addParametrizedDamageSticker(self, code, stickerID, data, collisionComponent, isActive):
        sticker = self.__damageStickers.get(code)
        if sticker is not None and sticker.handle:
            return
        else:
            collisionResult = DamageFromShotDecoder.collideHitPoint(data.componentIdx, data.segStart, data.segEnd, collisionComponent)
            if collisionResult is None:
                _logger.warning('Unable to add parametrized damage sticker. Collision result is None.')
                return
            uid = hash(code)
            hitPoint, hitDir, normal = collisionResult
            CGF.postEvent(self.__gameObject.spaceID, game_events.AddDamageStickerEvent(uid, self.__gameObject, hitPoint, hitDir, normal, game_events.GunShellInfo(data.caliber, data.shellType), data.hitType, isActive, stickerID))
            _logger.debug('Parametrized damage sticker add with uid: %i', uid)
            return uid

    def __delParametrizedDamageSticker(self, damageSticker):
        if damageSticker.handle:
            CGF.postEvent(self.__gameObject.spaceID, game_events.RemoveDamageStickerEvent(damageSticker.handle))

    def __addDamageSticker(self, code, stickerID, data):
        if self.__stickerModel is None:
            return
        else:
            sticker = self.__damageStickers.get(code)
            return None if sticker is not None and sticker.handle else self.__stickerModel.addDamageSticker(stickerID, data.segStart, data.segEnd)

    def __delDamageSticker(self, damageSticker):
        if self.__stickerModel is None:
            return
        else:
            if damageSticker.handle:
                self.__stickerModel.delSticker(damageSticker.handle)
            return
