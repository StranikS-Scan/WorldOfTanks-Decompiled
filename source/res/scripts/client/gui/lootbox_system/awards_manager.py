# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/awards_manager.py
from typing import TYPE_CHECKING
from gui.lootbox_system.bonuses_layout import BonusesLayout
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
if TYPE_CHECKING:
    from typing import Any, Dict, List
    from gui.server_events.bonuses import SimpleBonus

def awardsFactory(items, ctx=None):
    bonuses = []
    for key, value in items.iteritems():
        bonuses.extend(getNonQuestBonuses(key, value, ctx))

    return bonuses


class AwardsManager(object):
    __bonusesLayout = BonusesLayout()

    @classmethod
    def init(cls):
        cls.__bonusesLayout.init()

    @classmethod
    def finalize(cls):
        cls.__bonusesLayout.fini()

    @classmethod
    def composeBonuses(cls, rewards, ctx=None):
        bonuses = []
        for reward in rewards:
            bonuses.extend(awardsFactory(reward, ctx))

        return cls.sortMergeBonuses(bonuses)

    @classmethod
    def sortMergeBonuses(cls, bonuses, reverse=False):
        bonuses = splitBonuses(mergeBonuses(bonuses))
        return cls.sortBonuses(bonuses, reverse)

    @classmethod
    def sortBonuses(cls, bonuses, reverse=False):
        bonuses.sort(key=cls.__bonusesLayout.getPriority, reverse=reverse)
        return bonuses

    @classmethod
    def getRarity(cls, bonus):
        return cls.__bonusesLayout.getRarity(bonus)

    @classmethod
    def getIsVisible(cls, bonus):
        return cls.__bonusesLayout.getIsVisible(bonus)
