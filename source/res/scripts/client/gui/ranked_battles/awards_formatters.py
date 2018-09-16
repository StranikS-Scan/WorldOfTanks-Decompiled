# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/awards_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.money import Currency
_AWARDS_ORDER = ['items',
 Currency.CREDITS,
 'premium',
 Currency.GOLD,
 Currency.CRYSTAL,
 'oneof']
_MAX_VISIBLE_AWARDS = 6
_awardsFormatter = CurtailingAwardsComposer(_MAX_VISIBLE_AWARDS)

def getRankedQuestsOrderedAwards(quests, size=AWARDS_SIZES.SMALL):
    bonuses = []
    for quest in quests:
        questBonuses = quest.getBonuses()
        formattedBonuses = sorted(questBonuses, cmp=_sortBonusesFunc, reverse=True)
        bonuses.extend(formattedBonuses)

    awards = _awardsFormatter.getFormattedBonuses(bonuses, size=size)
    return awards


def _getOrderByBonusType(bonusName):
    return _AWARDS_ORDER.index(bonusName) if bonusName in _AWARDS_ORDER else -1


def _sortBonusesFunc(b1, b2):
    return cmp(_getOrderByBonusType(b1.getName()), _getOrderByBonusType(b2.getName()))
