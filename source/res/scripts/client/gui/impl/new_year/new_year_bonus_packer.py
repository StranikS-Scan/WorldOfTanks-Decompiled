# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_bonus_packer.py
import logging
from collections import defaultdict
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_GUEST_ACTIVITY_SHOWN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import BattlePassCustomizationsBonusPacker
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import formatEliteVehicle
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel, BonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.vehicle_bonus_model import VehicleBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.guest_reward_item_model import GuestRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.progress_reward_item_model import ProgressRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.new_year_toy_icon_bonus_model import NewYearToyIconBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.vehicle_compensation_model import VehicleCompensationModel
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.rewards_model import RewardsModel
from gui.server_events.awards_formatters import MEDIUM_AWARD_SIZE, LARGE_AWARD_SIZE, EPIC_AWARD_SIZE
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap, SimpleBonusUIPacker, DossierBonusUIPacker, CustomizationBonusUIPacker, getLocalizedBonusName, VehiclesBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, VEHICLE_RENT_ICON_POSTFIX, BaseBonusUIPacker, ExtendedBlueprintBonusUIPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import int2roman, dependency
from items.components.ny_constants import TOKEN_VARIADIC_DISCOUNT_PREFIX, NyATMReward, CurrentNYConstants, NySackLootBox
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from new_year.gift_machine_helper import getCoinToken
from new_year.ny_constants import GuestsQuestsTokens, parseCelebrityTokenActionType, GUEST_ECONOMIC_BONUS_ID
from new_year.ny_toy_info import NewYearCurrentToyInfo
from new_year.variadic_discount import createDiscountBonusModel
from shared_utils import first
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional, Callable
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus, CustomizationsBonus, TokensBonus, NyToyBonus, VehiclesBonus, TmanTemplateTokensBonus
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
VEH_COMP_R_ID = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()

def getNewYearBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NYCelebrityTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'customizations': _NYCelebrityCustomizationBonusUIPacker(),
     'vehicles': NYVehiclesBonusUIPacker(),
     'nyCoinToken': NYCelebrityTokenBonusUIPacker(),
     'blueprints': ExtendedBlueprintBonusUIPacker(),
     'blueprintsAny': ExtendedBlueprintBonusUIPacker(),
     'finalBlueprints': ExtendedBlueprintBonusUIPacker()})
    return BonusUIPacker(mapping)


def getNewYearLevelUpBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NYCelebrityTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'customizations': _NYLevelUpCustomizationBonusUIPacker(),
     'vehicles': NYVehiclesBonusUIPacker(),
     'nyCoinToken': NYCelebrityTokenBonusUIPacker()})
    return BonusUIPacker(mapping)


def getChallengeBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NYCelebrityTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NYChallengeTmanTemplateBonusPacker(),
     'customizations': _NYChallengeCustomizationBonusUIPacker(),
     'vehicles': NYVehiclesBonusUIPacker(),
     'nyCoinToken': NYCelebrityTokenBonusUIPacker()})
    return BonusUIPacker(mapping)


def getPiggyBankBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': NYPiggyBankCustomizationBonusUIPacker()})
    return BonusUIPacker(mapping)


class CollapseInscriptionBonusPacker(BattlePassCustomizationsBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        if cls.__needCollapse(bonus):
            customization = first(bonus.getCustomizations())
            data = first(bonus.getList())
            return [cls._packSingleBonus(bonus, customization, data)]
        return super(CollapseInscriptionBonusPacker, cls)._pack(bonus)

    @classmethod
    def _getToolTip(cls, bonus):
        if cls.__needCollapse(bonus):
            return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.COLLAPSE_CUSTOMIZATION_ITEM_AWARD, specialArgs=[ bonus.getC11nItem(item).intCD for item in bonus.getCustomizations() ])]
        else:
            return super(CollapseInscriptionBonusPacker, cls)._getToolTip(bonus)

    @staticmethod
    def __needCollapse(bonus):
        return all((bonus.getC11nItem(cItem).itemTypeName == 'inscription' for cItem in bonus.getCustomizations()))


class NewYearTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return TOKEN_VARIADIC_DISCOUNT_PREFIX if tokenID.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX) else super(NewYearTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        mapping = super(NewYearTokenBonusUIPacker, cls)._getTokenBonusPackers()
        mapping.update({TOKEN_VARIADIC_DISCOUNT_PREFIX: cls.__packVariadicDiscounts})
        return mapping

    @classmethod
    def _getTooltipsPackers(cls):
        mapping = super(NewYearTokenBonusUIPacker, cls)._getTooltipsPackers()
        mapping.update({TOKEN_VARIADIC_DISCOUNT_PREFIX: cls.__getVariadicDiscountsTooltipData})
        return mapping

    @classmethod
    def _hasUniqueModel(cls, tokenType):
        return tokenType == TOKEN_VARIADIC_DISCOUNT_PREFIX

    @classmethod
    def __packVariadicDiscounts(cls, bonus, complexToken, token):
        return createDiscountBonusModel(token)

    @classmethod
    def __getVariadicDiscountsTooltipData(cls, *_):
        return createTooltipData()


class NewYearDossierBonusUIPacker(DossierBonusUIPacker):

    @staticmethod
    def _getAchievementLabel(achievement):
        return backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.rewards.achievement.label(), name=achievement.getUserName())


class NewYearTmanTemplateBonusPacker(BaseBonusUIPacker):
    _isBigImageUsed = False

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls.__packTmanTemplateToken(tokenID, bonus)
                if packed is not None:
                    result.append(packed)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for tokenID in bonus.getTokens().iterkeys() if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX) ]

    @classmethod
    def __packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            groupName = recruitInfo.getGroupName()
            bonusImageName = cls.__getBonusImageName(recruitInfo)
            tankManFullName = recruitInfo.getFullUserName()
            model = RewardItemModel()
            cls._packCommon(bonus, model)
            model.setIcon(bonusImageName)
            model.setBigIcon('_'.join([bonusImageName, groupName]))
            model.setUserName(tankManFullName)
            model.setLabel(tankManFullName)
            model.setIsCollectionEntity(cls._isCollectionItem(groupName))
            cls._injectAwardID(model, groupName)
            return model

    @classmethod
    def __getBonusImageName(cls, recruitInfo):
        baseName = 'tank{}man'.format('wo' if recruitInfo.isFemale() else '')
        return baseName

    @classmethod
    def _injectAwardID(cls, item, postfix=None):
        if cls._isBigImageUsed and postfix:
            item.setIcon('_'.join([item.getIcon(), postfix]))


class NYFillersBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NY_FILLERS, specialArgs=[])]


class NYVehicleCompensationBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def packCompensation(cls, bonus):
        return cls._pack(bonus)[0]

    @classmethod
    def _getBonusModel(cls):
        return VehicleCompensationModel()


class NYVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = NYVehicleCompensationBonusUIPacker()
                for bonusComp in compensation:
                    compensationModel = packer.packCompensation(bonusComp)
                    compensationModel.setVehicleLvl(vehicle.level)
                    vehicleModel = compensationModel.compensatedItem
                    vehicleModel.setName(bonus.getName())
                    vehicleModel.setIsCompensation(bonus.isCompensation())
                    vehicleModel.setLabel(vehicle.shortUserName)
                    vehicleModel.setValue(vehicle.shortUserName)
                    packedVehicles.append(compensationModel)

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        compensation = bonus.compensation(vehicle, bonus)
        return first(cls._packCompensationTooltip(first(compensation), vehicle)) if bonus.compensation(vehicle, bonus) else super(NYVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(NYVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        return [ cls.__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    @classmethod
    def _createUINameWithPrem(cls, bonus, isRent, isPremium):
        return bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName()

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setName(cls._createUINameWithPrem(bonus, isRent, vehicle.isPremium))
        model.setIsCompensation(bool(bonus.compensation(vehicle, bonus)))
        cls.__fillVehicle(model, vehicle)
        return model

    @classmethod
    def __fillVehicle(cls, model, vehicle):
        model.setLabel(vehicle.userName)
        model.setVehicleName(vehicle.userName)
        model.setIsElite(vehicle.isElite)
        model.setType(vehicle.type)
        model.setVehicleLvl(vehicle.level)
        model.setValue(vehicle.shortUserName)
        model.setUserName(getNationLessName(vehicle.name))

    @classmethod
    def _getContentId(cls, bonus):
        outcome = []
        for vehicle, _ in bonus.getVehicles():
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                outcome.append(R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent())
            outcome.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return outcome

    @classmethod
    def __convertCompensationTooltip(cls, bonusComp, vehicle, tooltipData):
        specialArgs = {'iconBefore': backport.image(R.images.gui.maps.shop.vehicles.c_180x135.dyn(getIconResourceName(getNationLessName(vehicle.name)))()),
         'labelBefore': '',
         'iconAfter': backport.image(R.images.gui.maps.icons.quests.bonuses.big.gold()),
         'labelAfter': bonusComp.getIconLabel(),
         'bonusName': bonusComp.getName(),
         'vehicleName': vehicle.shortUserName,
         'vehicleType': formatEliteVehicle(vehicle.isElite, vehicle.type),
         'isElite': vehicle.isElite,
         'vehicleLvl': int2roman(vehicle.level)}
        return createTooltipData(tooltip=tooltipData.tooltip, specialAlias=VEH_COMP_R_ID, specialArgs=specialArgs)


class NYPremVehiclesBonusUIPacker(NYVehiclesBonusUIPacker):

    @classmethod
    def _createUINameWithPrem(cls, bonus, isRent, isPremium):
        name = 'premiumTank' if isPremium else bonus.getName()
        return name + VEHICLE_RENT_ICON_POSTFIX if isRent else name


class _NYCelebrityCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_NYCelebrityCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(customization.userName)
        model.setIntCD(customization.intCD)
        return model

    @classmethod
    def _getBonusModel(cls):
        return GuestRewardItemModel()

    @classmethod
    def _createBonusModel(cls):
        return GuestRewardItemModel()


class _NYLevelUpCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_NYLevelUpCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(customization.userName)
        model.setIcon('_'.join([customization.itemFullTypeName, str(customization.id)]))
        model.setIntCD(customization.intCD)
        model.setName(customization.itemFullTypeName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return GuestRewardItemModel()

    @classmethod
    def _createBonusModel(cls):
        return GuestRewardItemModel()


class _NYChallengeCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_NYChallengeCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setIntCD(customization.intCD)
        if customization.itemTypeName == 'inscription' and int(model.getValue()) > 1:
            label = backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.inscriptions())
        elif customization.itemTypeName == 'projectionDecal' and int(model.getValue()) > 1:
            label = backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.projectionDecals())
        elif customization.itemTypeName == 'attachment':
            model.setRarity(customization.rarity)
            model.setIconName(customization.name)
            label = customization.userName
        else:
            label = backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.dyn(customization.itemTypeName)(), name=customization.userName)
        model.setLabel(str(label))
        return model

    @classmethod
    def _getBonusModel(cls):
        return ProgressRewardItemModel()

    @classmethod
    def _createBonusModel(cls):
        return ProgressRewardItemModel()

    @classmethod
    def _pack(cls, bonus):
        mergedBonuses = cls.__preformat(bonus)
        result = []
        for cItems in mergedBonuses:
            cItem = first(cItems)
            label = getLocalizedBonusName(bonus.getC11nItem(cItem).itemTypeName)
            model = cls._packSingleBonus(bonus, cItem, label if label else '')
            value = sum([ item.get('value', 0) for item in cItems ])
            model.setValue(str(value))
            result.append(model)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        mergedBonuses = cls.__preformat(bonus)
        tooltipData = []
        for cItems in mergedBonuses:
            needCollapse = len(cItems) > 1
            if needCollapse:
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SHORT_COLLAPSE_CUSTOMIZATION_ITEM_AWARD, specialArgs=[ bonus.getC11nItem(item).intCD for item in cItems ]))
            cItem = first(cItems)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=bonus.getC11nItem(cItem).intCD, context=bonus.getContext())))

        return tooltipData

    @staticmethod
    def __preformat(bonus):
        preformated = defaultdict(list)
        nonFormattedAttachments = []
        for cItem in bonus.getCustomizations():
            if cItem is None:
                continue
            itemTypeID = bonus.getC11nItem(cItem).itemTypeID
            if itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
                attachment = [cItem]
                nonFormattedAttachments.append(attachment)
            preformated[itemTypeID].append(cItem)

        return preformated.values() + nonFormattedAttachments


class NYPiggyBankCustomizationBonusUIPacker(_NYChallengeCustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(NYPiggyBankCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        label = backport.text(R.strings.ny.customizations.dyn(customization.itemTypeName)(), name=customization.userName)
        model.setLabel(str(label))
        return model


class NYChallengeTmanTemplateBonusPacker(NewYearTmanTemplateBonusPacker):
    _isBigImageUsed = True

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(NYChallengeTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        label = backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.tmanToken(), name=getRecruitInfo(tokenID).getFullUserName())
        model.setLabel(str(label))
        model.setType(getRecruitInfo(tokenID).getRecruitID())
        return model


class NYCelebrityTokenBonusUIPacker(NewYearTokenBonusUIPacker):

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        nyCoinToken = getCoinToken()
        lootbox = cls._itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
        if tokenID == nyCoinToken:
            return nyCoinToken
        if tokenID.startswith(GuestsQuestsTokens.ACTION_TOKEN_PREFIX):
            return GuestsQuestsTokens.ACTION_TOKEN_PREFIX
        if tokenID == NyATMReward.DOG_TOKEN:
            return NyATMReward.DOG
        if tokenID == NyATMReward.CAT_TOKEN:
            return NyATMReward.CAT
        if tokenID == NyATMReward.MARKETPLACE_TOKEN:
            return NyATMReward.MARKETPLACE
        if tokenID in GuestsQuestsTokens.ECONOMIC_GUESTS_TOKENS:
            return GUEST_ECONOMIC_BONUS_ID
        return NySackLootBox.TYPE if lootbox and lootbox.getType() in NySackLootBox.TYPE else super(NYCelebrityTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        mapping = super(NYCelebrityTokenBonusUIPacker, cls)._getTokenBonusPackers()
        mapping.update({GuestsQuestsTokens.ACTION_TOKEN_PREFIX: cls.__packNYCelebrityActionToken,
         getCoinToken(): cls.__packNYLootboxCoinToken,
         NyATMReward.DOG: cls.__packNYDogUnlockToken,
         NyATMReward.CAT: cls.__packNYCatUnlockToken,
         NyATMReward.MARKETPLACE: cls.__packNYMarketplaceUnlockToken,
         GUEST_ECONOMIC_BONUS_ID: cls.__packNYEconomicToken,
         NySackLootBox.TYPE: None})
        return mapping

    @classmethod
    def _hasUniqueModel(cls, tokenType):
        return True if tokenType in (GuestsQuestsTokens.ACTION_TOKEN_PREFIX,
         getCoinToken(),
         NyATMReward.DOG,
         NyATMReward.CAT,
         NyATMReward.MARKETPLACE,
         GUEST_ECONOMIC_BONUS_ID) else super(NYCelebrityTokenBonusUIPacker, cls)._hasUniqueModel(tokenType)

    @classmethod
    def _getTooltipsPackers(cls):
        mapping = super(NYCelebrityTokenBonusUIPacker, cls)._getTooltipsPackers()
        mapping.update({GuestsQuestsTokens.ACTION_TOKEN_PREFIX: cls.__packNYCelebrityActionToolTipData,
         getCoinToken(): cls.__packNYLootboxCoinToolTipData,
         NyATMReward.DOG: cls.__packEmptyToolTipData,
         NyATMReward.CAT: cls.__packEmptyToolTipData,
         NyATMReward.MARKETPLACE: cls.__packEmptyToolTipData,
         GUEST_ECONOMIC_BONUS_ID: cls.__packEmptyToolTipData,
         NySackLootBox.TYPE: cls.__packEmptyToolTipData})
        return mapping

    @classmethod
    def _getContentId(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, _ in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls._getTokenBonusType(tokenID, complexToken)
            tooltipID = cls.__getTooltipId(tokenType)
            if tooltipID:
                result.append(tooltipID)
            result.extend(super(NYCelebrityTokenBonusUIPacker, cls)._getContentId(bonus))

        return result

    @classmethod
    def __getTooltipId(cls, tokenType):
        if tokenType == getCoinToken():
            return str(R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip())
        elif tokenType in (NyATMReward.DOG, NyATMReward.CAT):
            return str(R.views.lobby.new_year.tooltips.NyGuestTooltip())
        elif tokenType == NyATMReward.MARKETPLACE:
            return str(R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip())
        else:
            return str(R.views.lobby.new_year.tooltips.NyEconomicBonusTooltip()) if tokenType == GUEST_ECONOMIC_BONUS_ID else None

    @classmethod
    def __packNYLootboxCoinToken(cls, bonus, complexToken, token):
        count = bonus.getCount()
        if count < 0:
            return
        else:
            model = GuestRewardItemModel()
            cls._packCommon(bonus, model)
            lootbox = cls._itemsCache.items.tokens.getNyCoins()
            if lootbox is None:
                return
            lootboxType = lootbox.getType()
            label = str(backport.text(R.strings.lootboxes.type.nyCoin()))
            model.setLabel(label)
            model.setIcon(lootboxType)
            model.setValue(str(count))
            model.setTooltipContentId(cls.__getTooltipId(getCoinToken()))
            return model

    @classmethod
    def __packNYCelebrityActionToken(cls, bonus, complexToken, token):
        count = bonus.getCount()
        if count < 0:
            return None
        else:
            model = GuestRewardItemModel()
            cls._packCommon(bonus, model)
            model.setHasNewActivity(not AccountSettings.getUIFlag(NY_GUEST_ACTIVITY_SHOWN))
            model.setIcon(bonus.actionType())
            model.setValue(str(count))
            model.setLabel('{} Label'.format(bonus.actionType()))
            return model

    @classmethod
    def __packUnlockBonusToken(cls, bonus, rewardName):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        label = backport.text(R.strings.ny.quests.bonuses.dyn(rewardName).title())
        model.setLabel(label)
        model.setName(rewardName)
        model.setIcon(rewardName)
        model.setTooltipContentId(cls.__getTooltipId(rewardName))
        return model

    @classmethod
    def __packNYDogUnlockToken(cls, bonus, complexToken, token):
        return cls.__packUnlockBonusToken(bonus, NyATMReward.DOG)

    @classmethod
    def __packNYCatUnlockToken(cls, bonus, complexToken, token):
        return cls.__packUnlockBonusToken(bonus, NyATMReward.CAT)

    @classmethod
    def __packNYMarketplaceUnlockToken(cls, bonus, complexToken, token):
        return cls.__packUnlockBonusToken(bonus, NyATMReward.MARKETPLACE)

    @classmethod
    def __packNYEconomicToken(cls, bonus, complexToken, token):
        model = IconBonusModel()
        label = backport.text(R.strings.ny.quests.bonuses.nyGuestEconomic.title())
        model.setName('addcEconomicBonuses')
        model.setValue(str(bonus.getCount()))
        model.setLabel(label)
        model.setTooltipContentId(cls.__getTooltipId(GUEST_ECONOMIC_BONUS_ID))
        return model

    @classmethod
    def __packNYCelebrityActionToolTipData(cls, complexToken, token, *args):
        _, actionType, level = parseCelebrityTokenActionType(token.id)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NY23_ACTION_TOKEN, specialArgs=(actionType, level))

    @classmethod
    def __packNYLootboxCoinToolTipData(cls, complexToken, token, *args):
        lootbox = cls._itemsCache.items.tokens.getNyCoins()
        return None if lootbox is None else createTooltipData(makeTooltip(header=lootbox.getUserName(), body=backport.text(R.strings.ny.quests.bonuses.nyCoin.body())))

    @classmethod
    def __packEmptyToolTipData(cls, *_):
        return []


class NYToyBonusUIPacker(BaseBonusUIPacker):
    __nyController = dependency.descriptor(INewYearController)

    @classmethod
    def _pack(cls, bonus):
        result = []
        toys = cls.__mergeToys(bonus.getValue())
        for toyId, toysData in toys.iteritems():
            result.append(cls._packSingleBonus(bonus, toyId, toysData['count'], toysData['newCount']))

        return result

    @classmethod
    def __mergeToys(cls, toys):
        result = {}
        for toysData in toys.itervalues():
            newCount = toysData.pop('newCount', 0)
            for toyId, _ in toysData.iteritems():
                if result.get(toyId):
                    result[toyId]['count'] += toysData[toyId]
                    result[toyId]['newCount'] += newCount
                result[toyId] = {'count': toysData[toyId],
                 'newCount': newCount}

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, toyId, count, newCount):
        toyInfo = NewYearCurrentToyInfo(toyId)
        model = NewYearToyIconBonusModel()
        model.setName(bonus.getName())
        model.setValue(str(count))
        model.setIcon(backport.image(toyInfo.getIcon(cls._getImageSize())))
        model.setBigIcon(backport.image(toyInfo.getIcon(cls._getBigImageSize())))
        model.setRankIcon(backport.image(toyInfo.getRankIcon()))
        model.setRankValue(toyInfo.getRank())
        model.setToyID(toyId)
        isNewToy = bool(newCount)
        model.setIsNew(isNewToy)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        result = []
        toys = bonus.getValue()
        for toyId, count in toys.iteritems():
            tooltipData = backport.createTooltipData(tooltip='', specialArgs=(toyId, count))
            result.append(tooltipData)

        return result

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID] * len(bonus.getValue())

    @classmethod
    def _getImageSize(cls):
        return MEDIUM_AWARD_SIZE

    @classmethod
    def _getBigImageSize(cls):
        return LARGE_AWARD_SIZE


class NYToyBonusUIPackerExtra(NYToyBonusUIPacker):

    @classmethod
    def _getImageSize(cls):
        return EPIC_AWARD_SIZE


def getNYCelebityGuestAwardsBonusPacker():
    nyTokenPacker = NYCelebrityTokenBonusUIPacker()
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _NYChallengeCustomizationBonusUIPacker(),
     'tokens': nyTokenPacker,
     'questTokenStory': nyTokenPacker,
     'questTokenAnim': nyTokenPacker,
     'questTokenDecoration': nyTokenPacker,
     'battleToken': nyTokenPacker,
     CurrentNYConstants.TOYS: NYToyBonusUIPacker()})
    return BonusUIPacker(mapping)


def _prepareBonuses(bonuses, packer, bonusCatchers, sortKey):
    zippedBonuses = []
    for bonus in bonuses:
        if not bonus.isShowInGUI():
            continue
        bonusList = packer.pack(bonus)
        bonusTooltipList = packer.getToolTip(bonus)
        bonusContentIdList = packer.getContentId(bonus)
        zippedBonuses.extend(zip(bonusList, bonusTooltipList, bonusContentIdList))
        if bonusCatchers is not None:
            catcher = bonusCatchers.get(bonus.getName())
            if catcher is not None:
                catcher(bonus, bonusList)

    return sorted(zippedBonuses, key=sortKey) if sortKey is not None else zippedBonuses


def packBonusModelAndTooltipData(bonuses, bonusModelsList, packer=None, tooltipsData=None, bonusCatchers=None, sortKey=None):
    bonusesCount = 0
    bonusIndexTotal = 0
    if packer is None:
        mapping = getDefaultBonusPackersMap()
        packer = BonusUIPacker(mapping)
    zippedBonuses = _prepareBonuses(bonuses, packer, bonusCatchers, sortKey)
    for bonusModel, tooltipData, contentId in zippedBonuses:
        bonusModel.setIndex(bonusIndexTotal)
        bonusModelsList.addViewModel(bonusModel)
        bonusesCount += __getBonusCount(bonusModel)
        bonusIndexTotal += 1
        if tooltipsData is not None:
            tooltipIdx = str(len(tooltipsData))
            bonusModel.setTooltipId(tooltipIdx)
            tooltipsData[tooltipIdx] = tooltipData
            bonusModel.setTooltipContentId(str(contentId))

    return bonusesCount


_GUEST_BONUSES_ORDER = ({'getName': 'customizations',
  'getIcon': 'projectionDecal'},
 {'getName': 'customizations',
  'getIcon': 'style'},
 {'getName': 'customizations',
  'getIcon': 'inscription'},
 {'getName': 'premium_plus'},
 {'getName': 'battleToken',
  'getIconName': 'nyCoin'},
 {'getName': 'addcEconomicBonuses'},
 {'getName': 'questTokenAnim'},
 {'getName': 'questTokenStory'},
 {'getName': 'questTokenDecoration'})

def isBonusInOrder(bonus, bonusOrder):
    for criteria in bonusOrder:
        for method, value in criteria.items():
            if hasattr(bonus, method) and value in str(getattr(bonus, method)()):
                return True

    return False


def formatedBonusSortOrder(bonus, bonusOrder):
    for index, criteria in enumerate(bonusOrder):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in str(getattr(bonus, method)()):
                break
        else:
            return index

    return len(bonusOrder)


def guestQuestBonusSortOrder(bonusItems):
    bonus, _ = bonusItems
    return formatedBonusSortOrder(bonus, _GUEST_BONUSES_ORDER)


_CHALLENGE_BONUSES_ORDER = ({'getName': 'variadicDiscount',
  'getLevel': '5'},
 {'getName': 'variadicDiscount',
  'getLevel': '6'},
 {'getName': 'variadicDiscount',
  'getLevel': '7'},
 {'getName': 'variadicDiscount',
  'getLevel': '8'},
 {'getName': 'variadicDiscount',
  'getLevel': '9'},
 {'getName': 'variadicDiscount',
  'getLevel': '10'},
 {'getName': 'customizations',
  'getIcon': 'attachment'},
 {'getName': 'customizations',
  'getIcon': 'inscription'},
 {'getName': 'customizations',
  'getIcon': 'projectionDecal'},
 {'getName': 'customizations',
  'getIcon': 'style'},
 {'getName': 'tmanToken'},
 {'getName': 'dossier_achievement'},
 {'getName': 'items',
  'getOverlayType': 'equipmentModernized_2'},
 {'getName': 'items',
  'getOverlayType': 'equipmentModernized_1'},
 {'getName': 'equipCoin'},
 {'getName': 'battleToken',
  'getIcon': 'nyCoin'},
 {'getName': 'credits'},
 {'getName': 'crystal'},
 {'getName': 'freeXP'})

def challengeQuestBonusSortOrder(bonusItems):
    bonus, _, __ = bonusItems
    return formatedBonusSortOrder(bonus, _CHALLENGE_BONUSES_ORDER)


def getNYCelebrityGuestRewardBonuses(rewards, sortKey=None, excludeTokensChecker=None):
    packer = getNYCelebityGuestAwardsBonusPacker()
    packedBonuses = []
    if rewards:
        bonuses = []
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'tokens' and excludeTokensChecker is not None:
                bonusValue = {k:v for k, v in bonusValue.iteritems() if not excludeTokensChecker(k)}
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        for bonus in bonuses:
            packedBonuses.extend(zip(packer.pack(bonus), packer.getToolTip(bonus)))

    if sortKey is not None:
        packedBonuses = sorted(packedBonuses, key=sortKey)
    return packedBonuses


class _NYCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = RewardsModel()
        cls._packCommon(bonus, model)
        customization = bonus.getC11nItem(item)
        label = customization.userName
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(customization.itemTypeName))
        model.setLabel(label)
        model.setIsReceived(customization.isInInventory)
        return model


class _NYCustomizationCollapsedBonusUIPacker(_NYCustomizationBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        mergedBonuses = cls.__preformat(bonus)
        result = []
        for cItems in mergedBonuses:
            cItem = first(cItems)
            label = getLocalizedBonusName(bonus.getC11nItem(cItem).itemTypeName)
            isReceived = any([ bonus.getC11nItem(cItem).isInInventory for cItem in cItems ])
            model = cls._packSingleBonus(bonus, cItem, label if label else '')
            model.setIsReceived(isReceived)
            mergedLen = len(cItems)
            value = mergedLen if mergedLen > 1 else cItem.get('value', 0)
            model.setValue(str(value))
            result.append(model)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        mergedBonuses = cls.__preformat(bonus)
        tooltipData = []
        for cItems in mergedBonuses:
            needCollapse = len(cItems) > 1
            if needCollapse:
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SHORT_COLLAPSE_CUSTOMIZATION_ITEM_AWARD, specialArgs=[ bonus.getC11nItem(item).intCD for item in cItems ]))
            cItem = first(cItems)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=bonus.getC11nItem(cItem).intCD)))

        return tooltipData

    @staticmethod
    def __preformat(bonus):
        preformated = defaultdict(list)
        for cItem in bonus.getCustomizations():
            if cItem is None:
                continue
            itemTypeID = bonus.getC11nItem(cItem).itemTypeID
            preformated[itemTypeID].append(cItem)

        return preformated.values()


def getNYMarketplaceAwardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _NYCustomizationBonusUIPacker()})
    return BonusUIPacker(mapping)


def getNYMarketplaceAwardsCollapsedBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _NYCustomizationCollapsedBonusUIPacker()})
    return BonusUIPacker(mapping)


def getNYMarketplaceRewardBonuses(bonuses, isMerge=False, sortKey=None):
    packer = getNYMarketplaceAwardsCollapsedBonusPacker() if isMerge else getNYMarketplaceAwardsBonusPacker()
    packedBonuses = []
    for bonus in bonuses:
        packedBonuses.extend(zip(packer.pack(bonus), packer.getToolTip(bonus)))

    if sortKey:
        packedBonuses = sorted(packedBonuses, key=sortKey)
    return packedBonuses


def __getBonusCount(bonusModel):
    bonusName = bonusModel.getName()
    if bonusName in Currency.ALL or bonusName in ('vehicles', 'premiumTank', 'premiumTank_rent', 'style', 'style_3d', 'default', 'guest_cat'):
        return 1
    value = bonusModel.getValue()
    if not value:
        return 1
    if not value.isdigit():
        _logger.error('Failed to get bonus count. Bonus name: %s; value: %s', bonusName, value)
        return 1
    return int(value)
