# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/quest_packer.py
import logging
import typing
from constants import LOOTBOX_TOKEN_PREFIX
from cosmic_event.cosmic_constants import PROGRESSION_TOKEN
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.formatters import parseComplexToken
from gui.shared.missions.packers.bonus import BonusUIPacker, TokenBonusUIPacker, getDefaultBonusPackersMap, BACKPORT_TOOLTIP_CONTENT_ID
from gui.shared.missions.packers.events import DailyQuestUIDataPacker
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import List, Dict, Callable, TypeVar, Optional
    from gui.server_events.formatters import TokenComplex
    from gui.server_events.bonuses import TokensBonus
    TokenBonusType = TypeVar('TokenBonusType', bound=TokensBonus)
_logger = logging.getLogger(__name__)

class CosmicTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID == PROGRESSION_TOKEN:
            return PROGRESSION_TOKEN
        return LOOTBOX_TOKEN_PREFIX if tokenID.startswith(LOOTBOX_TOKEN_PREFIX) else super(CosmicTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        tooltips = super(CosmicTokenBonusUIPacker, cls)._getTooltipsPackers()
        tooltips.update({PROGRESSION_TOKEN: cls.__getCosmicToolTip,
         LOOTBOX_TOKEN_PREFIX: cls.__getLootTooltip})
        return tooltips

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(CosmicTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers.update({PROGRESSION_TOKEN: cls.__packCosmicToken,
         LOOTBOX_TOKEN_PREFIX: cls.__packLootboxToken})
        return packers

    @classmethod
    def _getContentId(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, _ in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls._getTokenBonusType(tokenID, complexToken)
            if tokenType == LOOTBOX_TOKEN_PREFIX:
                result.append(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip())
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __packCosmicToken(cls, model, bonus, *args):
        progressionController = dependency.instance(ICosmicEventProgressionController)
        return None if progressionController.isProgressionFinished() else cls.__packCosmicTokenCommon(model, bonus, 'mars_point')

    @classmethod
    def __packLootboxToken(cls, model, bonus, *args):
        iconName = u'cosmic_2024_2'
        model = cls.__packCosmicTokenCommon(model, bonus, iconName)
        model.setLabel(backport.text(R.strings.quests.bonusName.cosmic_lootbox()))
        return model

    @classmethod
    def __packCosmicTokenCommon(cls, model, bonus, name):
        model.setName(name)
        model.setValue(str(bonus.getCount()))
        return model

    @classmethod
    def __getCosmicToolTip(cls, *_):
        return makeTooltip(header=backport.text(R.strings.cosmicEvent.tooltip.marsPoints.header()), body=backport.text(R.strings.cosmicEvent.tooltip.marsPoints.description()))

    @classmethod
    def __getLootTooltip(cls, complexToken, token):
        if token.id.startswith(LOOTBOX_TOKEN_PREFIX):
            _, lbId = token.id.split(':')
            return lbId
        else:
            return None


def getCosmicBonusPacker():
    mapping = getDefaultBonusPackersMap()
    tokensPacker = CosmicTokenBonusUIPacker()
    mapping.update({'battleToken': tokensPacker})
    return BonusUIPacker(mapping)


class DailyCosmicQuestUIDataPacker(DailyQuestUIDataPacker):

    def __init__(self, quest):
        super(DailyCosmicQuestUIDataPacker, self).__init__(quest, self._getBonusPacker)

    def _getBonusPacker(self):
        return getCosmicBonusPacker()
