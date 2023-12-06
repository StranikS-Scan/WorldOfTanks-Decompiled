# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_bonus_packer.py
import logging
import typing
from constants import LOOTBOX_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker, BattlePassCustomizationsBonusPacker
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.new_year.components.vehicles_bonus_model import VehiclesBonusModel, VehicleType
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import EntitlementBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap, SimpleBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, DossierBonusUIPacker, BaseBonusUIPacker, VehiclesBonusUIPacker, CustomizationBonusUIPacker
from gui.shared.money import Currency
from helpers import dependency
from items.components.ny_constants import CurrentNYConstants, TOKEN_VARIADIC_DISCOUNT_PREFIX
from new_year.ny_constants import NY_MARKETPLACE_UNLOCK_ENTITLEMENT
from new_year.variadic_discount import createDiscountBonusModel
from shared_utils import first, findFirst
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Dict
    from frameworks.wulf import Array
    from gui.server_events.bonuses import TokensBonus, SimpleBonus, CustomizationsBonus
_logger = logging.getLogger(__name__)

def getNewYearBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'entitlements': NewYearEntitlementBonusUIPacker(),
     'battleToken': NewYearTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'vehicles': NewYearVehiclesBonusUIPacker(),
     'customizations': NewYearCustomizationsBonusUIPacker(),
     CurrentNYConstants.TOY_FRAGMENTS: NYToyFragmentsBonusPacker(),
     CurrentNYConstants.FILLERS: NYFillersBonusPacker()})
    return BonusUIPacker(mapping)


def getChallengeBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NewYearTokenBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'customizations': CollapseInscriptionBonusPacker()})
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
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX):
            return TOKEN_VARIADIC_DISCOUNT_PREFIX
        return LOOTBOX_TOKEN_PREFIX if tokenID.startswith(LOOTBOX_TOKEN_PREFIX) else super(NewYearTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        mapping = super(NewYearTokenBonusUIPacker, cls)._getTokenBonusPackers()
        mapping.update({TOKEN_VARIADIC_DISCOUNT_PREFIX: cls.__packVariadicDiscounts,
         LOOTBOX_TOKEN_PREFIX: cls.__packLootBox})
        return mapping

    @classmethod
    def _getTooltipsPackers(cls):
        mapping = super(NewYearTokenBonusUIPacker, cls)._getTooltipsPackers()
        mapping.update({TOKEN_VARIADIC_DISCOUNT_PREFIX: cls.__getVariadicDiscountsTooltipData,
         LOOTBOX_TOKEN_PREFIX: cls.__packLootBoxTooltipData})
        return mapping

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for tokenID in bonusTokens:
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX) and R.views.dyn('gui_lootboxes').isValid():
                result.append(R.views.dyn('gui_lootboxes').lobby.gui_lootboxes.tooltips.LootboxTooltip())
            if tokenID.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX):
                result.append(R.views.lobby.new_year.tooltips.NyDiscountRewardTooltip())
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __packVariadicDiscounts(cls, model, bonus, complexToken, token):
        return createDiscountBonusModel(token)

    @classmethod
    def __packLootBox(cls, model, bonus, complexToken, token):
        bonusName = bonus.getName()
        model.setName(bonusName)
        model.setLabel('')
        model.setValue(str(token.count))
        lootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(cls._getTokenID(bonus))
        if lootBox is not None:
            model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(lootBox.getIconName())()))
            model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(lootBox.getIconName())()))
        return model

    @classmethod
    def _getTokenID(cls, bonus):
        return findFirst(None, bonus.getTokens().keys())

    @classmethod
    def __getVariadicDiscountsTooltipData(cls, *_):
        return createTooltipData()

    @classmethod
    def __packLootBoxTooltipData(cls, _, token):
        if R.views.dyn('gui_lootboxes').isValid():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            lootbox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(token.id)
            return createTooltipData(tooltip=LootboxTooltip, specialArgs=(lootbox,))
        return createTooltipData()


class NewYearDossierBonusUIPacker(DossierBonusUIPacker):
    pass


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


class NewYearVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehiclesBonusModel()
        model.setName(cls._createUIName(bonus, isRent))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(cls._getLabel(vehicle))
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setType(VehicleType(vehicle.type))
        model.setNationTag(vehicle.nationName)
        model.setLevel(vehicle.level)
        return model

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentCycle = bonus.getRentCycle(vehInfo)
        rentExpiryTime = cls._getRentExpiryTime(rentDays)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NEW_YEAR_AWARD_VEHICLE, specialArgs=[vehicle.intCD,
         tmanRoleLevel,
         rentExpiryTime,
         rentBattles,
         rentWins,
         rentSeason,
         rentCycle])


class NewYearCustomizationsBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            label = bonus.getC11nItem(item).userName
            result.append(cls._packSingleBonus(bonus, item, label if label else ''))

        return result


class NYToyFragmentsBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = backport.text(R.strings.ny.fragments.name())
        return [cls._packSingleBonus(bonus, label)]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=False, specialAlias='', specialArgs=[str(bonus.getValue())])]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.new_year.tooltips.NyShardsTooltip()]


class NYFillersBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NY_FILLERS, specialArgs=[])]


class NewYearEntitlementBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        entitlementID = bonus.getValue().id
        packer = cls._getEntitlementPackers().get(entitlementID)
        result = []
        if packer:
            result.extend(packer(bonus))
        else:
            _logger.warning('Unknown entitlement %s', entitlementID)
        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        getters = cls._getEntitlementContentIdGetters()
        contentGetter = getters.get(bonus.getValue().id)
        if contentGetter:
            result.append(contentGetter())
        return result

    @classmethod
    def _getToolTip(cls, bonus):
        result = []
        getters = cls._getEntitlementTooltipGetters()
        tooltipGetter = getters.get(bonus.getValue().id)
        if tooltipGetter:
            result.append(tooltipGetter())
        return result

    @classmethod
    def _getEntitlementPackers(cls):
        return {NY_MARKETPLACE_UNLOCK_ENTITLEMENT: cls._packMarketplace}

    @classmethod
    def _getEntitlementContentIdGetters(cls):
        return {NY_MARKETPLACE_UNLOCK_ENTITLEMENT: R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip}

    @classmethod
    def _getEntitlementTooltipGetters(cls):
        return {NY_MARKETPLACE_UNLOCK_ENTITLEMENT: createTooltipData}

    @classmethod
    def _packMarketplace(cls, bonus):
        model = BonusModel()
        entitlementID = bonus.getValue().id
        model.setLabel(EntitlementBonus.getUserName(entitlementID))
        model.setName(entitlementID)
        return [model]


def packBonusModelAndTooltipData(bonuses, bonusModelsList, packer, tooltipsData=None, bonusCatchers=None):
    bonusesCount = 0
    bonusIndexTotal = 0
    for bonus in bonuses:
        if not bonus.isShowInGUI():
            continue
        bonusList = packer.pack(bonus)
        bonusTooltipList = packer.getToolTip(bonus)
        bonusContentIdList = packer.getContentId(bonus)
        for bonusModel, tooltipData, contentId in zip(bonusList, bonusTooltipList, bonusContentIdList):
            bonusModel.setIndex(bonusIndexTotal)
            bonusModelsList.addViewModel(bonusModel)
            bonusesCount += __getBonusCount(bonusModel)
            bonusIndexTotal += 1
            if tooltipsData is not None:
                tooltipIdx = str(len(tooltipsData))
                bonusModel.setTooltipId(tooltipIdx)
                tooltipsData[tooltipIdx] = tooltipData
                bonusModel.setTooltipContentId(str(contentId))

        if bonusCatchers is not None:
            catcher = bonusCatchers.get(bonus.getName())
            if catcher is not None:
                catcher(bonus, bonusList)

    return bonusesCount


def __getBonusCount(bonusModel):
    bonusName = bonusModel.getName()
    if bonusName in Currency.ALL or bonusName == 'vehicles' or bonusName == 'default':
        return 1
    value = bonusModel.getValue()
    if not value:
        return 1
    if not value.isdigit():
        _logger.error('Failed to get bonus count. Bonus name: %s; value: %s', bonusName, value)
        return 1
    return int(value)
