# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleStickers.py
from collections import namedtuple
import math
import BigWorld
from AvatarInputHandler import mathUtils
import items
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_WARNING
from helpers import dependency
import Math
import BattleReplay
from skeletons.gui.lobby_context import ILobbyContext
from vehicle_systems import stricted_loading
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames, TankNodeNames
from vehicle_systems.tankStructure import DetachedTurretPartIndexes, DetachedTurretPartNames
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Outfit

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


TextureParams = namedtuple('TextureParams', ('textureName', 'bumpTextureName', 'mirror'))

class StickerAttributes(object):
    IS_INSCRIPTION = 1
    DOUBLESIDED = 2
    IS_MIRRORED = 4
    IS_UV_PROPORTIONAL = 8


class SlotTypes(object):
    CLAN = 'clan'
    PLAYER = 'player'
    INSCRIPTION = 'inscription'
    INSIGNIA_ON_GUN = 'insigniaOnGun'
    FIXED_EMBLEM = 'fixedEmblem'
    FIXED_INSCRIPTION = 'fixedInscription'


class ModelStickers(object):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vDesc, emblemSlots, decals, onHull=True, insigniaRank=0):
        self.__slotsByType = {}
        self.__texParamsBySlotType = {}
        self.__isLoadingClanEmblems = False
        self.__clanID = 0
        self.__model = None
        self.__toPartRootMatrix = mathUtils.createIdentityMatrix()
        self.__parentNode = None
        self.__isDamaged = False
        self.__calcTexParams(vDesc, emblemSlots, decals, onHull, insigniaRank)
        if 'clan' in self.__texParamsBySlotType:
            self.__texParamsBySlotType[SlotTypes.CLAN] = [TextureParams('', '', False)]
        self.__stickerModel = BigWorld.WGStickerModel()
        self.__stickerModel.setLODDistance(vDesc.type.emblemsLodDist)
        return

    def __calcTexParams(self, vDesc, emblemSlots, decals, onHull, insigniaRank):
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
            descIdx = len(self.__slotsByType[slotType]) - 1
            emblemsCache = None
            emblemID = None
            if slotType in (SlotTypes.PLAYER, SlotTypes.INSCRIPTION):
                stickers = decals[slotType]
                if stickers:
                    sticker = stickers.getItem(descIdx)
                    if sticker:
                        texParams = TextureParams(sticker.texture, '', sticker.isMirrored)
                        self.__texParamsBySlotType[slotType].append(texParams)
                        continue
                    elif slotType == SlotTypes.PLAYER and not stickers.isLocked(descIdx):
                        emblemsCache = playerEmblemsCache
                        emblemID = vDesc.type.defaultPlayerEmblemID
                    else:
                        self.__texParamsBySlotType[slotType].append(TextureParams('', '', False))
                        continue
            elif slotType == SlotTypes.FIXED_EMBLEM:
                emblemsCache = playerEmblemsCache
                emblemID = slot.emblemId
            elif slotType == SlotTypes.FIXED_INSCRIPTION:
                emblemsCache = inscriptionsCache
                emblemID = slot.emblemId
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

    def attachStickers(self, model, parentNode, isDamaged, toPartRootMatrix=None):
        self.detachStickers()
        self.__model = model
        if toPartRootMatrix is not None:
            self.__toPartRootMatrix = toPartRootMatrix
        self.__parentNode = parentNode
        self.__isDamaged = isDamaged
        self.__stickerModel.setupSuperModel(self.__model, self.__toPartRootMatrix)
        self.__parentNode.attach(self.__stickerModel)
        replayCtrl = BattleReplay.g_replayCtrl
        accountRep = _getAccountRepository()
        for slotType, _ in self.__slotsByType.iteritems():
            if slotType != SlotTypes.CLAN or self.__clanID == 0 or replayCtrl.isPlaying and replayCtrl.isOffline:
                if slotType != SlotTypes.CLAN:
                    self.__doAttachStickers(slotType)
            if slotType == SlotTypes.CLAN:
                serverSettings = self.lobbyContext.getServerSettings()
                if serverSettings is not None and serverSettings.roaming.isInRoaming() or self.__isLoadingClanEmblems:
                    continue
                if not accountRep:
                    LOG_WARNING('Failed to attach clan sticker to the vehicle - account repository is not initialized')
                    continue
                self.__isLoadingClanEmblems = True
                fileCache = accountRep.customFilesCache
                fileServerSettings = accountRep.fileServerSettings
                clanEmblems = fileServerSettings.get('clan_emblems')
                if clanEmblems is None:
                    continue
                try:
                    url = clanEmblems['url_template'] % self.__clanID
                except Exception:
                    LOG_ERROR('Failed to attach stickers to the vehicle - server returned incorrect url format: %s' % clanEmblems['url_template'])
                    continue

                clanCallback = stricted_loading.makeCallbackWeak(self.__onClanEmblemLoaded)
                fileCache.get(url, clanCallback)

        return

    def detachStickers(self):
        if self.__model is None:
            return
        else:
            if self.__stickerModel.attached:
                self.__parentNode.detach(self.__stickerModel)
            self.__stickerModel.clear()
            self.__model = None
            self.__parentNode = None
            self.__isDamaged = False
            return

    def addDamageSticker(self, stickerID, segStart, segEnd):
        return 0 if self.__model is None else self.__stickerModel.addDamageSticker(stickerID, segStart, segEnd)

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

    def setAlpha(self, stickersAlpha):
        self.__stickerModel.setAlpha(stickersAlpha)

    def __doAttachStickers(self, slotType):
        if self.__model is None or slotType == SlotTypes.CLAN and self.__clanID == 0:
            return
        else:
            slots = self.__slotsByType[slotType]
            for idx, slot in enumerate(slots):
                if slot.hideIfDamaged and self.__isDamaged or self.__texParamsBySlotType[slotType][idx] is None:
                    continue
                texName, bumpTexName, isStickerMirrored = self.__texParamsBySlotType[slotType][idx]
                if texName == '' and slotType != SlotTypes.CLAN:
                    continue
                sizes = Math.Vector2(slot.size, slot.size)
                stickerAttributes = 0
                if slotType == SlotTypes.INSCRIPTION or slotType == SlotTypes.FIXED_INSCRIPTION:
                    sizes.y *= 0.5
                    stickerAttributes |= StickerAttributes.IS_INSCRIPTION
                elif slotType == SlotTypes.INSIGNIA_ON_GUN:
                    stickerAttributes |= StickerAttributes.DOUBLESIDED
                if slot.isMirrored and isStickerMirrored:
                    stickerAttributes |= StickerAttributes.IS_MIRRORED
                if slot.isUVProportional:
                    stickerAttributes |= StickerAttributes.IS_UV_PROPORTIONAL
                self.__stickerModel.addSticker(texName, bumpTexName, slot.rayStart, slot.rayEnd, sizes, slot.rayUp, stickerAttributes)

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

    def __init__(self, stickerID, rayStart, rayEnd, handle):
        self.rayStart = rayStart
        self.rayEnd = rayEnd
        self.stickerID = stickerID
        self.handle = handle


class VehicleStickers(object):

    def setClanID(self, clanID):
        for componentStickers in self.__stickers.itervalues():
            componentStickers.stickers.setClanID(clanID)

    def __setAlpha(self, alpha):
        multipliedAlpha = alpha * self.__defaultAlpha
        for componentStickers in self.__stickers.itervalues():
            actualAlpha = multipliedAlpha if self.__show else 0.0
            componentStickers.stickers.setAlpha(actualAlpha)
            componentStickers.alpha = multipliedAlpha

    alpha = property(lambda self: self.__stickers[TankPartNames.HULL].alpha, __setAlpha)

    def __setShow(self, show):
        self.__show = show
        for componentStickers in self.__stickers.itervalues():
            alpha = componentStickers.alpha if show else 0.0
            componentStickers.stickers.setAlpha(alpha)

    show = property(lambda self: self.__show, __setShow)
    COMPONENT_NAMES = ((TankPartNames.HULL, TankPartNames.HULL), (TankPartNames.TURRET, TankPartNames.TURRET), (TankPartNames.GUN, TankNodeNames.GUN_INCLINATION))
    __INSIGNIA_NODE_NAME = 'G'

    def __init__(self, vehicleDesc, insigniaRank=0, outfit=None):
        self.__showEmblemsOnGun = vehicleDesc.turret.showEmblemsOnGun
        self.__defaultAlpha = vehicleDesc.type.emblemsAlpha
        self.__show = True
        self.__animateGunInsignia = vehicleDesc.gun.animateEmblemSlots
        self.__currentInsigniaRank = insigniaRank
        if outfit is None:
            outfit = Outfit()
        componentSlots = ((TankPartNames.HULL, vehicleDesc.hull.emblemSlots),
         (TankPartNames.GUN if self.__showEmblemsOnGun else TankPartNames.TURRET, vehicleDesc.turret.emblemSlots),
         (TankPartNames.TURRET if self.__showEmblemsOnGun else TankPartNames.GUN, []),
         ('gunInsignia', vehicleDesc.gun.emblemSlots))
        self.__stickers = {}
        for componentName, emblemSlots in componentSlots:
            try:
                componentIdx = TankPartNames.getIdx(componentName)
            except Exception:
                componentIdx = -1

            container = outfit.getContainer(componentIdx)
            emblems = None
            inscriptions = None
            if container:
                emblems = container.slotFor(GUI_ITEM_TYPE.EMBLEM)
                inscriptions = container.slotFor(GUI_ITEM_TYPE.INSCRIPTION)
            decals = {SlotTypes.PLAYER: emblems,
             SlotTypes.INSCRIPTION: inscriptions}
            modelStickers = ModelStickers(vehicleDesc, emblemSlots, decals, componentName == TankPartNames.HULL, self.__currentInsigniaRank)
            self.__stickers[componentName] = ComponentStickers(modelStickers, {}, 1.0)

        return

    def getCurrentInsigniaRank(self):
        return self.__currentInsigniaRank

    def attach(self, compoundModel, isDamaged, showDamageStickers, isDetachedTurret=False):
        for componentName, attachNodeName in VehicleStickers.COMPONENT_NAMES:
            idx = DetachedTurretPartNames.getIdx(componentName) if isDetachedTurret else TankPartNames.getIdx(componentName)
            node = compoundModel.node(attachNodeName)
            if node is None:
                continue
            geometryLink = compoundModel.getPartGeometryLink(idx)
            componentStickers = self.__stickers[componentName]
            componentStickers.stickers.attachStickers(geometryLink, node, isDamaged)
            if showDamageStickers:
                for damageSticker in componentStickers.damageStickers.itervalues():
                    if damageSticker.handle is not None:
                        componentStickers.stickers.delDamageSticker(damageSticker.handle)
                        damageSticker.handle = None
                        LOG_WARNING('Adding %s damage sticker to occupied slot' % componentName)
                    damageSticker.handle = componentStickers.stickers.addDamageSticker(damageSticker.stickerID, damageSticker.rayStart, damageSticker.rayEnd)

        if isDamaged:
            gunNode = compoundModel.node(TankPartNames.GUN)
        elif self.__animateGunInsignia:
            gunNode = compoundModel.node(VehicleStickers.__INSIGNIA_NODE_NAME)
        else:
            gunNode = compoundModel.node(TankNodeNames.GUN_INCLINATION)
        if gunNode is None:
            return
        else:
            gunGeometry = compoundModel.getPartGeometryLink(DetachedTurretPartIndexes.GUN) if isDetachedTurret else compoundModel.getPartGeometryLink(TankPartIndexes.GUN)
            if isDamaged:
                toPartRoot = mathUtils.createIdentityMatrix()
            else:
                toPartRoot = Math.Matrix(gunNode)
                toPartRoot.invert()
                toPartRoot.preMultiply(compoundModel.node(TankNodeNames.GUN_INCLINATION))
            self.__stickers['gunInsignia'].stickers.attachStickers(gunGeometry, gunNode, isDamaged, toPartRoot)
            return

    def detach(self):
        for componentStickers in self.__stickers.itervalues():
            componentStickers.stickers.detachStickers()
            for dmgSticker in componentStickers.damageStickers.itervalues():
                dmgSticker.handle = None

        return

    def addDamageSticker(self, code, componentIdx, stickerID, segStart, segEnd):
        componentStickers = self.__stickers[TankPartIndexes.getName(componentIdx)]
        if componentStickers.damageStickers.has_key(code):
            return
        segment = segEnd - segStart
        segLen = segment.lengthSquared
        if segLen != 0:
            segStart -= 0.25 * segment / math.sqrt(segLen)
        handle = componentStickers.stickers.addDamageSticker(stickerID, segStart, segEnd)
        componentStickers.damageStickers[code] = DamageSticker(stickerID, segStart, segEnd, handle)

    def delDamageSticker(self, code):
        for componentStickers in self.__stickers.itervalues():
            damageSticker = componentStickers.damageStickers.get(code)
            if damageSticker is not None:
                if damageSticker.handle is not None:
                    componentStickers.stickers.delDamageSticker(damageSticker.handle)
                del componentStickers.damageStickers[code]

        return
