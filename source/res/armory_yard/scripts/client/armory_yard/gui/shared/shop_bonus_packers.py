# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/shop_bonus_packers.py
import logging
import re
from typing import TYPE_CHECKING
import nations
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_shop_item import ArmoryYardShopItem, TemplateType
from constants import PREMIUM_ENTITLEMENTS, ROLE_TYPE, ROLE_TYPE_TO_LABEL
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import OptDeviceBonusesDescriptionBuilder, getCategoriesIcons, getStorageItemName, getStorageItemIcon, getItemNationID, getTypeUserName
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from gui.shared.gui_items.customization.c11n_items import Style
from gui.shared.money import Currency
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from helpers import int2roman, dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

def _removeStringColorTags(string):
    return re.sub('{colorTagOpen}|{colorTagClose}', '', string)


def _getNationFlagIcon(item):
    itemNationID = getItemNationID(item)
    return nations.NAMES[itemNationID] if itemNationID != nations.NONE_INDEX else ''


class ArmoryOptDeviceBonusesDescriptionBuilder(OptDeviceBonusesDescriptionBuilder):
    KPI_VALUE_TEMPLATE = '%(80d43a_Open)s{}%(80d43a_Close)s'

    def _effectStringFormat(self, effect):
        return effect

    def _kpiStringFormat(self, description):
        return description


class ShopBaseUIPacker(object):

    def __init__(self, count):
        self.count = count

    @property
    def isSupported(self):
        return False

    @property
    def icon(self):
        raise NotImplementedError

    @property
    def largeIcon(self):
        raise NotImplementedError

    @property
    def title(self):
        raise NotImplementedError

    @property
    def description(self):
        pass

    @property
    def longDescription(self):
        pass

    @property
    def template(self):
        return TemplateType.OTHER

    @property
    def nationFlagIcon(self):
        pass

    @property
    def effect(self):
        pass

    @property
    def itemType(self):
        pass

    def pack(self, model, isLargeIcon=False):
        if not self.isSupported:
            return False
        model.setTemplate(self.template)
        model.setCount(self.count)
        model.setTitle(self.title)
        model.setImage(self.icon)
        model.setLargeImage(self.largeIcon)
        model.setEffect(self.effect)
        model.setLongDescription(self.longDescription)
        model.setDescription(self.description)
        model.setNationFlagIcon(self.nationFlagIcon)
        model.setAvailable(True)
        return True


class CurrencyPacker(ShopBaseUIPacker):
    _CURRENCY = None
    __FORMATTER = '%(C9C9B6_Open)s{}%(C9C9B6_Close)s'

    def __init__(self, count=0):
        super(CurrencyPacker, self).__init__(count)
        self._strSection = R.strings.armory_shop.dyn(self._CURRENCY)

    @property
    def isSupported(self):
        return True

    @property
    def icon(self):
        return backport.image(R.images.gui.maps.icons.quests.bonuses.s180x135.dyn(self._CURRENCY)())

    @property
    def largeIcon(self):
        return backport.image(R.images.gui.maps.icons.quests.bonuses.s400x300.dyn(self._CURRENCY)())

    @property
    def title(self):
        return backport.text(self._strSection.title()) if self._strSection is not None else None

    @property
    def description(self):
        return backport.text(self._strSection.description(), value=self.__FORMATTER.format(self.count)) if self._strSection is not None else None

    @property
    def longDescription(self):
        return backport.text(self._strSection.longDescription(), value=self.count) if self._strSection is not None else None


class CreditsPacker(CurrencyPacker):
    _CURRENCY = Currency.CREDITS


class GoldPacker(CurrencyPacker):
    _CURRENCY = Currency.GOLD


class FreeXpPacker(CurrencyPacker):
    _CURRENCY = Currency.FREE_XP


class EquipCoinPacker(CurrencyPacker):
    _CURRENCY = Currency.EQUIP_COIN


class CrystalPacker(CurrencyPacker):
    _CURRENCY = Currency.CRYSTAL


class PremiumPlusPacker(ShopBaseUIPacker):
    __IMG_NAME = 'premium_plus_{}'
    __FORMATTER = '%(C9C9B6_Open)s{}%(C9C9B6_Close)s'
    __SIZE_SMALL = 's232x174'
    __SIZE_LARGE = 's400x300'

    def __init__(self, day):
        super(PremiumPlusPacker, self).__init__(day)
        self.__day = day

    def __getIcon(self, size):
        resource = R.images.gui.maps.icons.quests.bonuses.dyn(size).dyn(self.__IMG_NAME.format(self.__day))
        return resource() if resource.isValid() else R.images.gui.maps.icons.quests.bonuses.dyn(size).premium_plus_universal()

    @property
    def isSupported(self):
        return True

    @property
    def icon(self):
        return backport.image(self.__getIcon(self.__SIZE_SMALL))

    @property
    def largeIcon(self):
        return backport.image(self.__getIcon(self.__SIZE_LARGE))

    @property
    def title(self):
        return backport.text(R.strings.armory_shop.premiumPlus.title())

    @property
    def description(self):
        return backport.text(self.__getDescription()(), value=self.__FORMATTER.format(self.__day))

    @property
    def longDescription(self):
        return backport.text(R.strings.armory_shop.premiumPlus.longDescription(), dayStr=backport.text(self.__getDescription()(), value=self.__day))

    def __getDescription(self):
        if self.__day == 1:
            descr = R.strings.armory_shop.premiumPlus.description_1
        elif self.__day in (2, 3):
            descr = R.strings.armory_shop.premiumPlus.description_2
        else:
            descr = R.strings.armory_shop.premiumPlus.description_3
        return descr


class CustomizationPacker(ShopBaseUIPacker):
    __service = dependency.descriptor(ICustomizationService)
    __customizationTitle = R.strings.armory_shop.product.customizationTitle
    __customizationImgPath = R.images.armory_yard.gui.maps.icons.shop.customizations.styles

    def __init__(self, params):
        styleParams = params[1][0]
        styleCount = styleParams['value']
        styleType = styleParams['custType']
        super(CustomizationPacker, self).__init__(styleCount)
        self.__itemTypeID = GUI_ITEM_TYPE_INDICES.get(styleType) if styleType != 'projection_decal' else GUI_ITEM_TYPE.PROJECTION_DECAL
        self.__item = self.__service.getItemByID(self.__itemTypeID, styleParams['id'])
        if not self.__item:
            _logger.warning('ArmoryYardShop style %s not found', styleParams['id'])
        self.__is3DStyle = isinstance(self.__item, Style) and self.__item.is3D

    @property
    def isSupported(self):
        return bool(self.__item)

    @property
    def icon(self):
        return self.__item.iconUrl if self.__itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL else backport.image(self.__customizationImgPath.num(STORE_CONSTANTS.ICON_SIZE_SMALL).num(self.__item.id)())

    @property
    def largeIcon(self):
        return self.__item.iconUrl if self.__itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL else backport.image(self.__customizationImgPath.num(STORE_CONSTANTS.ICON_SIZE_296).num(self.__item.id)())

    @property
    def title(self):
        if self.__itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            title = self.__customizationTitle.decals()
        elif self.__is3DStyle:
            title = self.__customizationTitle.style3D()
        else:
            title = self.__customizationTitle.style2D()
        return backport.text(title, styleName=self.__item.userName)

    @property
    def description(self):
        return self.__item.fullDescription

    @property
    def longDescription(self):
        return self.__item.fullDescription

    @property
    def template(self):
        return TemplateType.CUSTOMIZATION

    @property
    def itemType(self):
        return self.__item.itemTypeName

    def pack(self, model, isLargeIcon=False):
        if not super(CustomizationPacker, self).pack(model, isLargeIcon):
            return False
        model.setItemType(self.itemType)
        if self.__is3DStyle:
            model.setAvailable(not self.__item.inventoryCount)
        return True


class GoodiesPacker(ShopBaseUIPacker):
    __cache = dependency.descriptor(IGoodiesCache)
    __FORMATTER = '%(CBAC77_Open)s{}%(CBAC77_Close)s'
    __BOOSTER_TYPE_TITLE = {GOODIE_RESOURCE_TYPE.CREDITS: R.strings.personal_reserves.activation.creditsTitle(),
     GOODIE_RESOURCE_TYPE.XP: R.strings.personal_reserves.activation.battleXPTitle(),
     GOODIE_RESOURCE_TYPE.CREW_XP: R.strings.personal_reserves.activation.battleXPTitle(),
     GOODIE_RESOURCE_TYPE.FREE_XP: R.strings.personal_reserves.activation.battleXPTitle(),
     GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP: R.strings.personal_reserves.activation.comboXPTitle(),
     GOODIE_RESOURCE_TYPE.FREE_XP_MAIN_XP: R.strings.personal_reserves.activation.comboXPTitle()}

    def __init__(self, params):
        goodiesId, goodieParams = params.items()[0]
        self.__item = self.__cache.getBooster(goodiesId)
        super(GoodiesPacker, self).__init__(goodieParams.get('count', 1))
        if not self.__item:
            _logger.warning('ArmoryYardShop goodies %s not found', goodiesId)

    @property
    def isSupported(self):
        return bool(self.__item)

    @property
    def icon(self):
        return self.__item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL)

    @property
    def largeIcon(self):
        return self.__item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_MEDIUM)

    @property
    def title(self):
        title = self.__BOOSTER_TYPE_TITLE.get(self.__item.boosterType, None)
        return backport.text(title) if title is not None else self.__item.userName

    @property
    def longDescription(self):
        return self.__item.longDescriptionSpecial

    @property
    def effect(self):
        return self.__item.getDescription(valueFormatter=self.__format)

    @property
    def template(self):
        return TemplateType.MAINTAIN

    def __format(self, value):
        return self.__FORMATTER.format(value)


class ItemPacker(ShopBaseUIPacker):
    __cache = dependency.descriptor(IItemsCache)
    __BATTLE_BOOSTER_FORMATTER = '%(80D43A_Open)s{}%(80D43A_Close)s'
    __DEFAULT_TEMPLATE = {'expTagOpen': '%(C9C9B6_Open)s',
     'expTagClose': '%(C9C9B6_Close)s',
     'effectTagOpen': '%(CBAC77_Open)s',
     'effectTagClose': '%(CBAC77_Close)s',
     'colourTagOpen': '%(80D43A_Open)s',
     'colourTagClose': '%(80D43A_Close)s'}

    def __init__(self, params):
        itemId, count = params.items()[0]
        super(ItemPacker, self).__init__(count)
        self.__item = self.__cache.items.getItemByCD(itemId)
        self.__builder = None
        if not self.__item:
            _logger.warning('ArmoryYardShop item %s not found', itemId)
            return
        else:
            if self.__item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                self.__builder = ArmoryOptDeviceBonusesDescriptionBuilder()
            return

    @property
    def isSupported(self):
        return bool(self.__item)

    @property
    def icon(self):
        return getStorageItemIcon(self.__item, STORE_CONSTANTS.ICON_SIZE_SMALL)

    @property
    def largeIcon(self):
        return getStorageItemIcon(self.__item, STORE_CONSTANTS.ICON_SIZE_MEDIUM)

    @property
    def title(self):
        return getStorageItemName(self.__item)

    @property
    def description(self):
        if self.__item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            return ''
        elif self.__item.itemTypeID != GUI_ITEM_TYPE.BATTLE_BOOSTER:
            return self.__item.formattedShortDescription(self.__DEFAULT_TEMPLATE)
        elif self.__item.isCrewBooster():
            return self.__item.shortDescriptionSpecial
        else:
            return self.__item.getEconomicDirectivesDescription() if self.__item.isEconomicBooster() else self.__item.getOptDeviceBoosterDescription(None, valueFormatter=self.__format)

    @property
    def longDescription(self):
        if self.__item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            return backport.text(R.strings.tooltips.advanced.dyn(self.__item.descriptor.archetype)())
        elif self.__item.itemTypeID != GUI_ITEM_TYPE.BATTLE_BOOSTER:
            return self.__item.fullDescription
        elif self.__item.isCrewBooster():
            return self.__item.fullDescriptionSpecial
        else:
            return self.__item.longDescriptionSpecial if self.__item.isEconomicBooster() else self.__item.getOptDeviceBoosterDescription(None)

    @property
    def nationFlagIcon(self):
        return _getNationFlagIcon(self.__item)

    @property
    def effect(self):
        return self.__builder.getEffectDescription(self.__item) if self.__builder is not None else ''

    @property
    def template(self):
        return TemplateType.ECONOMICBOOSTER if self.__item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER and self.__item.isEconomicBooster() else TemplateType.MAINTAIN

    @property
    def itemType(self):
        itemType = self.__item.getOverlayType()
        return itemType if itemType else self.__item.itemTypeName

    def __setExtraParams(self, model):
        if self.__builder is None:
            return
        else:
            for param in self.__builder.getDescriptionByKpiStrings(self.__item):
                model.addString(param)

            model.invalidate()
            return

    def __setSpecializations(self, model):
        if self.__builder is None:
            return
        else:
            for specialization in getCategoriesIcons(self.__item):
                model.addString(specialization)

            model.invalidate()
            return

    def __format(self, value):
        return self.__BATTLE_BOOSTER_FORMATTER.format(value)

    def pack(self, model, isLargeIcon=False):
        if not super(ItemPacker, self).pack(model, isLargeIcon):
            return False
        model.setItemType(self.itemType)
        self.__setExtraParams(model.getExtraParams())
        self.__setSpecializations(model.getSpecializations())
        return True


class VehiclePacker(ShopBaseUIPacker):
    __cache = dependency.descriptor(IItemsCache)
    __COLOR_OPEN_TAG = '%(E9E2BF_open)s'
    __COLOR_CLOSE_TAG = '%(E9E2BF_close)s'

    def __init__(self, params):
        self.__vehicleId, self.__isOtherBonus, self.__isCrew, self.__isSlot, self.__armoryEpisode = params
        self.__item = self.__cache.items.getItemByCD(self.__vehicleId)
        super(VehiclePacker, self).__init__(1)
        if not self.__item:
            _logger.warning('ArmoryYardShop vehicle %s not found', self.__vehicleId)

    @property
    def vehicleId(self):
        return self.__vehicleId

    @property
    def isSupported(self):
        return bool(self.__item)

    @property
    def icon(self):
        return self.__item.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL)

    @property
    def largeIcon(self):
        return self.__item.getShopIcon(STORE_CONSTANTS.ICON_SIZE_MEDIUM)

    @property
    def title(self):
        return backport.text(R.strings.armory_shop.product.bundle.title(), vehicleName=self.__item.userName) if self.__isOtherBonus else getStorageItemName(self.__item)

    @property
    def template(self):
        return TemplateType.BUNDLE if self.__isOtherBonus else TemplateType.VEHICLE

    @property
    def longDescription(self):
        return backport.text(R.strings.armory_shop.product.bundle.longDescription.dyn('episode{}'.format(self.__armoryEpisode))()) if self.__isOtherBonus else self.__item.longDescriptionSpecial

    @property
    def nationFlagIcon(self):
        return _getNationFlagIcon(self.__item)

    @property
    def itemType(self):
        return 'bundle' if self.__isOtherBonus else self.__item.itemTypeName

    def __setExtraParams(self, model):
        extraParams = model.getExtraParams()
        if not self.__isOtherBonus:
            extraParams.addString(self.__item.shortDescriptionSpecial)
            extraParams.invalidate()
            return
        extraParams.addString(backport.text(R.strings.armory_shop.product.bundle.vehDescr(), vehicleName=self.__item.userName, vehicleLvl=model.getVehicleLevel(), color_open=self.__COLOR_OPEN_TAG, color_close=self.__COLOR_CLOSE_TAG))
        if self.__armoryEpisode > 0:
            extraParams.addString(backport.text(R.strings.armory_shop.product.bundle.armoryExtDescr(), color_open=self.__COLOR_OPEN_TAG, color_close=self.__COLOR_CLOSE_TAG))
        extraParams.invalidate()

    def pack(self, model, isLargeIcon=False):
        if not super(VehiclePacker, self).pack(model, isLargeIcon):
            return False
        model.setVehicleType(getTypeUserName(self.__item.type, self.__item.isElite))
        model.setVehicleLevel(int2roman(self.__item.level))
        if self.__item.role != ROLE_TYPE.NOT_DEFINED:
            model.setVehicleRoleName(ROLE_TYPE_TO_LABEL[self.__item.role])
        model.setAvailable(not self.__item.inventoryCount and not self.__item.isRestoreAvailable())
        model.setItemType(self.itemType)
        self.__setExtraParams(model)
        return True


class BundlePacker(ShopBaseUIPacker):
    __TEMPLATES = {'bundle': TemplateType.BUNDLE,
     'other': TemplateType.OTHER,
     'maintain': TemplateType.MAINTAIN,
     'customization': TemplateType.CUSTOMIZATION,
     'economicBooster': TemplateType.ECONOMICBOOSTER}

    def __init__(self, params):
        self.__keyName, self.__category, self.count = params
        super(BundlePacker, self).__init__(self.count)

    @property
    def isSupported(self):
        return True

    @property
    def icon(self):
        return backport.image(R.images.armory_yard.gui.maps.icons.shop.bundles.c_180x135.dyn(self.__keyName)())

    @property
    def largeIcon(self):
        return backport.image(R.images.armory_yard.gui.maps.icons.shop.bundles.c_400x300.dyn(self.__keyName)())

    @property
    def title(self):
        return backport.text(R.strings.armory_shop.bundles.dyn(self.__keyName).title())

    @property
    def template(self):
        return self.__TEMPLATES.get(self.__category, None)

    @property
    def description(self):
        return backport.text(R.strings.armory_shop.bundles.dyn(self.__keyName).description())

    @property
    def longDescription(self):
        return backport.text(R.strings.armory_shop.bundles.dyn(self.__keyName).longDescription())

    def pack(self, model, isLargeIcon=False):
        return False if not super(BundlePacker, self).pack(model, isLargeIcon) else True


_BONUS_PACKS = {'customizations': CustomizationPacker,
 'goodies': GoodiesPacker,
 'items': ItemPacker,
 'vehicles': VehiclePacker,
 'bundle': BundlePacker,
 PREMIUM_ENTITLEMENTS.PLUS: PremiumPlusPacker,
 Currency.CREDITS: CreditsPacker,
 Currency.CRYSTAL: CrystalPacker,
 Currency.GOLD: GoldPacker,
 Currency.FREE_XP: FreeXpPacker,
 Currency.EQUIP_COIN: EquipCoinPacker}

def packShopItem(productId, productParams, itemModel=None, isLargeIcon=False):
    packer = getBonusPacker(productId, **productParams)
    if itemModel is None:
        itemModel = ArmoryYardShopItem()
    itemModel.setItemID(productId)
    if 'limit' in productParams:
        itemModel.setLimit(max(productParams['limit'] - productParams.get('currCount', 0), 0))
    else:
        itemModel.setLimit(-1)
    itemModel.setIsOnlyArmoryCoins(productParams.get('onlyArmoryCoins', False))
    itemModel.setCoinsCost(productParams['price'])
    return itemModel if packer and packer.pack(itemModel, isLargeIcon) else None


def getBonusPacker(productId, bonus, **kwargs):
    bonusItems = {}
    isCrew = isSlot = False
    exclusiveVehicleID = kwargs.get('exclusiveVehicle', None)
    uiSection = kwargs.get('UI', {})
    packAsBundle = kwargs.get('packAsBundle', uiSection.get('packAsBundle', {}))
    vehicleID = None
    for bonusType, bonusValue in bonus.iteritems():
        if bonusType == 'vehicles':
            for vehID, attr in bonusValue.iteritems():
                if exclusiveVehicleID is not None and exclusiveVehicleID != vehID:
                    continue
                vehicleID = vehID
                if attr.get('crewLvl', 0) > 0:
                    isCrew = True
                break

            continue
        if bonusType == 'slots':
            isSlot = True
            continue
        bonusItems[bonusType] = bonusValue

    if packAsBundle:
        bonusType = 'bundle'
        bonusValue = [packAsBundle.get('useKeyName'), packAsBundle.get('category'), kwargs.get('count', 0)]
    elif vehicleID is not None:
        bonusType = 'vehicles'
        bonusValue = [vehicleID,
         bool(bonusItems),
         isCrew,
         isSlot,
         uiSection.get('armoryEpisode', 0)]
    else:
        bonusType, bonusValue = bonusItems.items()[0]
    if bonusType == 'customizations':
        bonusValue = (productId, bonusValue)
    if bonusType not in _BONUS_PACKS:
        _logger.warning('ArmoryYardShop bonus packer %s not found', bonusType)
        return
    else:
        packer = _BONUS_PACKS[bonusType](bonusValue)
        return packer
