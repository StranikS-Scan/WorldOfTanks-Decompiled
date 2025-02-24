# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/base/awards_manager.py
from typing import TYPE_CHECKING
from gui.lootbox_system.base.bonuses_layout import BonusesLayout
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
    def composeBonuses(cls, eventName, rewards, ctx=None):
        bonuses = []
        for reward in rewards:
            bonuses.extend(awardsFactory(reward, ctx))

        return cls.sortMergeBonuses(eventName, bonuses)

    @classmethod
    def sortMergeBonuses(cls, eventName, bonuses, reverse=False):
        bonuses = splitBonuses(mergeBonuses(bonuses))
        return cls.sortBonuses(eventName, bonuses, reverse)

    @classmethod
    def sortBonuses(cls, eventName, bonuses, reverse=False):
        bonuses.sort(key=lambda bonus: cls.__bonusesLayout.getPriority(eventName, bonus), reverse=reverse)
        return bonuses

    @classmethod
    def getRarity(cls, eventName, bonus):
        return cls.__bonusesLayout.getRarity(eventName, bonus)

    @classmethod
    def getIsVisible(cls, eventName, bonus):
        return cls.__bonusesLayout.getIsVisible(eventName, bonus)
