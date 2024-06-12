# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/bonuses/bonuses_packers.py
import copy
import logging
import typing
import constants
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from gui.collection.collections_constants import COLLECTION_ITEM_BONUS_NAME
from gui.collection.collections_helpers import getItemName, getCollectionRes
from gui.impl import backport
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.money import Money
from gui.shared.utils.functions import makeTooltip
from gui_lootboxes.gui.bonuses.bonuses_helpers import TOKEN_COMPENSATION_PREFIX, parseCompenstaionToken
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.compensation_bonus_model import CompensationBonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.customization_bonus_model import CustomizationBonusModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.server_events.bonuses import getServiceBonuses, CollectionEntitlementBonus, AnyCollectionItemBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BonusUIPacker, CustomizationBonusUIPacker, SimpleBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap, TankmenBonusUIPacker, TokenBonusUIPacker, CrewBookBonusUIPacker, DogTagComponentsUIPacker, PremiumDaysBonusPacker
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.dog_tag_bonus_model import DogTagBonusModel, DogTagType
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.vehicle_bonus_model import VehicleBonusModel, VehicleType
from helpers import dependency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
from skeletons.gui.game_control import ICollectionsSystemController
_logger = logging.getLogger(__name__)
EXTRA_BONUS_PACKER_MAPS_DEFAULT = {}
EXTRA_BONUS_PACKER_MAPS_REWARDS = {}
EXTRA_BONUS_PACKER_MAPS_MAIN_REWARDS = {}

def getLootBoxesBonusPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': LootBoxVehiclesBonusUIPacker(),
     'crewBooks': LootBoxCrewBookBonusUIPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'customizations': LootBoxCustomizationBonusUIPacker(),
     'collectionItem': LootBoxAnyCollectionItemBonusUIPacker(),
     'anyCollectionItem': LootBoxAnyCollectionItemBonusUIPacker(),
     'dogTagComponents': LootBoxDogTagUIPacker()})
    mapping.update(EXTRA_BONUS_PACKER_MAPS_DEFAULT)
    return mapping


def getLootBoxesBonusPacker():
    return BonusUIPacker(getLootBoxesBonusPackerMap())


def getLootboxesWithPossibleCompensationBonusPacker():
    mapping = getLootBoxesBonusPackerMap()
    mapping.update({'vehicles': LootBoxVehiclesWithPossibleCompensationBonusUIPacker()})
    return BonusUIPacker(mapping)


def getRewardsScreenDefaultBonusPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'tmanToken': TmanTemplateBonusPacker(),
     'vehicles': LootBoxVehiclesBonusUIPacker(),
     'customizations': LootBoxCustomizationBonusUIPacker(),
     'tankmen': LootBoxTankmenBonusUIPacker(),
     'collectionItem': LootBoxCollectionItemBonusUIPacker(),
     'battleToken': LootBoxTokensBonusUIPacker(),
     'dogTagComponents': LootBoxDogTagUIPacker(),
     'anyCollectionItem': LootBoxAnyCollectionItemBonusUIPacker(),
     constants.PREMIUM_ENTITLEMENTS.PLUS: PremiumDaysBonusPacker()})
    mapping.update(EXTRA_BONUS_PACKER_MAPS_REWARDS)
    return mapping


def getAdditionalRewardsTooltipBonusPacker():
    mapping = getRewardsScreenDefaultBonusPackerMap()
    mapping.update({'customizations': AdditionalRewardsCustomizationBonusUIPacker(),
     'vehicles': VehiclesBonusUIPacker()})
    return BonusUIPacker(mapping)


def getRewardsBonusPacker():
    return BonusUIPacker(getRewardsScreenDefaultBonusPackerMap())


def getMainRewardsBonusPacker():
    mapping = getRewardsScreenDefaultBonusPackerMap()
    mapping.update({'tmanToken': TmanTemplateRewardScreenBonusPacker(),
     'customizations': LootBoxUniqueCustomizationBonusUIPacker()})
    mapping.update(EXTRA_BONUS_PACKER_MAPS_MAIN_REWARDS)
    return BonusUIPacker(mapping)


class LootBoxTankmenBonusUIPacker(TankmenBonusUIPacker):
    _WOMAN_ICON = 'tankwoman'
    _MAN_ICON = 'tankman'

    @classmethod
    def _pack(cls, bonus):
        result = []
        for group in bonus.getTankmenGroups().itervalues():
            result.append(cls._packTankmanBonus(bonus, group, cls._getLabel(group)))

        return result

    @classmethod
    def _packTankmanBonus(cls, bonus, group, label):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setLabel(label)
        model.setIcon(cls._WOMAN_ICON if group.isFemales else cls._MAN_ICON)
        return model


class LootBoxTankmenRewardsBonusUIPacker(LootBoxTankmenBonusUIPacker):

    @classmethod
    def _packTankmanBonus(cls, bonus, group, label):
        model = super(LootBoxTankmenRewardsBonusUIPacker, cls)._packTankmanBonus(bonus, group, label)
        if group.isUnique:
            model.setIcon(group.name)
        return model


class TmanTemplateBonusPacker(SimpleBonusUIPacker):
    _WOMAN_ICON = 'tankwoman'
    _MAN_ICON = 'tankman'

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = cls._getBonusModel()
            cls._packCommon(bonus, model)
            model.setIcon(cls._WOMAN_ICON if recruit.isFemale() else cls._MAN_ICON)
            model.setLabel(recruit.getFullUserName())
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class TmanTemplateRewardScreenBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(TmanTemplateRewardScreenBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        if model is not None:
            recruit = getRecruitInfo(tokenID)
            if recruit.isUnique():
                model.setIcon(recruit.getGroupName())
        return model


class LootBoxCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            compensation = item.get('customCompensation', None)
            if compensation:
                compBonus = cls.__getCompBonus(compensation)
                if compBonus:
                    packer = LootBoxCompensationBonusUIPacker()
                    result.extend(packer.pack(compBonus))
            result.append(cls._packSingleBonus(bonus, item, cls._getLabel(bonus.getC11nItem(item))))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setLabel(label)
        c11Item = bonus.getC11nItem(item)
        model.setItem(str(c11Item.itemTypeName) + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else '')
        model.setCustomizationID(c11Item.innationID)
        model.setIcon(cls._getIcon(bonus, c11Item))
        return model

    @classmethod
    def _getBonusModel(cls):
        return CustomizationBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            compensation = item.get('customCompensation', None)
            if compensation:
                compBonus = cls.__getCompBonus(compensation)
                if compBonus:
                    tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[compBonus, bonus]))
            itemCustomization = bonus.getC11nItem(item)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=itemCustomization.intCD)))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for b in bonus.getCustomizations():
            if b is not None:
                compensation = b.get('customCompensation', None)
                if compensation:
                    compBonus = cls.__getCompBonus(compensation)
                    if compBonus:
                        result.append(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip())
                else:
                    result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def _getIcon(cls, bonus, c11Item):
        return str(c11Item.itemTypeName) + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else str(c11Item.itemTypeName)

    @classmethod
    def __getCompBonus(cls, compensation):
        money = Money.makeMoney(compensation)
        if money is not None:
            for currency, value in money.iteritems():
                if value:
                    return first(getServiceBonuses(currency, value, isCompensation=True))

        return

    @classmethod
    def _getLabel(cls, c11nItem):
        userName = c11nItem.userName
        elementBonusR = R.strings.vehicle_customization.elementBonus.desc.dyn(c11nItem.itemFullTypeName, R.invalid)
        return backport.text(elementBonusR(), value=userName) if elementBonusR else userName


class LootBoxUniqueCustomizationBonusUIPacker(LootBoxCustomizationBonusUIPacker):

    @classmethod
    def _getIcon(cls, bonus, c11Item):
        itemTypeName = str(c11Item.itemTypeName)
        iconName = '{}_{}'.format(itemTypeName + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else itemTypeName, c11Item.innationID)
        if R.images.gui.maps.icons.quests.bonuses.s600x450.dyn(iconName).exists():
            return iconName
        return itemTypeName + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else itemTypeName


class AdditionalRewardsCustomizationBonusUIPacker(LootBoxCustomizationBonusUIPacker):

    @classmethod
    def _getLabel(cls, c11nItem):
        return c11nItem.userName


class LootBoxCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        book, count = first(bonus.getItems())
        model = cls._packSingleBonus(bonus, book, count)
        if len(bonus.getValue()) > 1:
            model.setLabel(book.randomUserName)
            model.setIcon(book.getUniversalBonusIconName())
        else:
            model.setLabel(book.userName)
            model.setIcon(book.getBonusIconName())
        result.append(model)
        return result

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        item, count = first(bonus.getItems())
        if len(bonus.getValue()) == 1:
            specialAlias, specialArgs = TOOLTIPS_CONSTANTS.CREW_BOOK, (item.intCD, count)
        else:
            specialAlias, specialArgs = TOOLTIPS_CONSTANTS.RANDOM_CREWBOOK, (item.intCD, item)
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs)]

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]


class LootBoxCompensationBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(LootBoxCompensationBonusUIPacker, cls)._packSingleBonus(bonus, label)
        model.setCompensatedBonus(bonus.getCompensationReason().getName() if bonus.getCompensationReason() else '')
        return model

    @classmethod
    def _getBonusModel(cls):
        return CompensationBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[cls._getCompensatedBonus(bonus), bonus])]

    @classmethod
    def _getCompensatedBonus(cls, bonus):
        compensatedBonus = bonus.getCompensationReason()
        if compensatedBonus and compensatedBonus.getName() == 'vehicles':
            bonusValue = copy.deepcopy(compensatedBonus.getValue())
            for item in bonusValue:
                for vehInfo in item.values():
                    if vehInfo.get('compensatedNumber', 0) > 0:
                        vehInfo['compensatedNumber'] -= 1

            return getServiceBonuses(compensatedBonus.getName(), bonusValue)[0]
        return compensatedBonus

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip()]


class LootBoxPossibleCompensationBonusUIPacker(LootBoxCompensationBonusUIPacker):

    @classmethod
    def _getCompensatedBonus(cls, bonus):
        return bonus.getCompensationReason()


class LootBoxTokensBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = super(LootBoxTokensBonusUIPacker, cls)._pack(bonus)
        for tokenID, record in bonus.getTokens().iteritems():
            if tokenID.startswith(TOKEN_COMPENSATION_PREFIX):
                currency, value, _, _ = parseCompenstaionToken(tokenID)
                bonus = first(getServiceBonuses(currency, value * record.count, isCompensation=True))
                if bonus:
                    packer = LootBoxCompensationBonusUIPacker()
                    result.extend(packer.pack(bonus))

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(LootBoxTokensBonusUIPacker, cls)._getToolTip(bonus)
        for tokenID, record in bonus.getTokens().iteritems():
            if tokenID.startswith(TOKEN_COMPENSATION_PREFIX):
                currency, value, item, itemID = parseCompenstaionToken(tokenID)
                bonus = first(getServiceBonuses(currency, value * record.count, isCompensation=True))
                if bonus:
                    result.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[cls.__getCompReasonBonus(item, itemID), bonus]))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(TOKEN_COMPENSATION_PREFIX):
                result.append(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip())
            if tokenID.startswith(constants.LOOTBOX_TOKEN_PREFIX):
                result.append(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip())
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __getCompReasonBonus(cls, item, itemID):
        return AnyCollectionItemBonus('anyCollectionItem', itemID, False) if item == 'cllc' else None


class LootBoxVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setName(bonus.getName())
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setType(VehicleType(vehicle.type))
        model.setNationTag(vehicle.nationName)
        model.setLevel(vehicle.level)
        model.setIsCompensation(bonus.isCompensation())
        model.setIsElite(vehicle.isElite)
        model.setIsRent(vehicle.isRented)
        model.setInInventory(vehicle.isInInventory)
        model.setWasSold(vehicle.restoreInfo is not None)
        if isRent:
            model.setRentDays(bonus.getRentDays(vehInfo) or 0)
            model.setRentBattles(bonus.getRentBattles(vehInfo) or 0)
        model.setLabel(cls._getLabel(vehicle))
        model.setShortVehicleLabel(vehicle.shortUserName)
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = LootBoxCompensationBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        return LootBoxCompensationBonusUIPacker().getToolTip(bonusComp)

    @classmethod
    def _getContentId(cls, bonus):
        contentIds = []
        vehicles = bonus.getVehicles()
        for vehicle, _ in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    packer = LootBoxCompensationBonusUIPacker()
                    contentIds.extend(packer.getContentId(bonusComp))

            contentIds.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return contentIds


class LootBoxVehiclesWithPossibleCompensationBonusUIPacker(LootBoxVehiclesBonusUIPacker):

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = LootBoxCompensationBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))
            if bonus.isNonZeroCompensation(vehInfo):
                packer = LootBoxPossibleCompensationBonusUIPacker()
                compensationBonuses = bonus.getPossibleCompensationBonuses(vehicle, bonus)
                for compensationBonus in compensationBonuses:
                    if not compensationBonus.isShowInGUI():
                        continue
                    packedVehicles.extend(packer.pack(compensationBonus))

        return packedVehicles

    @classmethod
    def _packTooltips(cls, bonus, vehicles):
        packedTooltips = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    packedTooltips.extend(cls._packCompensationTooltip(bonusComp, vehicle))

            packedTooltips.append(cls._packTooltip(bonus, vehicle, vehInfo))
            if bonus.isNonZeroCompensation(vehInfo):
                packer = LootBoxPossibleCompensationBonusUIPacker()
                compensationBonuses = bonus.getPossibleCompensationBonuses(vehicle, bonus)
                for compensationBonus in compensationBonuses:
                    if not compensationBonus.isShowInGUI():
                        continue
                    packedTooltips.extend(packer.getToolTip(compensationBonus))

        return packedTooltips

    @classmethod
    def _getContentId(cls, bonus):
        contentIds = []
        vehicles = bonus.getVehicles()
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    packer = LootBoxCompensationBonusUIPacker()
                    contentIds.extend(packer.getContentId(bonusComp))

            contentIds.append(BACKPORT_TOOLTIP_CONTENT_ID)
            if bonus.isNonZeroCompensation(vehInfo):
                packer = LootBoxPossibleCompensationBonusUIPacker()
                compensationBonuses = bonus.getPossibleCompensationBonuses(vehicle, bonus)
                for compensationBonus in compensationBonuses:
                    if not compensationBonus.isShowInGUI():
                        continue
                    contentIds.extend(packer.getContentId(compensationBonus))

        return contentIds


class LootBoxCollectionItemBonusUIPacker(SimpleBonusUIPacker):
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')] if cls._isValidBonus(bonus) else []

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        item = bonus.getItem()
        model.setIcon('{}_{}_{}'.format(item.type, bonus.getCollectionId(), bonus.getItemId()))
        model.setLabel(getItemName(bonus.getCollectionId(), item))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[bonus.getItemId(), bonus.getCollectionId()])] if cls._isValidBonus(bonus) else []

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.collection.tooltips.CollectionItemTooltipView()] if cls._isValidBonus(bonus) else []

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _isValidBonus(cls, bonus):
        return cls.__collectionsSystem.getCollection(bonus.getCollectionId()) is not None


class LootBoxDogTagUIPacker(DogTagComponentsUIPacker):
    _DOG_TAG_VIEW_TYPE_TO_DOG_TAG_TYPE_ENUM = {ComponentViewType.ENGRAVING: DogTagType.ENGRAVING,
     ComponentViewType.BACKGROUND: DogTagType.BACKGROUND}

    @classmethod
    def _getBonusModel(cls):
        return DogTagBonusModel()

    @classmethod
    def _packDogTag(cls, bonus, dogTagRecord):
        model = super(LootBoxDogTagUIPacker, cls)._packDogTag(bonus, dogTagRecord)
        dogTagComponent = componentConfigAdapter.getComponentById(dogTagRecord.componentId)
        model.setDogTagType(cls._DOG_TAG_VIEW_TYPE_TO_DOG_TAG_TYPE_ENUM[dogTagComponent.viewType])
        return model


class LootBoxAnyCollectionItemBonusUIPacker(LootBoxCollectionItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setName(COLLECTION_ITEM_BONUS_NAME)
        model.setIcon('any_{}'.format(bonus.getCollectionId()))
        model.setLabel(backport.text(getCollectionRes(bonus.getCollectionId()).anyCollectionItem.name()))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(makeTooltip(header=backport.text(getCollectionRes(bonus.getCollectionId()).anyCollectionItem.tooltip.header()), body=backport.text(getCollectionRes(bonus.getCollectionId()).anyCollectionItem.tooltip.header())))] if cls._isValidBonus(bonus) else []

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID] if cls._isValidBonus(bonus) else []

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()
