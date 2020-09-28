# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_award.py
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager

class WTEventLootBoxAwardsManager(BattlePassAwardsManager):
    _SPECIAL_REWARDS = ('customizations', 'crewSkins', 'vehicles')

    @classmethod
    def sortBonuses(cls, bonuses):
        bonuses = super(WTEventLootBoxAwardsManager, cls).sortBonuses(bonuses)
        result = []
        specialRewards = []
        for bonus in bonuses:
            if bonus.getName() in cls._SPECIAL_REWARDS:
                specialRewards.append(bonus)
            result.append(bonus)

        return result + specialRewards
