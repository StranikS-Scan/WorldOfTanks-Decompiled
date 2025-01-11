# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_machine/ny_gift_machine_bonuses_helper.py
from constants import PREMIUM_ENTITLEMENTS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import SortedBonusNameQuestsBonusComposer
from gui.impl.auxiliary.rewards_helper import preparationRewardsCurrency, CrewBonusTypes
from gui.server_events.awards_formatters import getNYGiftAwardsPacker, EPIC_AWARD_SIZE
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.money import Currency
_BONUSES_ORDER = (Currency.CREDITS,
 Currency.GOLD,
 Currency.CRYSTAL,
 'customizations',
 'vehicles',
 'slots',
 'tankmen',
 PREMIUM_ENTITLEMENTS.PLUS,
 'freeXP',
 'freeXPFactor',
 'creditsFactor',
 'items',
 'berths',
 'dossier',
 'goodies',
 'tokens',
 'blueprints',
 'crewSkins',
 CrewBonusTypes.CREW_BOOK_BONUSES,
 CrewBonusTypes.CREW_SKIN_BONUSES,
 'finalBlueprints')

def getFormattedGiftBonuses(rewards, exclude=None):
    bonuses = __getGiftBonusesData(rewards, exclude)
    __preformatBonuses(bonuses)
    maxAwardCount = 9
    sortFunction = None
    formatter = SortedBonusNameQuestsBonusComposer(maxAwardCount, sortFunction, getNYGiftAwardsPacker())
    formattedBonuses = formatter.getFormattedBonuses(bonuses, size=EPIC_AWARD_SIZE)
    return formattedBonuses


def __getGiftBonusesData(rewards, exclude):
    preparationRewardsCurrency(rewards)
    bonuses = []
    exclude = exclude or []
    for rewardType, rewardValue in rewards.iteritems():
        if rewardType in exclude:
            continue
        if rewardType == 'vehicles' and isinstance(rewardValue, list):
            for vehicleData in rewardValue:
                bonuses += getNonQuestBonuses(rewardType, vehicleData)

        if rewardType == 'blueprints':
            bonuses += getNonQuestBonuses(rewardType, rewardValue, ctx={'isPacked': True})
        if rewardType == 'slots' and 'vehicles' in rewards:
            continue
        bonuses += getNonQuestBonuses(rewardType, rewardValue)

    return bonuses


def __bonusesOrderKey(bonus):
    name = bonus.getName()
    key = _BONUSES_ORDER.index(name) if name in _BONUSES_ORDER else len(_BONUSES_ORDER)
    return key


def __preformatBonuses(bonuses):
    bonuses.sort(key=__bonusesOrderKey)
