# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/challenges/challenges_award_manager.py
from __future__ import absolute_import
from future.utils import viewitems
from typing import TYPE_CHECKING
from gui.impl.lobby.common.bonuses_layout_config_reader import BonusesLayout
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
if TYPE_CHECKING:
    from typing import Any, Dict, List
    from gui.server_events.bonuses import SimpleBonus
_CONFIG_FILENAME = 'gui/challenges_bonuses_layout.xml'

def awardsFactory(rewards, ctx=None):
    bonuses = []
    for key, value in viewitems(rewards):
        if key == 'vehicles' and isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for vehCD, vehInfo in viewitems(item):
                        bonuses.extend(getNonQuestBonuses(key, {vehCD: vehInfo}, ctx))

        bonuses.extend(getNonQuestBonuses(key, value, ctx))

    return bonuses


class AwardsManager(object):
    __bonusesLayout = BonusesLayout(_CONFIG_FILENAME)

    @classmethod
    def init(cls):
        cls.__bonusesLayout.init()

    @classmethod
    def finalize(cls):
        cls.__bonusesLayout.fini()

    @classmethod
    def composeVisibleBonuses(cls, rewards, ctx=None, reverse=False):
        return list(filter(cls.__bonusesLayout.getIsVisible, cls.composeBonuses(rewards, ctx, reverse=reverse)))

    @classmethod
    def composeBonuses(cls, rewards, ctx=None, reverse=False):
        bonuses = awardsFactory(rewards, ctx)
        return cls.sortMergeBonuses(bonuses, reverse=reverse)

    @classmethod
    def sortMergeBonuses(cls, bonuses, reverse=False):
        bonuses = splitBonuses(mergeBonuses(bonuses))
        return cls.sortBonuses(bonuses, reverse)

    @classmethod
    def sortBonuses(cls, bonuses, reverse=False):
        bonuses.sort(key=cls.__bonusesLayout.getPriority, reverse=reverse)
        return bonuses

    @classmethod
    def sortVisibleBonuses(cls, bonuses, reverse=False):
        return cls.hideInvisible(cls.sortMergeBonuses(bonuses, reverse=reverse))

    @classmethod
    def hideInvisible(cls, bonuses):
        return list(filter(cls.__bonusesLayout.getIsVisible, bonuses))
