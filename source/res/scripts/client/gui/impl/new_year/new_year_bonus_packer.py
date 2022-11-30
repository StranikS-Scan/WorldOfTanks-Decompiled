# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_bonus_packer.py
import logging
from collections import defaultdict
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_GUEST_ACTIVITY_SHOWN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker, BattlePassCustomizationsBonusPacker
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import formatEliteVehicle
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.compensation_bonus_model import CompensationBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel, BonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.vehicle_bonus_model import VehicleBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.guest_reward_item_model import GuestRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.progress_reward_item_model import ProgressRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.vehicle_compensation_model import VehicleCompensationModel
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.rewards_model import RewardsModel
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap, SimpleBonusUIPacker, DossierBonusUIPacker, CustomizationBonusUIPacker, getLocalizedBonusName, VehiclesBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, VEHICLE_RENT_ICON_POSTFIX
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import int2roman
from items.components.ny_constants import TOKEN_VARIADIC_DISCOUNT_PREFIX, Ny23CoinToken, NyATMReward, NYFriendServiceDataTokens
from new_year.ny_constants import GuestsQuestsTokens, parseCelebrityTokenActionType, GUEST_ECONOMIC_BONUS_ID
from new_year.variadic_discount import createDiscountBonusModel
from shared_utils import first
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional, Callable
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus, CustomizationsBonus, TokensBonus
    from gui.server_events.bonuses import VehiclesBonus
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)
VEH_COMP_R_ID = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()

def getNewYearBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NYCelebrityTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'customizations': _NYCelebrityCustomizationBonusUIPacker(),
     'vehicles': NYVehiclesBonusUIPacker(),
     'ny23CoinToken': NYCelebrityTokenBonusUIPacker()})
    return BonusUIPacker(mapping)


def getChallengeBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NYCelebrityTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NYChallengeTmanTemplateBonusPacker(),
     'customizations': _NYChallengeCustomizationBonusUIPacker(),
     'ny23CoinToken': NYCelebrityTokenBonusUIPacker()})
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


class NewYearTmanTemplateBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(NewYearTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        recSourceID = getRecruitInfo(tokenID).getSourceID()
        if recSourceID.startswith('ny22men'):
            model.setIcon(recSourceID)
        tokenRecord = bonus.getTokens()[tokenID]
        if tokenRecord.count > 1:
            model.setValue(str(tokenRecord.count))
        return model


class NYFillersBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NY_FILLERS, specialArgs=[])]


class CompensationBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def packCompensation(cls, bonus):
        return cls._pack(bonus)[0]

    @classmethod
    def _getBonusModel(cls):
        return CompensationBonusModel()


class NYVehicleCompensationBonusUIPacker(CompensationBonusUIPacker):

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
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setName(cls._createUIName(bonus, isRent, vehicle.isPremium))
        model.setIsCompensation(bool(bonus.compensation(vehicle, bonus)))
        cls.__fillVehicle(model, vehicle)
        return model

    @classmethod
    def __fillVehicle(cls, model, vehicle):
        model.setLabel(vehicle.userName)
        model.setVehicleName(vehicle.userName)
        model.setIsElite(vehicle.isElite)
        model.setType(vehicle.type)
        model.setNation(vehicle.nationName)
        model.setVehicleLvl(vehicle.level)
        model.setValue(vehicle.shortUserName)

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
    def _createUIName(cls, bonus, isRent, isPremium):
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


class _NYChallengeCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_NYChallengeCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setIntCD(customization.intCD)
        if customization.itemTypeName == 'inscription' and int(model.getValue()) > 1:
            label = backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.inscriptions())
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
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=bonus.getC11nItem(cItem).intCD, context=bonus.getContext())))

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


class NYChallengeTmanTemplateBonusPacker(NewYearTmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(NYChallengeTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        label = backport.text(R.strings.ny.newYear.celebrityChallenge.rewardScreen.tmanToken(), name=getRecruitInfo(tokenID).getFullUserName())
        model.setLabel(str(label))
        return model


class NYCelebrityTokenBonusUIPacker(NewYearTokenBonusUIPacker):

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID == Ny23CoinToken.ID:
            return Ny23CoinToken.ID
        if tokenID.startswith(GuestsQuestsTokens.ACTION_TOKEN_PREFIX):
            return GuestsQuestsTokens.ACTION_TOKEN_PREFIX
        if tokenID == NyATMReward.DOG_TOKEN:
            return NyATMReward.DOG
        if tokenID == NyATMReward.MARKETPLACE_TOKEN:
            return NyATMReward.MARKETPLACE
        return GUEST_ECONOMIC_BONUS_ID if tokenID in GuestsQuestsTokens.ECONOMIC_GUESTS_TOKENS else super(NYCelebrityTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        mapping = super(NYCelebrityTokenBonusUIPacker, cls)._getTokenBonusPackers()
        mapping.update({GuestsQuestsTokens.ACTION_TOKEN_PREFIX: cls.__packNYCelebrityActionToken,
         Ny23CoinToken.ID: cls.__packNYLootboxCoinToken,
         NyATMReward.DOG: cls.__packNYDogUnlockToken,
         NyATMReward.MARKETPLACE: cls.__packNYMarketplaceUnlockToken,
         GUEST_ECONOMIC_BONUS_ID: cls.__packNYEconomicToken})
        return mapping

    @classmethod
    def _hasUniqueModel(cls, tokenType):
        return True if tokenType in (GuestsQuestsTokens.ACTION_TOKEN_PREFIX,
         Ny23CoinToken.ID,
         NyATMReward.DOG,
         NyATMReward.MARKETPLACE,
         GUEST_ECONOMIC_BONUS_ID) else super(NYCelebrityTokenBonusUIPacker, cls)._hasUniqueModel(tokenType)

    @classmethod
    def _getTooltipsPackers(cls):
        mapping = super(NYCelebrityTokenBonusUIPacker, cls)._getTooltipsPackers()
        mapping.update({GuestsQuestsTokens.ACTION_TOKEN_PREFIX: cls.__packNYCelebrityActionToolTipData,
         Ny23CoinToken.ID: cls.__packNYLootboxCoinToolTipData,
         NyATMReward.DOG: cls.__packEmptyToolTipData,
         NyATMReward.MARKETPLACE: cls.__packEmptyToolTipData,
         GUEST_ECONOMIC_BONUS_ID: cls.__packEmptyToolTipData})
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
        if tokenType == Ny23CoinToken.ID:
            return str(R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip())
        elif tokenType == NyATMReward.DOG:
            return str(R.views.lobby.new_year.tooltips.NyGuestDogTokenTooltip())
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
            label = str(backport.text(R.strings.lootboxes.type.ny23Coin()))
            model.setLabel(label)
            model.setIcon(lootboxType)
            model.setValue(str(count))
            model.setTooltipContentId(cls.__getTooltipId(Ny23CoinToken.ID))
            return model

    @classmethod
    def __packNYCelebrityActionToken(cls, bonus, complexToken, token):
        count = bonus.getCount()
        isGuestCFirstAnim = token.id == NYFriendServiceDataTokens.GUEST_C_QUEST_ANIM_1
        if count < 0 or isGuestCFirstAnim:
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
    def __packNYDogUnlockToken(cls, bonus, complexToken, token):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setName(NyATMReward.DOG)
        model.setLabel(NyATMReward.DOG)
        model.setIcon(NyATMReward.DOG)
        model.setTooltipContentId(cls.__getTooltipId(NyATMReward.DOG))
        return model

    @classmethod
    def __packNYMarketplaceUnlockToken(cls, bonus, complexToken, token):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setName(NyATMReward.MARKETPLACE)
        model.setLabel(NyATMReward.MARKETPLACE)
        model.setIcon(NyATMReward.MARKETPLACE)
        model.setTooltipContentId(cls.__getTooltipId(NyATMReward.MARKETPLACE))
        return model

    @classmethod
    def __packNYEconomicToken(cls, bonus, complexToken, token):
        model = IconBonusModel()
        label = backport.text(R.strings.ny.quests.bonuses.ny23GuestEconomic.title())
        model.setName('addcEconomicBonuses')
        model.setValue(str(bonus.getCount()))
        model.setLabel(label)
        model.setTooltipContentId(cls.__getTooltipId(GUEST_ECONOMIC_BONUS_ID))
        return model

    @classmethod
    def __packNYCelebrityActionToolTipData(cls, tokenId, *args):
        _, actionType, level = parseCelebrityTokenActionType(tokenId)
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NY23_ACTION_TOKEN, specialArgs=(actionType, level))]

    @classmethod
    def __packNYLootboxCoinToolTipData(cls, tokenId, *args):
        lootbox = cls._itemsCache.items.tokens.getNyCoins()
        return None if lootbox is None else createTooltipData(makeTooltip(header=lootbox.getUserName(), body=backport.text(R.strings.ny.quests.bonuses.ny23Coin.body())))

    @classmethod
    def __packEmptyToolTipData(cls, *_):
        return []


def getNYCelebityGuestAwardsBonusPacker():
    nyTokenPacker = NYCelebrityTokenBonusUIPacker()
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _NYChallengeCustomizationBonusUIPacker(),
     'tokens': nyTokenPacker,
     'questTokenStory': nyTokenPacker,
     'questTokenAnim': nyTokenPacker,
     'questTokenDecoration': nyTokenPacker,
     'battleToken': nyTokenPacker})
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
 {'getName': 'premium_plus'},
 {'getName': 'battleToken',
  'getIconName': 'ny23Coin'},
 {'getName': 'addcEconomicBonuses'},
 {'getName': 'questTokenAnim'},
 {'getName': 'questTokenStory'},
 {'getName': 'questTokenDecoration'})

def guestQuestBonusSortOrder(bonus, *args):
    for index, criteria in enumerate(_GUEST_BONUSES_ORDER):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_GUEST_BONUSES_ORDER)


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
    if bonusName in Currency.ALL or bonusName in ('vehicles', 'premiumTank', 'premiumTank_rent', 'style_3d', 'default', 'guest_cat'):
        return 1
    value = bonusModel.getValue()
    if not value:
        return 1
    if not value.isdigit():
        _logger.error('Failed to get bonus count. Bonus name: %s; value: %s', bonusName, value)
        return 1
    return int(value)
