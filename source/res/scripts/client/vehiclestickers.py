# Embedded file name: scripts/client/VehicleStickers.py
import BigWorld
from collections import namedtuple
import random
import math
import constants
import Account
from gui.prb_control.prb_helpers import preQueueFunctionalProperty
from gui.prb_control.settings import PREQUEUE_SETTING_NAME
from gui.shared import g_eventsCache
import items
from items import vehicles
import Math
import BattleReplay
from debug_utils import *
from gui import game_control
from VehicleEffects import TankComponentNames
TextureParams = namedtuple('TextureParams', ('textureName', 'bumpTextureName', 'mirror'))

class StickerAttributes():
    IS_INSCRIPTION = 1
    DOUBLESIDED = 2
    IS_MIRRORED = 4


class SlotTypes():
    CLAN = 'clan'
    PLAYER = 'player'
    INSCRIPTION = 'inscription'
    INSIGNIA_ON_GUN = 'insigniaOnGun'


class ModelStickers():

    def __init__(self, vDesc, emblemSlots, onHull = True, insigniaRank = 0):
        self.__slotsByType = {}
        self.__texParamsBySlotType = {}
        self.__isLoadingClanEmblems = False
        self.__clanID = 0
        self.__vehicleDescriptor = vDesc
        self.__model = None
        self.__parentNode = None
        self.__isDamaged = False
        self.__calcTexParams(vDesc, emblemSlots, onHull, insigniaRank)
        if 'clan' in self.__texParamsBySlotType:
            self.__texParamsBySlotType[SlotTypes.CLAN] = [TextureParams('', '', False)]
        self.__stickerModel = BigWorld.WGStickerModel()
        self.__stickerModel.setLODDistances(vDesc.type.emblemsLodDist, vDesc.type.damageStickersLodDist)
        return

    def __calcTexParams(self, vDesc, emblemSlots, onHull, insigniaRank):
        g_cache = items.vehicles.g_cache
        customizationCache = g_cache.customization(vDesc.type.customizationNationID)
        playerEmblemsCache = g_cache.playerEmblems()[1]
        inscriptionsCache = customizationCache['inscriptions']
        for slot in emblemSlots:
            slotType = slot.type
            self.__slotsByType.setdefault(slotType, []).append(slot)
            self.__texParamsBySlotType.setdefault(slotType, [])
            if slotType == SlotTypes.INSIGNIA_ON_GUN:
                insigniaParams = self.__getTexParamsForInsignia(vDesc, insigniaRank)
                self.__texParamsBySlotType[slotType].append(insigniaParams)
                continue
            elif slotType == SlotTypes.CLAN:
                self.__texParamsBySlotType[slotType] = [TextureParams('', '', False)]
                continue
            emblemsDesc = None
            emblemsCache = None
            if slotType == SlotTypes.PLAYER:
                emblemsDesc = vDesc.playerEmblems[0:2] if onHull else vDesc.playerEmblems[2:]
                emblemsCache = playerEmblemsCache
            elif slotType == SlotTypes.INSCRIPTION:
                emblemsDesc = vDesc.playerInscriptions[0:2] if onHull else vDesc.playerInscriptions[2:]
                emblemsCache = inscriptionsCache
            if emblemsDesc is None:
                continue
            descIdx = len(self.__slotsByType[slotType]) - 1
            emblemID = emblemsDesc[descIdx][0]
            if emblemID is None:
                self.__texParamsBySlotType[slotType].append(None)
                continue
            texName, bumpTexName, _, isMirrored = emblemsCache[emblemID][2:6]
            texParams = TextureParams(texName, bumpTexName, isMirrored)
            self.__texParamsBySlotType[slotType].append(texParams)

        return

    def __getTexParamsForInsignia(self, vDesc, insigniaRank):
        g_cache = items.vehicles.g_cache
        customizationCache = g_cache.customization(vDesc.type.customizationNationID)
        insigniaCache = customizationCache['insigniaOnGun']
        return TextureParams(*insigniaCache.get(insigniaRank, ('', '', False)))

    def __destroy__(self):
        self.__isLoadingClanEmblems = False
        self.detachStickers()

    def attachStickers(self, model, parentNode, isDamaged):
        self.detachStickers()
        self.__model = model
        self.__parentNode = parentNode
        self.__isDamaged = isDamaged
        self.__parentNode.attach(self.__stickerModel)
        isHBParticipatingVehicle = False
        if self.preQueueFunctional is not None and self.preQueueFunctional.getQueueType() == constants.QUEUE_TYPE.HISTORICAL:
            battleId = self.preQueueFunctional.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID)
            battle = g_eventsCache.getHistoricalBattles().get(battleId)
            if battle is not None and battle.canParticipateWith(self.__vehicleDescriptor.type.compactDescr):
                isHBParticipatingVehicle = True
        replayCtrl = BattleReplay.g_replayCtrl
        for slotType, slots in self.__slotsByType.iteritems():
            if slotType != SlotTypes.CLAN or self.__clanID == 0 or replayCtrl.isPlaying and replayCtrl.isOffline:
                self.__doAttachStickers(slotType)
            elif slotType == SlotTypes.CLAN:
                arenaBonusType = None
                if hasattr(BigWorld.player(), 'arena'):
                    arenaBonusType = BigWorld.player().arena.bonusType
                if game_control.g_instance.roaming.isInRoaming() or arenaBonusType == constants.ARENA_BONUS_TYPE.HISTORICAL or isHBParticipatingVehicle or self.__isLoadingClanEmblems:
                    continue
                self.__isLoadingClanEmblems = True
                fileCache = Account.g_accountRepository.customFilesCache
                fileServerSettings = Account.g_accountRepository.fileServerSettings
                clan_emblems = fileServerSettings.get('clan_emblems')
                if clan_emblems is None:
                    continue
                url = None
                try:
                    url = clan_emblems['url_template'] % self.__clanID
                except:
                    LOG_ERROR('Failed to attach stickers to the vehicle - server returned incorrect url format: %s' % clan_emblems['url_template'])
                    continue

                fileCache.get(url, self.__onClanEmblemLoaded)

        return

    def detachStickers(self):
        if self.__model is None:
            return
        else:
            self.__parentNode.detach(self.__stickerModel)
            self.__stickerModel.clear()
            self.__model = None
            self.__parentNode = None
            self.__isDamaged = False
            return

    def addDamageSticker(self, texName, bumpTexName, segStart, segEnd, sizes, rayUp):
        if self.__model is None:
            return 0
        else:
            return self.__stickerModel.addSticker(texName, bumpTexName, self.__model, segStart, segEnd, sizes, rayUp, 0)

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

    @preQueueFunctionalProperty
    def preQueueFunctional(self):
        return None

    def __doAttachStickers(self, slotType):
        if self.__model is None or slotType == SlotTypes.CLAN and self.__clanID == 0:
            return
        else:
            slots = self.__slotsByType[slotType]
            for idx, (rayStart, rayEnd, rayUp, size, hideIfDamaged, _, isMirrored) in enumerate(slots):
                if hideIfDamaged and self.__isDamaged or self.__texParamsBySlotType[slotType][idx] is None:
                    continue
                texName, bumpTexName, isStickerMirrored = self.__texParamsBySlotType[slotType][idx]
                if texName == '' and slotType != SlotTypes.CLAN:
                    continue
                sizes = Math.Vector2(size, size)
                stickerAttributes = 0
                if slotType == SlotTypes.INSCRIPTION:
                    sizes.y *= 0.5
                    stickerAttributes |= StickerAttributes.IS_INSCRIPTION
                elif slotType == SlotTypes.INSIGNIA_ON_GUN:
                    stickerAttributes |= StickerAttributes.DOUBLESIDED
                if isMirrored and isStickerMirrored:
                    stickerAttributes |= StickerAttributes.IS_MIRRORED
                self.__stickerModel.addSticker(texName, bumpTexName, self.__model, rayStart, rayEnd, sizes, rayUp, stickerAttributes)

            return

    def __onClanEmblemLoaded(self, url, data):
        if not self.__isLoadingClanEmblems:
            return
        else:
            self.__isLoadingClanEmblems = False
            if data is None:
                return
            try:
                self.__stickerModel.setTextureData(data)
                self.__doAttachStickers(SlotTypes.CLAN)
            except Exception:
                LOG_CURRENT_EXCEPTION()

            return


class ComponentStickers(object):

    def __init__(self, stickers, damageStickers, alpha):
        self.stickers = stickers
        self.damageStickers = damageStickers
        self.alpha = alpha


class DamageSticker(object):

    def __init__(self, textureName, bumpTextureName, rayStart, rayEnd, sizes, rayUp, handle):
        self.textureName = textureName
        self.bumpTextureName = bumpTextureName
        self.rayStart = rayStart
        self.rayEnd = rayEnd
        self.sizes = sizes
        self.rayUp = rayUp
        self.handle = handle


class VehicleStickers(object):

    def setClanID(self, clanID):
        for componentStickers in self.__stickers.itervalues():
            componentStickers.stickers.setClanID(clanID)

    def __setAlpha(self, alpha):
        multipliedAlpha = alpha * self.__defaultAlpha
        for componentStickers in self.__stickers.itervalues():
            actualAlpha = multipliedAlpha if self.__show else 0.0
            componentStickers.stickers.setAlphas(actualAlpha, actualAlpha)
            componentStickers.alpha = multipliedAlpha

    alpha = property(lambda self: self.__stickers[TankComponentNames.HULL].alpha, __setAlpha)

    def __setShow(self, show):
        self.__show = show
        for componentStickers in self.__stickers.itervalues():
            alpha = componentStickers.alpha if show else 0.0
            componentStickers.stickers.setAlphas(alpha, alpha)

    show = property(lambda self: self.__show, __setShow)
    COMPONENT_NAMES = (TankComponentNames.HULL, TankComponentNames.TURRET, TankComponentNames.GUN)
    __INSIGNIA_NODE_NAME = 'G'

    def __init__(self, vehicleDesc, insigniaRank = 0):
        self.__showEmblemsOnGun = vehicleDesc.turret['showEmblemsOnGun']
        self.__defaultAlpha = vehicleDesc.type.emblemsAlpha
        self.__show = True
        self.__animateGunInsignia = vehicleDesc.gun['animateEmblemSlots']
        self.__currentInsigniaRank = insigniaRank
        componentSlots = ((TankComponentNames.HULL, vehicleDesc.hull['emblemSlots']),
         (TankComponentNames.GUN if self.__showEmblemsOnGun else TankComponentNames.TURRET, vehicleDesc.turret['emblemSlots']),
         (TankComponentNames.TURRET if self.__showEmblemsOnGun else TankComponentNames.GUN, []),
         ('gunInsignia', vehicleDesc.gun['emblemSlots']))
        self.__stickers = {}
        for componentName, emblemSlots in componentSlots:
            modelStickers = ModelStickers(vehicleDesc, emblemSlots, componentName == TankComponentNames.HULL, insigniaRank)
            self.__stickers[componentName] = ComponentStickers(modelStickers, {}, 1.0)

    def getCurrentInsigniaRank(self):
        return self.__currentInsigniaRank

    def attach(self, modelsWithParentNodes, isDamaged, showDamageStickers):
        for componentName, (model, parentNode) in zip(VehicleStickers.COMPONENT_NAMES, modelsWithParentNodes):
            if model is None or parentNode is None:
                continue
            componentStickers = self.__stickers[componentName]
            componentStickers.stickers.attachStickers(model, parentNode, isDamaged)
            if showDamageStickers:
                for damageSticker in componentStickers.damageStickers:
                    if damageSticker.handle is not None:
                        componentStickers.stickers.delDamageSticker(damageSticker.handle)
                        damageSticker.handle = None
                        LOG_WARNING('Adding %s damage sticker to occupied slot' % componentName)
                    damageSticker.handle = componentStickers.stickers.addDamageSticker(damageSticker.textureName, damageSticker.bumpTextureName, damageSticker.rayStart, damageSticker.rayEnd, damageSticker.sizes, damageSticker.rayUp)

        gunModel, gunNode = modelsWithParentNodes[-1]
        if gunModel is None or gunNode is None:
            return
        else:
            if self.__animateGunInsignia:
                try:
                    gunNode = gunModel.root if isDamaged else gunModel.node(VehicleStickers.__INSIGNIA_NODE_NAME)
                except:
                    LOG_ERROR('Cannot attach gun decals to model "%s" - it does not have node named "G"' % gunModel.sources[0])
                    return

            else:
                gunNode = gunModel.root
            self.__stickers['gunInsignia'].stickers.attachStickers(gunModel, gunNode, isDamaged)
            return

    def detach(self):
        for componentStickers in self.__stickers.itervalues():
            componentStickers.stickers.detachStickers()
            for dmgSticker in componentStickers.damageStickers.itervalues():
                dmgSticker.handle = None

        return

    def addDamageSticker(self, code, componentName, stickerID, segStart, segEnd):
        componentStickers = self.__stickers[componentName]
        if componentStickers.damageStickers.has_key(code):
            return
        desc = items.vehicles.g_cache.damageStickers['descrs'][stickerID]
        texParams = random.choice(desc['variants'])
        textureName = texParams['texName']
        bumpTexName = texParams['bumpTexName']
        sizes = texParams['modelSizes']
        segment = segEnd - segStart
        segLen = segment.lengthSquared
        if segLen != 0:
            segStart -= 0.25 * segment / math.sqrt(segLen)
        angle = random.random() * math.pi * 2.0
        rotAxis = 0
        for i in xrange(1, 3):
            if abs(segment[i]) > abs(segment[rotAxis]):
                rotAxis = i

        up = Math.Vector3()
        up[(rotAxis + 1) % 3] = math.sin(angle)
        up[(rotAxis + 2) % 3] = math.cos(angle)
        handle = componentStickers.stickers.addDamageSticker(textureName, bumpTexName, segStart, segEnd, sizes, up)
        componentStickers.damageStickers[code] = DamageSticker(textureName, bumpTexName, segStart, segEnd, up, sizes, handle)

    def delDamageSticker(self, code):
        for componentStickers in self.__stickers.itervalues():
            damageSticker = componentStickers.damageStickers.get(code)
            if damageSticker is not None:
                if damageSticker.handle is not None:
                    componentStickers.stickers.delDamageSticker(damageSticker.handle)
                del componentStickers.damageStickers[code]

        return
