# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_bonus_packer.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPackersMap, TmanTemplateBonusPacker, BattlePassCustomizationsBonusPacker
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, BonusUIPacker
from items import new_year
from items.components.ny_constants import VEH_BRANCH_EXTRA_SLOT_TOKEN
from new_year.variadic_discount import createDiscountBonusModel
from gui.impl import backport
from gui.impl.gen import R
from shared_utils import first

def getNewYearBonusPacker():
    mapping = getBattlePassBonusPackersMap()
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

    @classmethod
    def _pack(cls, bonus):
        result = super(NewYearTokenBonusUIPacker, cls)._pack(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if tokenID == VEH_BRANCH_EXTRA_SLOT_TOKEN:
                result.append(cls._packExtraSlot(token))
            if tokenID in new_year.g_cache.variadicDiscounts:
                result.append(cls._packVariadicDiscounts(token))

        return result

    @classmethod
    def _packExtraSlot(cls, token):
        model = TokenBonusModel()
        model.setValue(str(token.count))
        model.setName(token.id)
        model.setUserName(backport.text(R.strings.ny.newYear.celebrityChallenge.extraSlot.caption()))
        return model

    @classmethod
    def _packVariadicDiscounts(cls, token):
        return createDiscountBonusModel(token)

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(NewYearTokenBonusUIPacker, cls)._getToolTip(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, _ in bonusTokens.iteritems():
            if tokenID == VEH_BRANCH_EXTRA_SLOT_TOKEN or tokenID in new_year.g_cache.variadicDiscounts:
                result.append(None)

        return result


class NewYearTmanTemplateBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(NewYearTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo.getSourceID() == 'ny21men':
            model.setIcon('commanderChuck')
        tokenRecord = bonus.getTokens()[tokenID]
        if tokenRecord.count > 1:
            model.setValue(str(tokenRecord.count))
        return model
