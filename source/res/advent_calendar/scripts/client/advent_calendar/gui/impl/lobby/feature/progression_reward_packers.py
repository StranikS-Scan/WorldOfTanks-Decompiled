# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/progression_reward_packers.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING, List
from advent_calendar.gui.impl.gen.view_models.views.lobby.progression_reward_item_view_model import ProgressionRewardItemViewModel
from advent_calendar.gui.impl.lobby.feature.advent_helper import getProgressionRewardType
from constants import LOOTBOX_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BonusUIPacker, BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
if TYPE_CHECKING:
    from gui.server_events.bonuses import TmanTemplateTokensBonus, CustomizationsBonus, TokensBonus, SimpleBonus
_logger = logging.getLogger(__name__)

def getProgressionBonusPacker():
    mapping = {'customizations': CustomizationPacker(),
     'tmanToken': TmanTemplatePacker(),
     'lootBox': LootboxTokensPacker()}
    return ProgressionBonusUIPacker(mapping)


class ProgressionBonusUIPacker(BonusUIPacker):

    def getCustomToolTip(self, bonus, questID):
        packer = self._getBonusPacker(bonus.getName())
        if packer:
            return packer.getCustomToolTip(bonus, questID)
        _logger.error('Bonus packer for bonus type %s was not implemented yet.', bonus.getName())
        return []


class BaseProgressionRewardPacker(BaseBonusUIPacker):

    @classmethod
    def _createModel(cls, bonus):
        model = ProgressionRewardItemViewModel()
        model.setRewardType(getProgressionRewardType(bonus))
        return model

    @classmethod
    def getCustomToolTip(cls, bonus, questID):
        return cls._getToolTip(bonus)


class TmanTemplatePacker(BaseProgressionRewardPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().keys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._createModel(bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def getCustomToolTip(cls, bonus, questID):
        tooltipData = []
        for tokenID in bonus.getTokens().keys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_TANKMAN_NOT_RECRUITED, specialArgs=[tokenID, questID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().keys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class CustomizationPacker(BaseProgressionRewardPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is not None:
                result.append(cls._createModel(bonus))

        return result

    @classmethod
    def getCustomToolTip(cls, bonus, questID):
        item = first(bonus.getCustomizations())
        itemCustomization = bonus.getC11nItem(item)
        tooltipData = [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_CUSTOMIZATION_ITEM, specialArgs=(questID,) + CustomizationTooltipContext(itemCD=itemCustomization.intCD))]
        return tooltipData


class LootboxTokensPacker(BaseProgressionRewardPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().keys():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                result.append(cls._createModel(bonus))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().keys():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def getCustomToolTip(cls, bonus, questID):
        result = []
        for tokenID in bonus.getTokens().keys():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                result.append(TooltipData())

        return result
