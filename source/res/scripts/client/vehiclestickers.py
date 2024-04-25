# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleStickers.py
import imghdr
import logging
import weakref
from collections import namedtuple
import math
import BigWorld
import math_utils
import items
from debug_utils import LOG_ERROR, LOG_WARNING
from constants import IS_EDITOR
from helpers import dependency
import Math
from items.vehicles import getItemByCompactDescr
from items.components.c11n_constants import CustomizationType, DecalType
from skeletons.gui.lobby_context import ILobbyContext
from vehicle_systems import stricted_loading
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames, TankNodeNames
from vehicle_systems.tankStructure import DetachedTurretPartIndexes, DetachedTurretPartNames
from gui.shared.gui_items import GUI_ITEM_TYPE
from vehicle_outfit.outfit import Outfit
import wrapped_options
_logger = logging.getLogger(__name__)
if not IS_EDITOR:
    import BattleReplay

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


def isUseDebugStickers():
    return wrapped_options.getOptionBool('Vehicle/useDebugStickers', False)


DEBUG_STICKER_TEXTURE = 'gui/maps/vehicles/decals/player_stickers/cool/sticker_15.dds'
_TextureParams = namedtuple('TextureParams', ('textureName', 'bumpTextureName', 'mirror'))
_CounterParams = namedtuple('CounterParams', ('atlas', 'alphabet', 'mirror'))
_StickerSlotPair = namedtuple('_StickerSlotPair', ('componentSlot', 'stickerParams'))
_PersonalNumberTexParams = namedtuple('PersonalNumberTexParams', ('textureName', 'textureMap', 'text', 'fontMask', 'digitsCount'))
_INSIGNIA_LETTER = '*'

class StickerAttributes(object):
    IS_INSCRIPTION = 1
    DOUBLESIDED = 2
    IS_MIRRORED = 4
    IS_UV_PROPORTIONAL = 8
    APPLY_TO_FABRIC = 16
    IS_PLANE_PROJECTION = 32


class SlotTypes(object):
    CLAN = 'clan'
    PLAYER = 'player'
    INSCRIPTION = 'inscription'
    INSIGNIA_ON_GUN = 'insigniaOnGun'
    INSIGNIA = 'insignia'
    FIXED_EMBLEM = 'fixedEmblem'
    FIXED_INSCRIPTION = 'fixedInscription'
    ALL = (CLAN,
     PLAYER,
     INSCRIPTION,
     INSIGNIA_ON_GUN,
     INSIGNIA,
     FIXED_EMBLEM,
     FIXED_INSCRIPTION)


class Insignia(object):

    class NodeNames(object):
        SINGLE = 'G'
        DUAL_LEFT = 'G_L'
        DUAL_RIGHT = 'G_R'
        ALL = (SINGLE, DUAL_LEFT, DUAL_RIGHT)

    class Types(object):
        SINGLE = 'gunInsignia'
        DUAL_LEFT = 'gunInsigniaL'
        DUAL_RIGHT = 'gunInsigniaR'
        ALL = (SINGLE, DUAL_LEFT, DUAL_RIGHT)

    class Indexes(object):
        SINGLE = -1
        DUAL_LEFT = -2
        DUAL_RIGHT = -3
        ALL = (SINGLE, DUAL_LEFT, DUAL_RIGHT)


class ModelStickers(object):

    def __init__(self, spaceID, componentIdx, stickerPacks, vDesc, emblemSlots):
        self.__componentIdx = componentIdx
        self.__stickerPacks = stickerPacks
        for slot in emblemSlots:
            if slot.type in self.__stickerPacks:
                stickerPackTuple = self.__stickerPacks[slot.type]
                for stickerPack in stickerPackTuple:
                    stickerPack.bind(componentIdx, slot)

        self.__model = None
        self.__toPartRootMatrix = math_utils.createIdentityMatrix()
        self.__parentNode = None
        self.__isDamaged = False
        self.__stickerModel = BigWorld.WGStickerModel(spaceID)
        self.__stickerModel.setLODDistance(vDesc.type.emblemsLodDist)
        return

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
        stickerPacks = set()
        for stickerPackTuple in self.__stickerPacks.itervalues():
            for stickerPack in stickerPackTuple:
                stickerPacks.add(stickerPack)

        for stickerPack in stickerPacks:
            stickerPack.attach(self.__componentIdx, self.__stickerModel, isDamaged)

        return

    def detachStickers(self):
        if self.__model is None:
            return
        else:
            if self.__stickerModel.attached:
                self.__parentNode.detach(self.__stickerModel)
            for stickerPackTuple in self.__stickerPacks.itervalues():
                for stickerPack in stickerPackTuple:
                    stickerPack.detach(self.__componentIdx, self.__stickerModel)

            self.__stickerModel.clear()
            self.__model = None
            self.__parentNode = None
            return

    def addDamageSticker(self, stickerID, segStart, segEnd):
        return 0 if self.__model is None else self.__stickerModel.addDamageSticker(stickerID, segStart, segEnd)

    def delDamageSticker(self, handle):
        if self.__model is not None:
            self.__stickerModel.delSticker(handle)
        return

    def updateClanSticker(self):
        clanStickerPackTuple = self.__stickerPacks[SlotTypes.CLAN]
        if self.__model is not None:
            for clanStickerPack in clanStickerPackTuple:
                clanStickerPack.detach(self.__componentIdx, self.__stickerModel)
                clanStickerPack.attach(self.__componentIdx, self.__stickerModel, self.__isDamaged)

        return

    def updateInsigniaSticker(self):
        insigniaStickerPacks = set(self.__stickerPacks[SlotTypes.INSIGNIA] + self.__stickerPacks[SlotTypes.INSIGNIA_ON_GUN])
        if self.__model is not None:
            for insigniaStickerPack in insigniaStickerPacks:
                insigniaStickerPack.detach(self.__componentIdx, self.__stickerModel)
                insigniaStickerPack.update(self.__componentIdx)
                insigniaStickerPack.attach(self.__componentIdx, self.__stickerModel, self.__isDamaged)

        return

    def setAlpha(self, stickersAlpha):
        self.__stickerModel.setAlpha(stickersAlpha)


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


class StickerPack(object):
    _ALLOWED_PART_IDX = ()

    def __init__(self, vDesc, outfit):
        self._outfit = outfit
        self._data = {idx:[] for idx in self._ALLOWED_PART_IDX}
        self._handles = {idx:{} for idx in self._ALLOWED_PART_IDX}

    def getData(self, componentIdx):
        return self._data[componentIdx]

    def bind(self, componentIdx, componentSlot):
        raise NotImplementedError

    def attach(self, componentIdx, stickerModel, isDamaged):
        if not self._isValidComponentIdx(componentIdx):
            return
        params = self._data[componentIdx]
        for idx, param in enumerate(params):
            slot, sticker = param
            if not sticker or slot.hideIfDamaged and isDamaged:
                continue
            texName, bumpTexName, _ = sticker
            if texName == '' and not self._useTexture():
                continue
            sizes = self._getStickerSize(slot)
            stickerAttributes = self._getStickerAttributes(slot, sticker)
            handle = stickerModel.addSticker(texName, bumpTexName, slot.rayStart, slot.rayEnd, sizes, slot.rayUp, stickerAttributes)
            self._handles[componentIdx][idx] = handle

    def detach(self, componentIdx, stickerModel):
        if not self._isValidComponentIdx(componentIdx):
            return
        for handle in self._handles[componentIdx]:
            stickerModel.delSticker(handle)

        self._handles = {idx:{} for idx in self._ALLOWED_PART_IDX}

    def _isValidComponentIdx(self, componentIdx):
        return componentIdx in self._ALLOWED_PART_IDX

    def _useTexture(self):
        return False

    def _getStickerSize(self, slot):
        return (slot.size,) * 2

    def _getStickerAttributes(self, slot, sticker):
        stickerAttributes = 0
        if slot.isMirrored and sticker.mirror:
            stickerAttributes |= StickerAttributes.IS_MIRRORED
        if slot.isUVProportional:
            stickerAttributes |= StickerAttributes.IS_UV_PROPORTIONAL
        return stickerAttributes


class FixedEmblemStickerPack(StickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET, TankPartIndexes.GUN)

    def bind(self, componentIdx, componentSlot):
        if not self._isValidComponentIdx(componentIdx):
            return
        params = self._data[componentIdx]
        stickerParam = self._getDefaultParams(componentSlot.emblemId)
        params.append(_StickerSlotPair(componentSlot, stickerParam))

    def _getDefaultParams(self, stickerID):
        stickerID = stickerID
        item = items.vehicles.g_cache.customization20().decals.get(stickerID)
        return None if item is None else _TextureParams(item.texture, '', item.canBeMirrored)


class EmblemStickerPack(StickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET, TankPartIndexes.GUN)

    def bind(self, componentIdx, componentSlot):
        if not self._isValidComponentIdx(componentIdx):
            return
        else:
            container = self._outfit.getContainer(componentIdx)
            slot = container.slotFor(GUI_ITEM_TYPE.EMBLEM)
            params = self._data[componentIdx]
            slotIdx = len(params)
            intCD = slot.getItemCD(slotIdx)
            if intCD:
                item = getItemByCompactDescr(intCD)
                stickerParam = self.__convertToParams(item)
            else:
                stickerParam = None
            params.append(_StickerSlotPair(componentSlot, stickerParam))
            return

    def __convertToParams(self, item):
        return _TextureParams(item.texture, '', item.canBeMirrored)


class FixedInscriptionStickerPack(FixedEmblemStickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET, TankPartIndexes.GUN)

    def _getStickerSize(self, slot):
        return (slot.size, slot.size * 0.5)

    def _getStickerAttributes(self, slot, sticker):
        stickerAttributes = super(FixedInscriptionStickerPack, self)._getStickerAttributes(slot, sticker)
        return stickerAttributes | StickerAttributes.IS_INSCRIPTION


class InscriptionStickerPack(StickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET, TankPartIndexes.GUN)

    def bind(self, componentIdx, componentSlot):
        if not self._isValidComponentIdx(componentIdx):
            return
        else:
            container = self._outfit.getContainer(componentIdx)
            slot = container.slotFor(GUI_ITEM_TYPE.INSCRIPTION)
            params = self._data[componentIdx]
            slotIdx = len(params)
            intCD = slot.getItemCD(slotIdx)
            stickerParam = None
            if intCD:
                item = getItemByCompactDescr(intCD)
                if hasattr(item, 'type') and item.type == DecalType.INSCRIPTION:
                    stickerParam = self._convertToParams(item)
            params.append(_StickerSlotPair(componentSlot, stickerParam))
            return

    def _convertToParams(self, item):
        return _TextureParams(item.texture, '', item.canBeMirrored)

    def _getStickerSize(self, slot):
        return (slot.size, slot.size * 0.5)

    def _getStickerAttributes(self, slot, sticker):
        stickerAttributes = super(InscriptionStickerPack, self)._getStickerAttributes(slot, sticker)
        return stickerAttributes | StickerAttributes.IS_INSCRIPTION


class PersonalNumStickerPack(StickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET, TankPartIndexes.GUN)

    def bind(self, componentIdx, componentSlot):
        if not self._isValidComponentIdx(componentIdx):
            return
        else:
            container = self._outfit.getContainer(componentIdx)
            slot = container.slotFor(GUI_ITEM_TYPE.PERSONAL_NUMBER)
            params = self._data[componentIdx]
            slotIdx = len(params)
            component = slot.getComponent(slotIdx)
            intCD = slot.getItemCD(slotIdx)
            stickerParam = None
            if intCD:
                item = getItemByCompactDescr(intCD)
                if component and item.itemType == CustomizationType.PERSONAL_NUMBER:
                    stickerParam = self._convertToParams(item, component)
            params.append(_StickerSlotPair(componentSlot, stickerParam))
            return

    def _convertToParams(self, item, component):
        return _PersonalNumberTexParams(textureName=item.fontInfo.texture, textureMap=item.fontInfo.alphabet, text=component.number, fontMask=item.fontInfo.mask, digitsCount=item.digitsCount)

    def _getStickerSize(self, slot):
        return (slot.size, slot.size * 0.5)

    def attach(self, componentIdx, stickerModel, isDamaged):
        if not self._isValidComponentIdx(componentIdx):
            return
        params = self._data[componentIdx]
        for idx, param in enumerate(params):
            slot, sticker = param
            if not sticker or slot.hideIfDamaged and isDamaged:
                continue
            if sticker.textureName == '' and not self._useTexture():
                continue
            sizes = self._getStickerSize(slot)
            handle = stickerModel.addCounterSticker((sticker.textureName,
             sticker.textureMap,
             sticker.text,
             slot.rayStart,
             slot.rayEnd,
             sizes,
             slot.rayUp,
             sticker.fontMask,
             1,
             sticker.digitsCount,
             True))
            self._handles[componentIdx][idx] = handle


class ClanStickerPack(StickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET, TankPartIndexes.GUN)
    _NO_CLAN_ID = 0
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vDesc, clanId=_NO_CLAN_ID):
        super(ClanStickerPack, self).__init__(vDesc, None)
        self._clanId = clanId
        return

    def setClanId(self, clanId):
        clanId = clanId or self._NO_CLAN_ID
        if self._clanId == clanId:
            return False
        self._clanId = clanId
        return True

    def bind(self, componentIdx, componentSlot):
        self._data[componentIdx].append(_StickerSlotPair(componentSlot, _TextureParams('', '', False)))

    def attach(self, componentIdx, stickerModel, isDamaged):
        if IS_EDITOR:
            self.__onClanEmblemLoaded(None, None, componentIdx, stickerModel, isDamaged)
            return
        elif not self._isValidComponentIdx(componentIdx):
            return
        elif not self._data[componentIdx]:
            return
        else:
            if not IS_EDITOR:
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying and replayCtrl.isOffline:
                    return
            serverSettings = self.lobbyContext.getServerSettings()
            if serverSettings is not None and serverSettings.roaming.isInRoaming():
                return
            accountRep = _getAccountRepository()
            if not accountRep:
                LOG_WARNING('Failed to attach clan sticker to the vehicle - account repository is not initialized')
                return
            fileCache = accountRep.customFilesCache
            fileServerSettings = accountRep.fileServerSettings
            clanEmblems = fileServerSettings.get('clan_emblems')
            if clanEmblems is None:
                return
            try:
                url = clanEmblems['url_template'] % self._clanId
            except Exception:
                LOG_ERROR('Failed to attach stickers to the vehicle - server returned incorrect url format: %s' % clanEmblems['url_template'])
                return

            clanCallback = stricted_loading.makeCallbackWeak(self.__onClanEmblemLoaded, componentIdx=componentIdx, stickerModel=weakref.proxy(stickerModel), isDamaged=isDamaged)
            fileCache.get(url, clanCallback)
            return

    def _isValidComponentIdx(self, componentIdx):
        return super(ClanStickerPack, self)._isValidComponentIdx(componentIdx) if IS_EDITOR else self._clanId != ClanStickerPack._NO_CLAN_ID and super(ClanStickerPack, self)._isValidComponentIdx(componentIdx)

    def _useTexture(self):
        return False if IS_EDITOR else True

    def __onClanEmblemLoaded(self, _, data, componentIdx, stickerModel, isDamaged):
        if not IS_EDITOR:
            if data is None:
                return
            if imghdr.what(None, data) is None:
                return
            stickerModel.setTextureData(data)
        super(ClanStickerPack, self).attach(componentIdx, stickerModel, isDamaged)
        return


class InsigniaStickerPack(StickerPack):
    _ALLOWED_PART_IDX = (TankPartIndexes.HULL, TankPartIndexes.TURRET) + Insignia.Indexes.ALL
    _NO_INSIGNIA_RANK = 0

    def __init__(self, vDesc, outfit, insigniaRank):
        super(InsigniaStickerPack, self).__init__(vDesc, outfit)
        self._insigniaRank = insigniaRank
        self._customizationNationID = vDesc.type.customizationNationID
        self._useCustomInsignia = False
        self._useOldInsignia = True

    def setInsigniaRank(self, insigniaRank):
        if self._insigniaRank == insigniaRank:
            return False
        self._insigniaRank = insigniaRank
        return True

    def bind(self, componentIdx, componentSlot):
        params = self._data[componentIdx]
        slotIdx = len(params)
        if componentIdx in Insignia.Indexes.ALL:
            if IS_EDITOR:
                defaultParams = _TextureParams('', '', False)
                item = items.vehicles.g_cache.customization20().insignias.get(componentSlot.edResourceId)
                stickerParam = defaultParams if item is None else self._convertToInsignia(item)
            else:
                container = self._outfit.getContainer(TankPartIndexes.GUN)
                slot = container.slotFor(GUI_ITEM_TYPE.INSIGNIA)
                intCD = slot.getItemCD(slotIdx)
                if intCD:
                    item = getItemByCompactDescr(intCD)
                    stickerParam = self._convertToInsignia(item)
                    self._useCustomInsignia = True
                else:
                    stickerParam = self._getDefaultParams()
        else:
            container = self._outfit.getContainer(componentIdx)
            slot = container.slotFor(GUI_ITEM_TYPE.INSIGNIA)
            intCD = slot.getItemCD(slotIdx)
            if intCD:
                item = getItemByCompactDescr(intCD)
                stickerParam = self._convertToCounter(item)
                self._useOldInsignia = False
            else:
                stickerParam = None
        params.append(_StickerSlotPair(componentSlot, stickerParam))
        return

    def attach(self, componentIdx, stickerModel, isDamaged):
        if not self._isValidComponentIdx(componentIdx):
            return
        if componentIdx in Insignia.Indexes.ALL:
            if self._useOldInsignia or self._useCustomInsignia:
                super(InsigniaStickerPack, self).attach(componentIdx, stickerModel, isDamaged)
            return
        params = self._data[componentIdx]
        for idx, param in enumerate(params):
            slot, sticker = param
            if not sticker or slot.hideIfDamaged and isDamaged:
                continue
            size = self._getStickerSize(slot)
            value = _INSIGNIA_LETTER * self._insigniaRank
            handle = stickerModel.addCounterSticker((sticker.atlas,
             sticker.alphabet,
             value,
             slot.rayStart,
             slot.rayEnd,
             size,
             slot.rayUp,
             '',
             1,
             3,
             True))
            self._handles[componentIdx][idx] = handle

    def update(self, componentIdx):
        if not self._isValidComponentIdx(componentIdx):
            return
        params = self._data.pop(componentIdx, [])
        self._data[componentIdx] = []
        for param in params:
            slot, _ = param
            self.bind(componentIdx, slot)

    def _isValidComponentIdx(self, componentIdx):
        return False if self._insigniaRank == self._NO_INSIGNIA_RANK else super(InsigniaStickerPack, self)._isValidComponentIdx(componentIdx)

    def _getDefaultParams(self):
        defaultParams = _TextureParams('', '', False)
        defaultInsignia = items.vehicles.g_cache.customization20().defaultInsignias.get(self._customizationNationID)
        if defaultInsignia is None:
            return defaultParams
        else:
            item = items.vehicles.g_cache.customization20().insignias.get(defaultInsignia)
            return defaultParams if item is None else self._convertToInsignia(item)

    def _getStickerAttributes(self, slot, sticker):
        stickerAttributes = StickerAttributes.DOUBLESIDED
        if slot.applyToFabric:
            stickerAttributes |= StickerAttributes.APPLY_TO_FABRIC
        if slot.planeProjection:
            stickerAttributes |= StickerAttributes.IS_PLANE_PROJECTION
        return stickerAttributes | super(InsigniaStickerPack, self)._getStickerAttributes(slot, sticker)

    def _convertToInsignia(self, item):
        constantPart, delimeterPart, changeablePart = item.texture.rpartition('_')
        _, dotPart, extenstionPart = changeablePart.partition('.')
        textureName = constantPart + delimeterPart + str(self._insigniaRank) + dotPart + extenstionPart
        return _TextureParams(textureName, '', item.canBeMirrored)

    def _convertToCounter(self, item):
        return _CounterParams(item.atlas, item.alphabet, item.canBeMirrored)


class DebugStickerPack(StickerPack):
    _ALLOWED_PART_IDX = TankPartIndexes.ALL + Insignia.Indexes.ALL

    def bind(self, componentIdx, componentSlot):
        if not self._isValidComponentIdx(componentIdx):
            return
        params = self._data[componentIdx]
        stickerParam = _TextureParams(DEBUG_STICKER_TEXTURE, '', True)
        params.append(_StickerSlotPair(componentSlot, stickerParam))

    def setClanId(self, clanId):
        pass

    def setInsigniaRank(self, insigniaRank):
        pass

    def _getStickerSize(self, slot):
        return (slot.size, slot.size * 0.5) if slot.type in (SlotTypes.INSCRIPTION, SlotTypes.FIXED_INSCRIPTION) else super(DebugStickerPack, self)._getStickerSize(slot)

    def _getStickerAttributes(self, slot, sticker):
        stickerAttributes = super(DebugStickerPack, self)._getStickerAttributes(slot, sticker)
        if slot.type in (SlotTypes.INSIGNIA, SlotTypes.INSIGNIA_ON_GUN):
            stickerAttributes |= StickerAttributes.DOUBLESIDED
            if slot.applyToFabric:
                stickerAttributes |= StickerAttributes.APPLY_TO_FABRIC
        return stickerAttributes


class VehicleStickers(object):

    def setClanID(self, clanID):
        clanStickerPackTuple = self.__stickerPacks[SlotTypes.CLAN]
        for clanStickerPack in clanStickerPackTuple:
            if clanStickerPack.setClanId(clanID):
                for componentStickers in self.__stickers.itervalues():
                    componentStickers.stickers.updateClanSticker()

    def setInsigniaRank(self, insigniaRank):
        self.__currentInsigniaRank = insigniaRank
        insigniaStickerPacks = set(self.__stickerPacks[SlotTypes.INSIGNIA] + self.__stickerPacks[SlotTypes.INSIGNIA_ON_GUN])
        for insigniaStickerPack in insigniaStickerPacks:
            if insigniaStickerPack.setInsigniaRank(insigniaRank):
                for componentStickers in self.__stickers.itervalues():
                    componentStickers.stickers.updateInsigniaSticker()

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

    def __init__(self, spaceID, vehicleDesc, insigniaRank=0, outfit=None):
        self.__defaultAlpha = vehicleDesc.type.emblemsAlpha
        self.__show = True
        self.__animateGunInsignia = vehicleDesc.gun.animateEmblemSlots
        self.__currentInsigniaRank = insigniaRank
        self.__vDesc = vehicleDesc
        self.__componentNames = [(TankPartNames.HULL, TankPartNames.HULL), (TankPartNames.TURRET, TankPartNames.TURRET), (TankPartNames.GUN, TankNodeNames.GUN_INCLINATION)]
        if outfit is None:
            outfit = Outfit(vehicleCD=vehicleDesc.makeCompactDescr())
        componentSlots = self._createComponentSlots(vehicleDesc, vehicleDesc.turret.showEmblemsOnGun, outfit)
        if not isUseDebugStickers():
            self.__stickerPacks = self._createStickerPacks(vehicleDesc, outfit, insigniaRank)
        else:
            self.__stickerPacks = self._createDebugStickerPacks(vehicleDesc, outfit, insigniaRank)
        self.__stickers = {}
        for componentName, emblemSlots in componentSlots:
            if componentName == Insignia.Types.SINGLE:
                componentIdx = Insignia.Indexes.SINGLE
            elif componentName == Insignia.Types.DUAL_LEFT:
                componentIdx = Insignia.Indexes.DUAL_LEFT
            elif componentName == Insignia.Types.DUAL_RIGHT:
                componentIdx = Insignia.Indexes.DUAL_RIGHT
            else:
                componentIdx = TankPartNames.getIdx(componentName)
            modelStickers = ModelStickers(spaceID, componentIdx, self.__stickerPacks, vehicleDesc, emblemSlots)
            self.__stickers[componentName] = ComponentStickers(modelStickers, {}, 1.0)

        return

    def getCurrentInsigniaRank(self):
        return self.__currentInsigniaRank

    def getStickerPack(self, packType):
        return self.__stickerPacks[packType]

    def attach(self, compoundModel, isDamaged, showDamageStickers, isDetachedTurret=False):
        for componentName, attachNodeName in self.__componentNames:
            idx = DetachedTurretPartNames.getIdx(componentName) if isDetachedTurret else TankPartNames.getIdx(componentName)
            node = compoundModel.node(attachNodeName)
            if node is None:
                continue
            if idx is None:
                node = compoundModel.node(componentName + ('_normal' if not isDamaged else '_destroyed'))
                idx = compoundModel.findPartHandleByNode(node)
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

        if isDetachedTurret:
            gunGeometry = compoundModel.getPartGeometryLink(DetachedTurretPartIndexes.GUN)
        else:
            gunGeometry = compoundModel.getPartGeometryLink(TankPartIndexes.GUN)
        for key in set(Insignia.Types.ALL) & set(self.__stickers.keys()):
            gunNode, toPartRoot = self.__getInsigniaAttachNode(key, isDamaged, compoundModel)
            if gunNode is None:
                return
            self.__stickers[key].stickers.attachStickers(gunGeometry, gunNode, isDamaged, toPartRoot)

        return

    def detach(self):
        for componentStickers in self.__stickers.itervalues():
            componentStickers.stickers.detachStickers()
            for dmgSticker in componentStickers.damageStickers.itervalues():
                dmgSticker.handle = None

        return

    def addDamageSticker(self, code, componentIdx, stickerID, segStart, segEnd, collisionComponent):
        componentName = TankPartIndexes.getName(componentIdx)
        if not componentName:
            return
        componentStickers = self.__stickers[componentName]
        if code in componentStickers.damageStickers:
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

    @classmethod
    def _createComponentSlots(cls, vehicleDesc, showEmblemsOnGun, outfit):
        showEmblemsOnGun = vehicleDesc.turret.showEmblemsOnGun
        componentSlots = ((TankPartNames.HULL, vehicleDesc.hull.emblemSlots), (TankPartNames.GUN if showEmblemsOnGun else TankPartNames.TURRET, vehicleDesc.turret.emblemSlots), (TankPartNames.TURRET if showEmblemsOnGun else TankPartNames.GUN, [ slot for slot in vehicleDesc.gun.emblemSlots if slot.type != 'insigniaOnGun' ]))
        gunSlots = cls._createGunSlots(vehicleDesc, outfit)
        if gunSlots:
            componentSlots += gunSlots
        return componentSlots

    @classmethod
    def _createGunSlots(cls, vehicleDesc, outfit):
        gunEmblemSlots = vehicleDesc.gun.emblemSlots
        outfitModelSet = outfit.modelsSet
        compatibleGunSlots = []
        if outfitModelSet:
            for gSlot in gunEmblemSlots:
                if outfitModelSet in gSlot.compatibleModels:
                    compatibleGunSlots.append(gSlot)

        if not compatibleGunSlots:
            for gSlot in gunEmblemSlots:
                if not gSlot.compatibleModels:
                    compatibleGunSlots.append(gSlot)

        if vehicleDesc.isDualgunVehicle and compatibleGunSlots:
            slotsCount = len(compatibleGunSlots)
            if slotsCount >= 2:
                midIndex = slotsCount / 2
                i = slotsCount - 1
                secondHalf = []
                while i >= midIndex:
                    secondHalf.append(compatibleGunSlots.pop())
                    i = i - 1

                return ((Insignia.Types.DUAL_LEFT, compatibleGunSlots), (Insignia.Types.DUAL_RIGHT, secondHalf))
            _logger.warning('Dual gun vehicle has less then two slots for marks on gun!')
            return None
        else:
            return ((Insignia.Types.SINGLE, compatibleGunSlots),)

    def _createStickerPacks(self, vehicleDesc, outfit, insigniaRank):
        insignias = InsigniaStickerPack(vehicleDesc, outfit, insigniaRank)
        return {SlotTypes.PLAYER: (EmblemStickerPack(vehicleDesc, outfit),),
         SlotTypes.FIXED_EMBLEM: (FixedEmblemStickerPack(vehicleDesc, outfit),),
         SlotTypes.INSCRIPTION: (InscriptionStickerPack(vehicleDesc, outfit), PersonalNumStickerPack(vehicleDesc, outfit)),
         SlotTypes.FIXED_INSCRIPTION: (FixedInscriptionStickerPack(vehicleDesc, outfit),),
         SlotTypes.INSIGNIA: (insignias,),
         SlotTypes.INSIGNIA_ON_GUN: (insignias,),
         SlotTypes.CLAN: (ClanStickerPack(vehicleDesc),)}

    def _createDebugStickerPacks(self, vehicleDesc, outfit, insigniaRank):
        debugStickerPack = DebugStickerPack(vehicleDesc, outfit)
        return {SlotTypes.PLAYER: (debugStickerPack,),
         SlotTypes.FIXED_EMBLEM: (debugStickerPack,),
         SlotTypes.INSCRIPTION: (debugStickerPack,),
         SlotTypes.FIXED_INSCRIPTION: (debugStickerPack,),
         SlotTypes.INSIGNIA: (debugStickerPack,),
         SlotTypes.INSIGNIA_ON_GUN: (debugStickerPack,),
         SlotTypes.CLAN: (debugStickerPack,)}

    def __getInsigniaAttachNode(self, insigniaType, isDamaged, compoundModel):
        if isDamaged:
            toPartRoot = math_utils.createIdentityMatrix()
            gunNode = compoundModel.node(TankPartNames.GUN)
        else:
            if self.__animateGunInsignia:
                idx = Insignia.Types.ALL.index(insigniaType)
                gunNode = compoundModel.node(Insignia.NodeNames.ALL[idx])
            else:
                gunNode = compoundModel.node(TankNodeNames.GUN_INCLINATION)
            if gunNode is None:
                return (None, None)
            toPartRoot = Math.Matrix(gunNode)
            toPartRoot.invert()
            toPartRoot.preMultiply(compoundModel.node(TankNodeNames.GUN_INCLINATION))
        return (gunNode, toPartRoot)
