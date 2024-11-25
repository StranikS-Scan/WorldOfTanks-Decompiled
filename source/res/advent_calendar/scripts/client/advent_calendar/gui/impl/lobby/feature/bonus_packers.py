# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/bonus_packers.py
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker as BaseTmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker as BaseCustomizationBonusUIPacker, CrewSkinBonusUIPacker as BaseCrewSkinBonusUIPacker, TokenBonusUIPacker as BaseTokenBonusUIPacker, ItemBonusUIPacker as BaseItemBonusUIPacker
from helpers import dependency
from skeletons.gui.shared import IItemsCache

def getRewardBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': CustomizationBonusUIPacker(),
     'lootBox': LootBoxPacker(),
     'battleToken': TokensPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'crewSkins': CrewSkinBonusUIPacker(),
     'tokens': TokenBonusUIPacker(),
     'items': ItemBonusUIPacker()})
    return BonusUIPacker(mapping)


class TokenBonusUIPacker(BaseTokenBonusUIPacker):

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        if bonus.getName() == BATTLE_BONUS_X5_TOKEN:
            model = cls._getBonusModel()
        else:
            model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(TokenBonusUIPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token})
        return tokenBonusPackers

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(backport.text(R.strings.tooltips.quests.bonuses.token.battle_bonus_x5.header()))
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
            model.setTooltipContentId(str(R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarBigLootBoxTooltip()))
            return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class TokensPacker(SimpleBonusUIPacker):
    _IMAGE_NAME = 'nyCoin'

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        count = bonus.getCount()
        if count < 0:
            return None
        else:
            model = cls._getBonusModel()
            cls._packCommon(bonus, model)
            model.setValue(str(count))
            model.setIcon(cls._IMAGE_NAME)
            model.setTooltipContentId(str(R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip()))
            model.setLabel(bonus.getUserName())
            return model

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
