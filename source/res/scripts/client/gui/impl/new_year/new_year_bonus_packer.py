# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_bonus_packer.py
import logging
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker, BattlePassCustomizationsBonusPacker
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap, SimpleBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, DossierBonusUIPacker
from gui.shared.money import Currency
from items.components.ny_constants import VEH_BRANCH_EXTRA_SLOT_TOKEN, CurrentNYConstants, TOKEN_VARIADIC_DISCOUNT_PREFIX
from new_year.ny_constants import NyBonusNames
from new_year.variadic_discount import createDiscountBonusModel
from ny_common.settings import NYVehBranchConsts
from shared_utils import first
if typing.TYPE_CHECKING:
    from typing import List, Dict
    from frameworks.wulf import Array
    from gui.impl.new_year.new_year_bonuses import NYVehicleSlot
    from gui.server_events.bonuses import TokensBonus, SimpleBonus, CustomizationsBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
_logger = logging.getLogger(__name__)

def getNewYearBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NewYearTokenBonusUIPacker(),
     'dossier': NewYearDossierBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'customizations': NewYearCustomizationsBonusPacker(),
     NyBonusNames.ALBUM_ACCESS: SimpleBonusUIPacker(),
     NyBonusNames.VEHICLE_SLOT: NYVehicleSlotBonusPacker(),
     CurrentNYConstants.TOY_FRAGMENTS: NYToyFragmentsBonusPacker(),
     CurrentNYConstants.FILLERS: NYFillersBonusPacker()})
    return BonusUIPacker(mapping)


def getChallengeBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': NewYearTokenBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'customizations': CollapseInscriptionBonusPacker()})
    return BonusUIPacker(mapping)


class NewYearCustomizationsBonusPacker(BattlePassCustomizationsBonusPacker):

    @classmethod
    def _getLabel(cls, custItem):
        wrapper = R.strings.ny.giftSystem.award.label.dyn(custItem.itemTypeName)
        return backport.text(wrapper(), name=custItem.userName) if wrapper.exists() else custItem.userName

    @classmethod
    def _getUserName(cls, custItem):
        wrapper = R.strings.ny.giftSystem.award.label.dyn(custItem.itemTypeName)
        return backport.text(wrapper(), name=custItem.userName) if wrapper.exists() else custItem.userName


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
        if tokenID.startswith(VEH_BRANCH_EXTRA_SLOT_TOKEN):
            return VEH_BRANCH_EXTRA_SLOT_TOKEN
        return TOKEN_VARIADIC_DISCOUNT_PREFIX if tokenID.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX) else super(NewYearTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        mapping = super(NewYearTokenBonusUIPacker, cls)._getTokenBonusPackers()
        mapping.update({VEH_BRANCH_EXTRA_SLOT_TOKEN: cls.__packExtraSlot,
         TOKEN_VARIADIC_DISCOUNT_PREFIX: cls.__packVariadicDiscounts})
        return mapping

    @classmethod
    def _getTooltipsPackers(cls):
        mapping = super(NewYearTokenBonusUIPacker, cls)._getTooltipsPackers()
        mapping.update({VEH_BRANCH_EXTRA_SLOT_TOKEN: cls.__getExtraSlotTooltipData,
         TOKEN_VARIADIC_DISCOUNT_PREFIX: cls.__getVariadicDiscountsTooltipData})
        return mapping

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for tokenID in bonusTokens:
            if tokenID.startswith(VEH_BRANCH_EXTRA_SLOT_TOKEN):
                result.append(R.views.lobby.new_year.tooltips.NyVehicleSlotTooltip())
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __packExtraSlot(cls, model, bonus, complexToken, token):
        model.setName(token.id)
        model.setUserName(backport.text(R.strings.ny.newYear.celebrityChallenge.extraSlot.caption()))
        return model

    @classmethod
    def __packVariadicDiscounts(cls, model, bonus, complexToken, token):
        return createDiscountBonusModel(token)

    @classmethod
    def __getExtraSlotTooltipData(cls, *_):
        return createTooltipData(specialArgs=[NYVehBranchConsts.TOKEN])

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


class NYVehicleSlotBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=False, specialAlias='', specialArgs=[bonus.getSlotType()])]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.new_year.tooltips.NyVehicleSlotTooltip()]


class NYToyFragmentsBonusPacker(SimpleBonusUIPacker):

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
