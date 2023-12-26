# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/award_notification_base.py
import ast
from gui.shared.utils import flashObject2Dict
from ny_notification import NyNotification
from items.components.ny_constants import NyATMReward
from items.components.crew_books_constants import CREW_BOOK_RARITY
from gui.server_events.bonuses import getSplitBonusFunction, VehiclesBonus, getNonQuestBonuses
from gui.impl.new_year.new_year_helper import ADDITIONAL_BONUS_NAME_GETTERS, BLUEPRINT_NATION_ORDER, CREEBOOK_NATION_ORDER
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
MAX_HUGE_REWARDS = 1
HUGE_BONUSES = ('customizations_style',
 NyATMReward.DOG,
 'tmanToken',
 'vehicles',
 'nyCoin',
 CREW_BOOK_RARITY.PERSONAL,
 CREW_BOOK_RARITY.UNIVERSAL)
BONUSES_ORDER = (NyATMReward.DOG,
 NyATMReward.MARKETPLACE,
 'tmanToken',
 'customizations_style',
 'vehicles',
 'playerBadges',
 'singleAchievements',
 'nyCoin') + CREEBOOK_NATION_ORDER + ('crewBooks', 'booster_credits', 'booster_xp') + BLUEPRINT_NATION_ORDER + ('BlueprintNationFragmentCongrats', 'booster_crew_xp', 'BlueprintUniversalFragmentCongrats', 'tankmen', 'slots')

def bonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return BONUSES_ORDER.index(bonusName) if bonusName in BONUSES_ORDER else len(BONUSES_ORDER)


def splitHugeBonuses(bonuses):
    hugeBonuses = []
    otherBonuses = []
    for bonus in bonuses:
        bonusName = bonus.getName()
        getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
        if getAdditionalName is not None:
            bonusName = getAdditionalName(bonus)
        if bonusName in HUGE_BONUSES:
            hugeBonuses.append(bonus)
        otherBonuses.append(bonus)

    if hugeBonuses:
        hugeBonuses.sort(key=bonusesSortOrder)
        if len(hugeBonuses) > MAX_HUGE_REWARDS:
            otherBonuses.extend(hugeBonuses[MAX_HUGE_REWARDS:])
            hugeBonuses = hugeBonuses[:MAX_HUGE_REWARDS]
    else:
        otherBonuses.sort(key=bonusesSortOrder)
        delimiter = MAX_HUGE_REWARDS if len(otherBonuses) >= MAX_HUGE_REWARDS else len(otherBonuses)
        hugeBonuses.extend(otherBonuses[:delimiter])
        otherBonuses = otherBonuses[delimiter:]
    return (hugeBonuses, otherBonuses)


def customSplitBonuses(bonuses):
    split = []
    for bonus in bonuses:
        splitFunc = getSplitBonusFunction(bonus)
        if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
            split.extend(bonus.getVehiclesCrewBonuses())
            split.append(bonus)
        if splitFunc:
            split.extend(splitFunc(bonus))
        split.append(bonus)

    return split


def fromRawBonusesToBonuses(rawBonuses):
    bonuses = []
    for bonusType, bonusData in rawBonuses.iteritems():
        if bonusType == VehiclesBonus.VEHICLES_BONUS or bonusType == 'items' or bonusType == 'blueprints':
            tempBonusData = {}
            for id, data in bonusData.iteritems():
                tempBonusData[int(id)] = data

            bonuses += getNonQuestBonuses(bonusType, tempBonusData)
        if bonusType == 'dossier':
            tempBonusData = {}
            for id, data in bonusData.iteritems():
                tempDosierBonusData = {}
                for key, item in data.iteritems():
                    tempDosierBonusData[ast.literal_eval(key)] = item

                tempBonusData[int(id)] = tempDosierBonusData

            bonuses += getNonQuestBonuses(bonusType, tempBonusData)
        bonuses += getNonQuestBonuses(bonusType, bonusData)

    return bonuses


def fromRawBonusWithListsToBonuses(rawBonus):
    rawBonusDict = flashObject2Dict(rawBonus)
    for key, value in rawBonusDict.iteritems():
        if isinstance(value, list):
            listOfBonuses = []
            for item in value:
                listOfBonuses.append(flashObject2Dict(item))

            rawBonusDict[key] = listOfBonuses

    return fromRawBonusesToBonuses(rawBonusDict)


class AwardNotificationBase(NyNotification):
    __slots__ = ('_tooltips',)

    def __init__(self, resId, *args, **kwargs):
        super(AwardNotificationBase, self).__init__(resId, *args, **kwargs)
        self._tooltips = {}

    def _fillRewardsList(self, rewardsList, bonuses, sortMethod, packer):
        rewardsList.clear()
        bonuses.sort(key=sortMethod)
        packBonusModelAndTooltipData(bonuses, rewardsList, packer, self._tooltips)

    def _onClick(self):
        pass
