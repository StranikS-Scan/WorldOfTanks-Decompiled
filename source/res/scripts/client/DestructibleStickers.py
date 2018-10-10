# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DestructibleStickers.py
import BigWorld
from AvatarInputHandler import mathUtils
import VehicleStickers

class DestructibleStickers(object):

    def __init__(self, model, nodeToAttach):
        self.__model = model
        self.__stickerModel = BigWorld.WGStickerModel()
        self.__stickerModel.setLODDistance(1000.0)
        self.__stickerModel.setupSuperModel(model, mathUtils.createIdentityMatrix())
        nodeToAttach.attach(self.__stickerModel)
        self.__damageStickers = {}

    def destroy(self):
        if self.__model is None:
            return
        else:
            if self.__stickerModel.attached:
                self.__model.detach(self.__stickerModel)
            self.__stickerModel.clear()
            self.__damageStickers.clear()
            return

    def addDamageSticker(self, code, stickerID, segStart, segEnd):
        if code in self.__damageStickers:
            return
        elif self.__stickerModel is None:
            return
        else:
            handle = self.__stickerModel.addDamageSticker(stickerID, segStart, segEnd)
            self.__damageStickers[code] = VehicleStickers.DamageSticker(stickerID, segStart, segEnd, handle)
            return

    def delDamageSticker(self, code):
        if self.__stickerModel is None:
            return
        else:
            damageSticker = self.__damageStickers.get(code)
            if damageSticker is not None:
                if damageSticker.handle is not None:
                    self.__stickerModel.delSticker(damageSticker.handle)
                del self.__damageStickers[code]
            return
