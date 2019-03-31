# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleStickers.py
# Compiled at: 2011-11-29 19:01:06
import BigWorld
import Account
import Vehicle
import items
import Event
import Math
import BattleReplay
from debug_utils import *

class VehicleStickers:

    def __init__(self, vDesc, emblemSlots):
        self.__slotsByType = {}
        self.__texParamsBySlotType = {}
        self.__isLoadingClanEmblems = False
        self.__numTextures = 0
        self.__clanID = 0
        self.__model = None
        self.__parentNode = None
        self.__isDamaged = False
        g_cache = items.vehicles.g_cache
        playerEmblems = g_cache.playerEmblems()
        texSize = playerEmblems['textureSize']
        texName, texX, texY = playerEmblems['descrs'][vDesc.playerEmblemID]['texture']
        tex = BigWorld.PyTextureProvider(texName)
        texX *= texSize
        texY *= texSize
        self.__texParamsBySlotType['player'] = (0, Math.Vector4(texX / float(tex.width), texY / float(tex.height), texSize / float(tex.width), texSize / float(tex.height)))
        damageTexName = g_cache.damageStickers['textureName']
        texNames = [texName, damageTexName]
        for slot in emblemSlots:
            slotType = slot[5]
            if slotType != 'player':
                if not self.__texParamsBySlotType.has_key(slotType):
                    self.__texParamsBySlotType[slotType] = (len(texNames), Math.Vector4(0, 0, 1.0, 1.0))
                    texNames.append('')
            if self.__slotsByType.has_key(slotType):
                self.__slotsByType[slotType].append(slot)
            else:
                self.__slotsByType[slotType] = [slot]

        self.__numTextures = len(texNames)
        self.__stickerModel = BigWorld.WGStickerModel(texNames)
        self.__stickerModel.setLODDistances(vDesc.type.emblemsLodDist, vDesc.type.damageStickersLodDist)
        return

    def __destroy__(self):
        self.__isLoadingClanEmblems = False
        self.detachStickers()

    def attachStickers(self, model, parentNode, isDamaged):
        self.detachStickers()
        self.__model = model
        self.__parentNode = parentNode
        self.__isDamaged = isDamaged
        self.__parentNode.attach(self.__stickerModel)
        replayCtrl = BattleReplay.g_replayCtrl
        for slotType, slots in self.__slotsByType.iteritems():
            if slotType == 'player' or self.__clanID == 0 or replayCtrl.isPlaying and replayCtrl.isOffline:
                self.__doAttachStickers(slotType)
            elif slotType == 'clan':
                if self.__isLoadingClanEmblems:
                    return
                self.__isLoadingClanEmblems = True
                fileCache = Account.g_accountRepository.customFilesCache
                fileServerSettings = Account.g_accountRepository.fileServerSettings
                clan_emblems = fileServerSettings['clan_emblems']
                url = None
                try:
                    url = clan_emblems['url_template'] % self.__clanID
                except:
                    LOG_ERROR('Failed to attach stickers to the vehicle - server returned incorrect url format: %s' % clan_emblems['url_template'])
                    return

                fileCache.get(url, clan_emblems['cache_life_time'], self.__onClanEmblemLoaded)

        return

    def detachStickers(self):
        if self.__model is None:
            return
        else:
            self.__parentNode.detach(self.__stickerModel)
            for i in xrange(0, self.__numTextures):
                self.__stickerModel.clear(i)

            self.__model = None
            self.__parentNode = None
            self.__isDamaged = False
            return

    def addDamageSticker(self, texCoords, segStart, segEnd, sizes, rayUp):
        if self.__model is None:
            return 0
        else:
            return self.__stickerModel.addSticker(1, texCoords, self.__model, segStart, segEnd, sizes, rayUp)

    def delDamageSticker(self, handle):
        if self.__model is not None:
            self.__stickerModel.delSticker(handle)
        return

    def setClanID(self, clanID):
        if self.__clanID == clanID:
            return
        else:
            self.__clanID = clanID
            if self.__model is not None:
                self.attachStickers(self.__model, self.__parentNode, self.__isDamaged)
            return

    def setAlphas(self, emblemAlpha, dmgStickerAlpha):
        self.__stickerModel.setAlphas(emblemAlpha, dmgStickerAlpha)

    def __doAttachStickers(self, slotType):
        if self.__model is None:
            return
        else:
            texSlotType = 'player' if slotType == 'clan' and self.__clanID == 0 else slotType
            texIndex, texCoords = self.__texParamsBySlotType[texSlotType]
            for rayStart, rayEnd, rayUp, size, hideIfDamaged, _ in self.__slotsByType[slotType]:
                if hideIfDamaged and self.__isDamaged:
                    continue
                sizes = Math.Vector2(size, size)
                self.__stickerModel.addSticker(texIndex, texCoords, self.__model, rayStart, rayEnd, sizes, rayUp)

            return

    def __onClanEmblemLoaded(self, url, data):
        if not self.__isLoadingClanEmblems:
            return
        self.__isLoadingClanEmblems = False
        try:
            texIndex, texCoords = self.__texParamsBySlotType['clan']
            self.__stickerModel.setTextureData(texIndex, data)
            self.__doAttachStickers('clan')
        except Exception:
            LOG_CURRENT_EXCEPTION()
