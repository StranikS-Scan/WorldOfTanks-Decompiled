# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_award.py
import typing
from battle_pass_common import BATTLE_PASS_SELECT_BONUS_NAME
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.battle_pass.bonuses_layout_controller import BonusesLayoutController
from shared_utils import findFirst
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import BattlePassSelectTokensBonus

def awardsFactory(items, ctx=None):
    bonuses = []
    for key, value in items.iteritems():
        bonuses.extend(getNonQuestBonuses(key, value, ctx))

    return bonuses


class BattlePassAwardsManager(object):
    __bonusesLayoutController = BonusesLayoutController()

    @classmethod
    def init(cls):
        cls.__bonusesLayoutController.init()

    @classmethod
    def composeBonuses(cls, rewards, ctx=None, withSort=True):
        bonuses = []
        for reward in rewards:
            bonuses.extend(awardsFactory(reward, ctx))

        if withSort:
            return cls.sortBonuses(bonuses)
        bonuses = mergeBonuses(bonuses)
        bonuses = splitBonuses(bonuses)
        return bonuses

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

    @classmethod
    def getBigIcon(cls, bonus):
        return cls.__bonusesLayoutController.getBigIcon(bonus)

    @classmethod
    def getPriority(cls, bonus):
        return cls.__bonusesLayoutController.getPriority(bonus)

    @classmethod
    def uniteTokenBonuses(cls, bonuses):
        keys = []
        splitKey = ''
        for bonus in bonuses:
            if bonus.getName() == BATTLE_PASS_SELECT_BONUS_NAME:
                result = {}
                for key, value in bonus.getValue().iteritems():
                    splitKey = key.rsplit(':', 3)[0]
                    newKey = findFirst(lambda x: x.startswith(splitKey), keys, key)
                    result[newKey] = value
                    if newKey not in keys:
                        keys.append(newKey)

                bonus.setValue(result)

        return bonuses

    @classmethod
    def preprocessDogTags(cls, bonuses):
        dogTagEngraving = None
        dogTagBackgroundId = None
        dogTagBackground = None
        dogTagCount = 0
        for bonus in bonuses:
            if bonus.getName() == 'dogTagComponents':
                for background in bonus.getUnlockedBackgrounds():
                    dogTagBackgroundId = background.componentId
                    dogTagBackground = bonus
                    dogTagCount += 1

                engravings = bonus.getUnlockedEngravings()
                if engravings:
                    dogTagEngraving = bonus
                    dogTagCount += len(engravings)
            if dogTagCount > 2:
                return bonuses

        if dogTagBackground is not None and dogTagEngraving is not None:
            result = [ b for b in bonuses if b != dogTagBackground and b != dogTagEngraving ]
            dogTagEngraving.updateContext({'withBackground': dogTagBackgroundId})
            result.append(dogTagEngraving)
            return result
        else:
            return bonuses
