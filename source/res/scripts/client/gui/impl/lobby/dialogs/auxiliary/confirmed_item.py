# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/auxiliary/confirmed_item.py
import typing
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.lobby.dialogs.auxiliary.confirmed_item_helpers import getHighlightsTypeByItem, getOverlayTypeByItem, ConfirmedItemWarningTypes, DependsOnDevicesWarning
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl.gen.view_models.views.lobby.common.confirmed_item_model import ConfirmedItemModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.gui_items.gui_item_economics import ItemPrice
SUPPORTED_TYPES = GUI_ITEM_TYPE.ARTEFACTS + GUI_ITEM_TYPE.VEHICLE_MODULES

class ConfirmedItem(object):
    __slots__ = ('_item', '_ctx', '_warnings')

    def __init__(self, item, ctx=None):
        self._item = item
        self._ctx = ctx if ctx is not None else {}
        self._warnings = self._setWarnings()
        return

    def getName(self):
        return self._item.userName

    def getTypeID(self):
        return self._item.itemTypeID

    def getImageSource(self):
        return R.invalid()

    def getHighlightsType(self):
        pass

    def getOverlayType(self):
        pass

    def getWarnings(self):
        return self._warnings

    def getRemovalPrice(self):
        return ITEM_PRICE_EMPTY

    def canUseDemountKit(self):
        return False

    def getLevel(self):
        pass

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        if item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            return ConfirmedModule.createFromGUIItem(item, ctx)
        if item.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            return ConfirmedArtefact.createFromGUIItem(item, ctx)
        if item.itemTypeID == GUI_ITEM_TYPE.SHELL:
            return ConfirmedShell(item, ctx)
        return ConfirmedBattleAbility(item, ctx) if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_ABILITY else ConfirmedItem(item)

    def getCofirmedItemViewModel(self):
        itemModel = ConfirmedItemModel()
        itemModel.setName(self.getName())
        itemModel.setImageSource(self.getImageSource())
        itemModel.setHighlightType(self.getHighlightsType())
        itemModel.setOverlayType(self.getOverlayType())
        itemModel.setCanUseDemountKit(self.canUseDemountKit())
        itemModel.setLevel(self.getLevel())
        price = self.getRemovalPrice()
        if price:
            BuyPriceModelBuilder.fillPriceModelByItemPrice(itemModel.demountPrice, price)
        return itemModel

    def _setWarnings(self):
        return {}


class ConfirmedArtefact(ConfirmedItem):

    def getImageSource(self):
        imageSource = R.images.gui.maps.shop.artefacts.c_180x135.dyn(self._item.getGUIEmblemID())
        return imageSource() if imageSource else R.invalid()

    def getHighlightsType(self):
        return getHighlightsTypeByItem(self._item)

    def getOverlayType(self):
        return getOverlayTypeByItem(self._item)

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            return ConfirmedBattleBooster(item, ctx)
        return ConfirmedOptDevice(item, ctx) if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else ConfirmedArtefact(item, ctx)


class ConfirmedOptDevice(ConfirmedArtefact):
    __itemsCache = dependency.descriptor(IItemsCache)

    def getRemovalPrice(self):
        return self._item.getRemovalPrice(self.__itemsCache.items)

    def canUseDemountKit(self):
        return not self._item.isRemovable and not self._item.isDeluxe

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        return ConfirmedOptDevice(item, ctx)


class ConfirmedBattleBooster(ConfirmedArtefact):
    __itemsCache = dependency.descriptor(IItemsCache)

    def getOverlayType(self):
        vehInvID = self._ctx.get('vehicleInvID', None)
        return getOverlayTypeByItem(self._item, self.__getBoosterReplaceCriteria(vehInvID)) if vehInvID is not None else getOverlayTypeByItem(self._item)

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        return ConfirmedBattleBooster(item, ctx)

    def _setWarnings(self):
        warnings = {}
        vehInvID = self._ctx.get('vehicleInvID', None)
        if vehInvID is not None:
            vehicleToInstall = self.__itemsCache.items.getVehicle(vehInvID)
            devicesCritetia = REQ_CRITERIA.VEHICLE.SUITABLE([vehicleToInstall], [GUI_ITEM_TYPE.OPTIONALDEVICE]) | ~REQ_CRITERIA.HIDDEN ^ ~REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | ~REQ_CRITERIA.SECRET
            devices = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, devicesCritetia).values()
            compatibleDeviceCDs = set()
            compatibleDeviceTierLessNames = set()
            for d in devices:
                if self._item.isOptionalDeviceCompatible(d):
                    compatibleDeviceCDs.add(d.intCD)
                    if not d.isUpgraded:
                        compatibleDeviceTierLessNames.add(d.descriptor.tierlessName)

            if compatibleDeviceCDs and compatibleDeviceCDs.isdisjoint([ d.intCD for d in vehicleToInstall.optDevices.layout.getItems() ]):
                warnings[ConfirmedItemWarningTypes.DEPENDS_ON_DEVICES] = DependsOnDevicesWarning(compatibleDeviceTierLessNames)
        return warnings

    def __getBoosterReplaceCriteria(self, vehInvID):
        vehicleToInstall = self.__itemsCache.items.getVehicle(vehInvID)
        skillLearn = REQ_CRITERIA.CUSTOM(lambda item: not item.isAffectedSkillLearnt(vehicleToInstall))
        return {ItemHighlightTypes.BATTLE_BOOSTER_REPLACE: REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT | skillLearn,
         ItemHighlightTypes.BATTLE_BOOSTER: (REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT | ~skillLearn) ^ REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT}


class ConfirmedBattleAbility(ConfirmedItem):

    def getHighlightsType(self):
        return ItemHighlightTypes.BATTLE_ABILITY

    def getImageSource(self):
        imageSource = R.images.gui.maps.icons.epicBattles.skills.c_180x135.dyn(self._item.getGUIEmblemID())
        return imageSource() if imageSource else R.invalid()

    def getLevel(self):
        return self._item.level if self._item.isUnlocked else 0

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        return ConfirmedBattleAbility(item, ctx)


class ConfirmedModule(ConfirmedItem):

    def getImageSource(self):
        imageSource = R.images.gui.maps.shop.modules.c_180x135.dyn(self._item.getGUIEmblemID())
        return imageSource() if imageSource else R.invalid()

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        return ConfirmedDualGun(item, ctx) if item.itemTypeID == GUI_ITEM_TYPE.GUN and item.isDualGun() else ConfirmedModule(item, ctx)


class ConfirmedDualGun(ConfirmedModule):

    def getImageSource(self):
        imageSource = R.images.gui.maps.shop.modules.c_180x135.dyn(FITTING_TYPES.VEHICLE_GUN)
        return imageSource() if imageSource else R.invalid()

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        return ConfirmedDualGun(item, ctx)


class ConfirmedShell(ConfirmedItem):

    def getImageSource(self):
        imageSource = R.images.gui.maps.shop.shells.c_180x135.dyn(self._item.getGUIEmblemID())
        return imageSource() if imageSource else R.invalid()

    @classmethod
    def createFromGUIItem(cls, item, ctx=None):
        return ConfirmedShell(item, ctx)
