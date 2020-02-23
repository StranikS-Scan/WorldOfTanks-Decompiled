# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_award.py
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.battle_pass.bonuses_layout_controller import BonusesLayoutController

def awardsFactory(items):
    bonuses = []
    for key, value in items.iteritems():
        bonuses.extend(getNonQuestBonuses(key, value))

    return bonuses


class BattlePassAwardsManager(object):
    __bonusesLayoutController = BonusesLayoutController()

    @classmethod
    def init(cls):
        cls.__bonusesLayoutController.init()

    @classmethod
    def composeBonuses(cls, rewards):
        bonuses = []
        for reward in rewards:
            bonuses.extend(awardsFactory(reward))

        return cls.sortBonuses(bonuses)

    @classmethod
    def sortBonuses(cls, bonuses):
        bonuses = mergeBonuses(bonuses)
        bonuses = splitBonuses(bonuses)
        bonuses.sort(key=cls.__bonusesLayoutController.getPriority, reverse=True)
        return bonuses

    @classmethod
    def hideInvisible(cls, bonuses, needSplit=False):
        if needSplit:
            bonuses = mergeBonuses(bonuses)
            bonuses = splitBonuses(bonuses)
        bonuses = list(filter(cls.__bonusesLayoutController.getIsVisible, bonuses))
        return bonuses
