# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_bonus_packer.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_progression_reward_item_view_model import ProgressionState, RewardType
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_helper import getProgressionRewardQuestBonus, getProgressionRewardType
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.bonuses import LootBoxTokensBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker, CrewSkinBonusUIPacker, TokenBonusUIPacker, ItemBonusUIPacker
from helpers import dependency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from skeletons.gui.game_control import IAdventCalendarV2Controller
from skeletons.gui.shared import IItemsCache

def getAdventCalendarV2BonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': AdventCustomizationBonusUIPacker(),
     'battleToken': AdventCalendarTokensPacker(),
     'tmanToken': AdventCalendarTmanTemplateBonusPacker(),
     'crewSkins': AdventCrewSkinBonusUIPacker(),
     'tokens': AdventCalendarTokenBonusUIPacker(),
     'items': AdventCalendarItemBonusUIPacker()})
    return AdventCalendarBonusPacker(mapping)


class AdventCalendarBonusPacker(BonusUIPacker):

    def pack(self, bonus):
        return AdventCalendarLootBoxPacker().pack(bonus) if bonus.getName() == 'battleToken' and isinstance(bonus, LootBoxTokensBonus) else super(AdventCalendarBonusPacker, self).pack(bonus)


class AdventCalendarTokenBonusUIPacker(TokenBonusUIPacker):

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
        tokenBonusPackers = super(AdventCalendarTokenBonusUIPacker, cls)._getTokenBonusPackers()
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


class AdventCrewSkinBonusUIPacker(CrewSkinBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count, label):
        model = super(AdventCrewSkinBonusUIPacker, cls)._packSingleBonus(bonus, crewSkin, count, label)
        model.setIcon(crewSkin.getIconName())
        return model


class AdventCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(AdventCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        item = bonus.getC11nItem(item)
        model.setIcon(item.texture.split('/')[-1].split('.')[0])
        model.setLabel(item.userName)
        return model


class AdventCalendarTmanTemplateBonusPacker(TmanTemplateBonusPacker):
    __adventCalendarV2Ctrl = dependency.descriptor(IAdventCalendarV2Controller)

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(AdventCalendarTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        if model:
            model.setIcon(getRecruitInfo(tokenID).getDynIconName())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        crewMemberToken = cls.__getCrewMemberName()
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_TANKMAN_NOT_RECRUITED, specialArgs=[crewMemberToken,
                 ProgressionState.REWARD_RECEIVED,
                 0,
                 True]))

        return tooltipData

    @classmethod
    def __getCrewMemberName(cls):
        adventQuests = cls.__adventCalendarV2Ctrl.progressionRewardQuestsOrdered
        for idx, quest in enumerate(adventQuests):
            if getProgressionRewardType(quest) == RewardType.CREW_MEMBER:
                return getProgressionRewardQuestBonus(adventQuests[idx])


class AdventCalendarLootBoxPacker(SimpleBonusUIPacker):
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
            model.setTooltipContentId(str(R.views.lobby.advent_calendar.tooltips.AdventCalendarBigLootBoxTooltip()))
            model.setLabel(lootbox.getUserName())
            return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class AdventCalendarTokensPacker(SimpleBonusUIPacker):
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


class AdventCalendarItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(item.getGUIEmblemID())
        model.setLabel(item.userName)
        return model
