# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/bonus_packers.py
from typing import TYPE_CHECKING, List
from constants import LOOTBOX_TOKEN_PREFIX
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker as BaseTmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.new_year_toy_icon_bonus_model import NewYearToyIconBonusModel
from gui.impl.new_year.new_year_bonus_packer import NYToyBonusUIPacker as BaseNYToyBonusUIPacker
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker as BaseCustomizationBonusUIPacker, CrewSkinBonusUIPacker as BaseCrewSkinBonusUIPacker, TokenBonusUIPacker as BaseTokenBonusUIPacker, ItemBonusUIPacker as BaseItemBonusUIPacker
from helpers import dependency
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus

def getRewardBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': CustomizationBonusUIPacker(),
     'lootBox': LootBoxPacker(),
     'battleToken': TokenBonusUIPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'crewSkins': CrewSkinBonusUIPacker(),
     'tokens': TokenBonusUIPacker(),
     'items': ItemBonusUIPacker(),
     'ny25Toys': NYToyBonusUIPacker()})
    return BonusUIPacker(mapping)


class NYToyBonusUIPacker(BaseNYToyBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, toyId, count, newCount):
        toyInfo = NewYearCurrentToyInfo(toyId)
        model = NewYearToyIconBonusModel()
        model.setName(bonus.getName())
        model.setValue(str(count))
        model.setLabel(backport.text(toyInfo.getName()))
        return model


class TokenBonusUIPacker(BaseTokenBonusUIPacker):
    _NY_GP_TOKEN = 'ny_gp'
    _NY_COIN_TOKEN = 'nyCoin'

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(cls._NY_GP_TOKEN):
            return cls._NY_GP_TOKEN
        return cls._NY_COIN_TOKEN if tokenID.startswith(LOOTBOX_TOKEN_PREFIX) else super(TokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

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
            result.extend(super(TokenBonusUIPacker, cls)._getContentId(bonus))

        return result

    @classmethod
    def __getTooltipId(cls, tokenType):
        return str(R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip()) if tokenType == cls._NY_COIN_TOKEN else None

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(TokenBonusUIPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token,
         cls._NY_GP_TOKEN: cls.__packNYGPToken,
         cls._NY_COIN_TOKEN: cls.__packNYCoinToken})
        return tokenBonusPackers

    @classmethod
    def _getTooltipsPackers(cls):
        defaultPacker = lambda *_: createTooltipData()
        mapping = super(TokenBonusUIPacker, cls)._getTooltipsPackers()
        mapping.update({cls._NY_GP_TOKEN: defaultPacker,
         cls._NY_COIN_TOKEN: defaultPacker})
        return mapping

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(backport.text(R.strings.tooltips.quests.bonuses.token.battle_bonus_x5.header()))
        return model

    @classmethod
    def __packNYGPToken(cls, model, bonus, *_):
        model.setName(cls._NY_GP_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(backport.text(R.strings.quests.bonusName.ny_gp()))
        return model

    @classmethod
    def __packNYCoinToken(cls, model, bonus, *_):
        model.setValue(str(bonus.getCount()))
        model.setIcon(cls._NY_COIN_TOKEN)
        model.setLabel(bonus.getUserName())
        return model


class CrewSkinBonusUIPacker(BaseCrewSkinBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count, label):
        model = super(CrewSkinBonusUIPacker, cls)._packSingleBonus(bonus, crewSkin, count, label)
        model.setIcon(crewSkin.getIconName())
        return model


class CustomizationBonusUIPacker(BaseCustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(CustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        item = bonus.getC11nItem(item)
        model.setIcon(item.texture.split('/')[-1].split('.')[0])
        model.setLabel(item.userName)
        return model


class TmanTemplateBonusPacker(BaseTmanTemplateBonusPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            model = RewardItemModel()
            cls._packCommon(bonus, model)
            model.setIcon(getRecruitInfo(tokenID).getDynIconName())
            model.setLabel(recruitInfo.getFullUserName())
            return model


class LootBoxPacker(SimpleBonusUIPacker):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        lootbox = cls._itemsCache.items.tokens.getLootBoxByTokenID(bonus.getTokens().keys()[0])
        count = bonus.getCount()
        if lootbox is None or count < 0:
            return
        else:
            model = cls._getBonusModel()
            model.setIsCompensation(bonus.isCompensation())
            model.setName(bonus.getName())
            model.setValue(str(count))
            model.setIcon(lootbox.getType())
            return model

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                result.append(str(R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarBigLootBoxTooltip()))

        return result

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class ItemBonusUIPacker(BaseItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(item.getGUIEmblemID())
        model.setLabel(item.userName)
        return model
