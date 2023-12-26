# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_bonuses_packers.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.bonuses import TokensBonus
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, CustomizationBonusUIPacker

class _SeniorityAwardsTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        if bonus.getName() == BATTLE_BONUS_X5_TOKEN:
            model = IconBonusModel()
        else:
            model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(_SeniorityAwardsTokenBonusUIPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token})
        return tokenBonusPackers

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(backport.text(R.strings.tooltips.quests.bonuses.token.battle_bonus_x5.header()))
        return model


class _SeniorityAwardsCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_SeniorityAwardsCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(customization.userName)
        return model


def getSeniorityAwardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _SeniorityAwardsCustomizationBonusUIPacker(),
     'tokens': _SeniorityAwardsTokenBonusUIPacker()})
    return BonusUIPacker(mapping)
