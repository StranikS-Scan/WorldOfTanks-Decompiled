# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/challenges/challenges_bonuses_packers.py
from __future__ import absolute_import
import copy
import logging
import typing
from future.utils import viewitems
from battle_pass_common import CurrencyBP
from challenges_common import ChallengeMainRewardTypes
from constants import PREMIUM_ENTITLEMENTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import getSingleVehicleForCustomization
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.challenges.bonus_model import BonusModel, VehicleType
from gui.impl.gen.view_models.views.lobby.challenges.skill_model import SkillModel
from gui.server_events.awards_formatters import AWARDS_SIZES, BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN
from gui.server_events.bonuses import _BONUSES, AttachmentsSetTokenBonus, BlueprintsBonusSubtypes, VehiclesBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import getIconResourceName, getUnicName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, AttachmentsSetTokenBonusPacker, BaseBonusUIPacker, BlueprintBonusUIPacker, BonusUIPacker, CrewBookBonusUIPacker, CrewSkinBonusUIPacker, CurrenciesBonusUIPacker, Customization3Dand2DbonusUIPacker, GoodiesBonusUIPacker, ItemBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap, getLocalizedBonusName
from gui.shared.money import Currency, Money
from helpers import dependency, int2roman
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from typing import List
_logger = logging.getLogger(__name__)
VEH_COMP_R_ID = R.views.mono.battle_pass.tooltips.reward_compensation()

def _getVehicleUIData(vehicle):
    return {'vehicleName': vehicle.shortUserName,
     'vehicleType': getIconResourceName(vehicle.type),
     'isElite': vehicle.isElite,
     'vehicleLvl': int2roman(vehicle.level),
     'vehicleLvlNum': vehicle.level}


def getChallengesPostBattleBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': Customization3Dand2DbonusUIPacker(),
     'currencies': ChallengesCurrenciesBonusUIPacker(),
     'tmanToken': ChallengesPostBattleTmanTemplateBonusUIPacker(),
     'lootBox': ChallengesPostBattleLootBoxBonusUIPacker(),
     PREMIUM_ENTITLEMENTS.PLUS: ChallengesPostBattlePremiumBonusUIPacker(),
     Currency.BPCOIN: ChallengesBPCoinBonusUIPacker()})
    return BonusUIPacker(mapping)


def getChallengesBonusPacker():
    mapping = getDefaultBonusPackersMap()
    currencyPacker = ChallengesCurrencyBonusUIPacker()
    mapping.update({'battleToken': ChallengesTokenBonusUIPacker(),
     'blueprints': ChallengesBlueprintBonusUIPacker(),
     'crewBooks': ChallengesCrewBookBonusUIPacker(),
     'crewSkins': ChallengesCrewSkinBonusUIPacker(),
     'customizations': ChallengesCustomizationsBonusUIPacker(),
     'currencies': ChallengesCurrenciesBonusUIPacker(),
     'goodies': ChallengesGoodiesBonusUIPacker(),
     'items': ChallengesItemBonusUIPacker(),
     'slots': ChallengesSlotsBonusUIPacker(),
     'tmanToken': ChallengesTmanTemplateBonusUIPacker(),
     'tokens': ChallengesTokenBonusUIPacker(),
     'vehicles': ChallengesVehiclesBonusUIPacker(),
     'lootBox': ChallengesLootBoxBonusUIPacker(),
     Currency.FREE_XP: currencyPacker,
     Currency.CREDITS: currencyPacker,
     Currency.GOLD: currencyPacker,
     Currency.EQUIP_COIN: currencyPacker,
     Currency.CRYSTAL: currencyPacker,
     Currency.BPCOIN: ChallengesBPCoinBonusUIPacker(),
     PREMIUM_ENTITLEMENTS.PLUS: ChallengesPremiumBonusUIPacker(),
     AttachmentsSetTokenBonus.NAME: ChallengesAttachmentsSetTokenBonusPacker()})
    return BonusUIPacker(mapping)


class ChallengesSlotsBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(bonus.getValue())
        model.setIcon(bonus.getName())
        model.setLabel(backport.text(R.strings.tooltips.awardItem.slots.header()))
        return model


class ChallengesCurrencyBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        cls._packCommon(bonus, model)
        bonusName = bonus.getName()
        model.setIcon(bonusName)
        model.setValue(str(bonus.getValue()))
        model.setLabel(str(bonus.getValue()))
        model.setDescription(getLocalizedBonusName(bonusName))
        if ChallengeMainRewardTypes.hasValue(bonusName):
            model.setBonusType(bonusName)
        return model


class ChallengesVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    __customizationService = dependency.descriptor(ICustomizationService)

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = cls.__getCompensation(bonus, vehInfo)
            if compensation:
                packer = ChallengesCurrencyBonusUIPacker
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setBonusType(ChallengeMainRewardTypes.VEHICLE.value)
        styleID = vehInfo.get('customization', {}).get('styleId')
        if styleID is not None and vehicle.isOutfitLocked:
            style = cls.__customizationService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
            model.setStyleID(styleID)
            model.setDescription(backport.text(R.strings.challenges.bonuses.description.lockedStyle(), styleName=style.userName))
        model.setName(bonus.getName())
        model.setIsRent(isRent)
        model.setIsCompensation(bool(cls.__getCompensation(bonus, vehInfo)))
        cls.__fillVehicleInfo(model, vehicle)
        return model

    @classmethod
    def __fillVehicleInfo(cls, model, vehicle):
        model.setIsInHangar(vehicle.isInInventory)
        model.setId(vehicle.intCD)
        model.setLabel(vehicle.userName)
        model.setVehicleShortName(vehicle.shortUserName)
        model.setType(VehicleType(vehicle.type))
        model.setLevel(vehicle.level)
        model.setIsElite(vehicle.isElite)
        model.setIcon(getUnicName(vehicle.name))

    @classmethod
    def _packTooltips(cls, bonus, vehicles):
        packedTooltips = []
        for vehicle, vehInfo in vehicles:
            compensation = cls.__getCompensation(bonus, vehInfo)
            if compensation:
                for bonusComp in compensation:
                    packedTooltips.extend(cls._packCompensationTooltip(bonusComp, vehicle, vehInfo))

            packedTooltips.append(cls._packTooltip(bonus, vehicle, vehInfo))

        return packedTooltips

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        compensation = cls.__getCompensation(bonus, vehInfo)
        return first(cls._packCompensationTooltip(first(compensation), vehicle, vehInfo)) if compensation else super(ChallengesVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)

    @classmethod
    def _packCompensationTooltip(cls, compensationBonus, vehicle, vehicleInfo):
        vehicleInfoCopy = copy.deepcopy(vehicleInfo)
        vehicleInfoCopy.pop('compensatedNumber', None)
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[VehiclesBonus('vehicles', {vehicle.intCD: vehicleInfoCopy}), compensationBonus])]

    @classmethod
    def _getContentId(cls, bonus):
        outcome = []
        for _, vehInfo in bonus.getVehicles():
            compensation = cls.__getCompensation(bonus, vehInfo)
            if compensation:
                outcome.append(VEH_COMP_R_ID)
            outcome.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return outcome

    @classmethod
    def __getCompensation(cls, bonus, vehInfo):
        compBonuses = []
        compensatedNumber = vehInfo.get('compensatedNumber', 0)
        compensation = vehInfo.get('customCompensation')
        if compensatedNumber and compensation is not None:
            money = Money(*compensation)
            for currency, value in viewitems(money):
                if value:
                    bonusClass = _BONUSES.get(currency)
                    compBonuses.append(bonusClass(currency, value, isCompensation=True, compensationReason=bonus))

        return compBonuses


class ChallengesLootBoxBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        box = bonus.getBox()
        model.setId(bonus.lootBoxID)
        model.setIcon('lootBox_' + box.getCategory() if box else bonus.getName())
        model.setCount(bonus.getCount())
        model.setLabel(box.getUserName() if box else '')
        return model

    @classmethod
    def _getContentId(cls, _):
        return [R.views.mono.lootbox.tooltips.box_tooltip()]

    @classmethod
    def _getToolTip(cls, bonus):
        box = bonus.getBox()
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[box.getCategory(), box.getType()])]


class ChallengesCustomizationsBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item, data in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None or cls.__isLockedStyle(bonus, item):
                continue
            compensation = cls.__getCompensation(bonus)
            if compensation:
                for compensationBonus in compensation:
                    packer = ChallengesCurrencyBonusUIPacker()
                    result.extend(packer.pack(compensationBonus))

            result.append(cls._packSingleBonus(bonus, item, data))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, data):
        model = BonusModel()
        model.setName(bonus.getName())
        custItem = bonus.getC11nItem(item)
        itemName = custItem.itemTypeName
        description = getLocalizedBonusName(itemName)
        if itemName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT]:
            model.setName(itemName)
            model.setIcon(custItem.name)
            model.setOverlayType(custItem.rarity)
            description = backport.text(R.strings.item_types.customization.attachment.rarity(), rarity=backport.text(R.strings.vehicle_customization.customization.rarity.dyn(custItem.rarity)()))
        else:
            if itemName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE]:
                vehicleCD = getSingleVehicleForCustomization(custItem)
                model.setIsInHangar(vehicleCD is not None and custItem.fullInventoryCount() > 0)
                if custItem.is3D:
                    itemName = 'style_3d'
                    model.setIsCompensation(bool(cls.__getCompensation(bonus)))
                    model.setBonusType(ChallengeMainRewardTypes.STYLE_3D.value)
                else:
                    model.setBonusType(ChallengeMainRewardTypes.STYLE_2D.value)
                description = backport.text(R.strings.challenges.bonuses.description.dyn(itemName)())
            model.setIcon(itemName)
        model.setId(custItem.id)
        model.setCount(item.get('value', 0))
        model.setDescription(description)
        model.setLabel(custItem.userName)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, _ in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None:
                continue
            itemCustomization = bonus.getC11nItem(item)
            specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD
            specialArgs = CustomizationTooltipContext(itemCD=itemCustomization.intCD)
            if itemCustomization.itemTypeName in (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE], GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE]):
                vehicle = getSingleVehicleForCustomization(itemCustomization)
                if vehicle is not None:
                    specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM
                    specialArgs = CustomizationTooltipContext(itemCD=itemCustomization.intCD, vehicleIntCD=vehicle)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for item, _ in zip(bonus.getCustomizations(), bonus.getList()):
            if item is not None:
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __isLockedStyle(cls, bonus, item):
        item = bonus.getC11nItem(item)
        return item.itemTypeName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE] and item.isLockedOnVehicle

    @classmethod
    def __getCompensation(cls, bonus):
        for customizationItem in bonus.getCustomizations():
            compBonuses = []
            compensatedNumber = customizationItem.get('compensatedNumber', 0)
            compensation = customizationItem.get('customCompensation')
            if compensatedNumber and compensation is not None:
                money = Money.makeMoney(compensation)
                for currency, value in viewitems(money):
                    if value:
                        bonusClass = _BONUSES.get(currency)
                        compBonuses.append(bonusClass(currency, value, isCompensation=True, compensationReason=bonus))

            return compBonuses

        return


class ChallengesCrewSkinBonusUIPacker(CrewSkinBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count, label):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setIcon(str(crewSkin.itemTypeName + str(crewSkin.getRarity())))
        model.setDescription(backport.text(R.strings.challenges.bonuses.description.crewSkin()))
        model.setLabel(label)
        return model


class ChallengesCurrenciesBonusUIPacker(CurrenciesBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = BonusModel()
        model.setName(bonus.getCode())
        model.setValue(str(bonus.getValue()))
        model.setIcon(bonus.getCode())
        model.setLabel(str(bonus.getValue()))
        model.setDescription(getLocalizedBonusName(bonus.getCode()))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.mono.battle_pass.tooltips.bptaler()] if bonus.getCode() == CurrencyBP.TALER.value else super(ChallengesCurrenciesBonusUIPacker, cls)._getContentId(bonus)


class ChallengesBPCoinBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setCount(str(bonus.getValue()))
        model.setLabel(backport.text(R.strings.challenges.bonuses.bpcoin()))
        model.setIcon(bonus.getName())
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.mono.battle_pass.tooltips.bpcoin()]


class ChallengesItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        icon, overlay = (item.name, '') if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else (item.getGUIEmblemID(), item.getOverlayType())
        model.setIcon(icon)
        model.setOverlayType(overlay)
        model.setLabel(item.userName)
        model.setDescription(cls.__getDescription(item))
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isDeluxe:
            model.setBonusType(ChallengeMainRewardTypes.IMPROVED_EQUIPMENT.value)
        return model

    @classmethod
    def __getDescription(cls, item):
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            if item.isTrophy:
                return backport.text(R.strings.challenges.bonuses.description.bounty_equipment())
            if item.isModernized:
                return backport.text(R.strings.challenges.bonuses.description.experimental_equipment())
            if item.isDeluxe:
                return backport.text(R.strings.challenges.bonuses.description.improved_equipment())
            return backport.text(R.strings.challenges.bonuses.description.standard_equipment())
        return backport.text(R.strings.challenges.bonuses.description.directive()) if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else ''


class ChallengesGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        return cls._packIconBonusModel(bonus, booster.getFullNameForResource(), count, backport.text(R.strings.menu.booster.label.dyn(booster.boosterGuiType)(), effectValue=booster.getFormattedValue()), description=backport.text(R.strings.challenges.bonuses.description.booster()))

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label, description=''):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setIcon(icon)
        model.setLabel(label)
        model.setDescription(description)
        return model


class ChallengesPremiumBonusUIPacker(BaseBonusUIPacker):
    _ICONS_AVAILABLE = (1, 2, 3, 7, 14, 30, 90, 180, 360)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        icon = 'premium_plus_universal'
        days = bonus.getValue()
        if days in cls._ICONS_AVAILABLE:
            icon = '{}_{}'.format(bonus.getName(), str(days))
        model.setIcon(icon)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(days))
        model.setLabel(str(days))
        model.setDescription(backport.text(R.strings.tooltips.awardItem.premium_plus.header()))
        return model


class ChallengesTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = BonusModel()
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token,
         CREW_BONUS_X3_TOKEN: cls.__packCrewBonusX3Token}

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(ChallengesTokenBonusUIPacker, cls)._getTooltipsPackers()
        return {BATTLE_BONUS_X5_TOKEN: packers[BATTLE_BONUS_X5_TOKEN],
         CREW_BONUS_X3_TOKEN: packers[CREW_BONUS_X3_TOKEN]}

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setCount(bonus.getCount())
        model.setLabel(backport.text(R.strings.challenges.bonuses.battleBonusX5()))
        model.setIcon(BATTLE_BONUS_X5_TOKEN)
        return model

    @classmethod
    def __packCrewBonusX3Token(cls, model, bonus, *args):
        model.setCount(bonus.getCount())
        model.setLabel(backport.text(R.strings.challenges.bonuses.crewBonusX3()))
        model.setIcon(CREW_BONUS_X3_TOKEN)
        return model


class ChallengesBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        label = bonus.getBlueprintTooltipName()
        model.setIcon(bonus.getImageCategory())
        blueprintName = bonus.getBlueprintName()
        if blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            label = backport.text(R.strings.challenges.bonuses.blueprints.nationalFragment(), nation=backport.text(R.strings.blueprints.nations.dyn(bonus.getImageCategory())()))
        elif blueprintName == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
            label = backport.text(R.strings.challenges.bonuses.blueprints.universalFragment())
        model.setLabel(label)
        model.setCount(bonus.getCount())
        return [model]

    @staticmethod
    def getTooltip(bonuses):
        fragmentCDs = [ bonus.getBlueprintSpecialArgs() for bonus in bonuses ]
        specialAlias = [ bonus.getBlueprintSpecialAlias() for bonus in bonuses ]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=specialAlias, specialArgs=[fragmentCDs])


class ChallengesCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setLabel(book.userName)
        model.setIcon(book.getBonusIconName())
        return model


class ChallengesTmanTemplateBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID, tokenRecord in viewitems(bonus.getTokens()):
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                count = tokenRecord.count
                packed = cls._packTmanTemplateToken(tokenID, bonus, count)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus, count):
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = BonusModel()
            model.setName(bonus.getName())
            model.setCount(count)
            model.setIcon(cls.__getBonusImageName(recruit))
            groupName = recruit.getGroupName()
            if groupName == 'men1':
                label = backport.text(R.strings.challenges.bonuses.standardCrewMember.male())
            elif groupName == 'women1':
                label = backport.text(R.strings.challenges.bonuses.standardCrewMember.female())
            else:
                label = recruit.getFullUserName()
                model.setDescription(backport.text(R.strings.challenges.bonuses.uniqueCrewMember()))
            model.setLabel(label)
            model.setBonusType(ChallengeMainRewardTypes.CREW_MEMBER.value)
            model.setValue('' if groupName in ('men1', 'women1') else groupName)
            cls.__packTmanSkills(model.getSkills(), recruit)
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __packTmanSkills(cls, skillsArrayModel, recruit):
        for skill in recruit.getFreeSkills():
            skillModel = SkillModel()
            skillModel.setName(skill)
            skillModel.setIsZero(True)
            skillsArrayModel.addViewModel(skillModel)

        for skill in recruit.getEarnedSkills(True):
            skillModel = SkillModel()
            skillModel.setName(skill)
            skillModel.setIsZero(False)
            skillsArrayModel.addViewModel(skillModel)

        return skillsArrayModel

    @classmethod
    def __getBonusImageName(cls, recruitInfo):
        baseName = 'tank{}man'.format('wo' if recruitInfo.isFemale() else '')
        return baseName


class ChallengesAttachmentsSetTokenBonusPacker(AttachmentsSetTokenBonusPacker):

    @classmethod
    def _packSingleBonus(cls, tokenID, token, bonus):
        model = super(ChallengesAttachmentsSetTokenBonusPacker, cls)._packSingleBonus(tokenID, token, bonus)
        model.setCount(token.count)
        model.setBonusType(ChallengeMainRewardTypes.ATTACHMENTS_SET.value)
        model.setValue(tokenID)
        model.setDescription(backport.text(R.strings.challenges.bonuses.description.attachments_set()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()


class ChallengesPostBattlePremiumBonusUIPacker(SimpleBonusUIPacker):
    _ICONS_AVAILABLE = (1, 2, 3, 7, 14, 30, 90, 180, 360)

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(ChallengesPostBattlePremiumBonusUIPacker, cls)._packSingleBonus(bonus, label)
        days = bonus.getValue()
        if days in cls._ICONS_AVAILABLE:
            model.setName(bonus.getName())
        else:
            model.setName('premium_plus_universal')
        return model


class ChallengesPostBattleLootBoxBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = TokenBonusModel()
        model.setName(bonus.getName())
        box = bonus.getBox()
        boxName = box.getUserName() if box else ''
        model.setValue(str(bonus.getCount()))
        model.setLabel(boxName)
        model.setUserName(boxName)
        model.setIconSmall(bonus.getIconBySize(AWARDS_SIZES.SMALL))
        model.setIconBig(bonus.getIconBySize(AWARDS_SIZES.BIG))
        return model

    @classmethod
    def _getContentId(cls, _):
        return [R.views.mono.lootbox.tooltips.box_tooltip()]

    @classmethod
    def _getToolTip(cls, bonus):
        box = bonus.getBox()
        return [TooltipData(tooltip=None, isSpecial=False, specialAlias=None, specialArgs=[box.getCategory(), box.getType()])]


class ChallengesPostBattleTmanTemplateBonusUIPacker(ChallengesTmanTemplateBonusUIPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus, count):
        model = super(ChallengesPostBattleTmanTemplateBonusUIPacker, cls)._packTmanTemplateToken(tokenID, bonus, count)
        model.setValue(str(count))
        return model
