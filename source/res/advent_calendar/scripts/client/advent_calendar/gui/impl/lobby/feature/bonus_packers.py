# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/bonus_packers.py
from __future__ import absolute_import
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker as BaseTmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.bonuses import C11nProgressTokenBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, getDefaultBonusPackersMap, BaseBonusUIPacker, BonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker as BaseCustomizationBonusUIPacker, CrewSkinBonusUIPacker as BaseCrewSkinBonusUIPacker, TokenBonusUIPacker as BaseTokenBonusUIPacker
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

def getRewardBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': CustomizationBonusUIPacker(),
     'lootBox': LootBoxPacker(),
     'battleToken': TokensPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'crewSkins': CrewSkinBonusUIPacker(),
     'tokens': TokenBonusUIPacker(),
     'freeXP': SimpleBonusUIPacker(),
     C11nProgressTokenBonus.BONUS_NAME: ProgressionCustomizationBonusUIPacker()})
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
        model.setLabel(item.userName)
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isQuestsProgression:
            model.setIcon('progressionStyle')
        else:
            model.setIcon('{}_{}'.format(item.itemTypeName, item.id))
        return model


class ProgressionCustomizationBonusUIPacker(BaseBonusUIPacker):
    _c11nService = dependency.descriptor(ICustomizationService)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus, level=None):
        styleID = bonus.getStyleID()
        level = bonus.getProgressLevel()
        style = cls._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon('style_progress_{}_{}'.format(styleID, level))
        model.setValue(style.userName)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        styleID = bonus.getStyleID()
        level = bonus.getProgressLevel()
        style = cls._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=style.intCD, level=level))]

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]


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
            model.setTooltipContentId(BACKPORT_TOOLTIP_CONTENT_ID)
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
