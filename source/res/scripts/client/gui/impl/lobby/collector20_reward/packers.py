# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collector20_reward/packers.py
import typing
import logging
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.missions.packers.bonus import BonusUIPacker, DOSSIER_ACHIEVEMENT_POSTFIX, DOSSIER_BADGE_ICON_PREFIX, DOSSIER_BADGE_POSTFIX, DossierBonusUIPacker, getDefaultBonusPackersMap
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
    from gui.server_events.bonuses import DossierBonus
_logger = logging.getLogger(__name__)

class Collector20DossierBonusUIPacker(DossierBonusUIPacker):
    _REWARD_ORDER = ('playerBadges', 'singleAchievements')

    @classmethod
    def _getBadgeTooltip(cls, bonus):
        return [ createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID, badge.isSuffixLayout()]) for badge in cls.__getSortedBadges(bonus) ]

    @classmethod
    def _getToolTip(cls, bonus):
        methodMapping = {'playerBadges': cls._getBadgeTooltip,
         'singleAchievements': cls._getAchievementTooltip}
        return cls.__applyPackMethodsInOrder(bonus, methodMapping)

    @classmethod
    def _pack(cls, bonus):
        methodMapping = {'playerBadges': cls._packBadges,
         'singleAchievements': cls._packAchievements}
        return cls.__applyPackMethodsInOrder(bonus, methodMapping)

    @classmethod
    def _packBadges(cls, bonus):
        result = []
        for badge in cls.__getSortedBadges(bonus):
            dossierIconName = DOSSIER_BADGE_ICON_PREFIX + str(badge.badgeID)
            dossierValue = 0
            if badge.isSuffixLayout():
                template = backport.text(R.strings.awards.collector20.awardNameTemplate.stripe())
            else:
                template = backport.text(R.strings.awards.collector20.awardNameTemplate.badge())
            dossierLabel = template.format(name=badge.getUserName())
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_BADGE_POSTFIX, dossierValue, dossierLabel))

        return result

    @classmethod
    def _packSingleAchievement(cls, achievement, bonus):
        dossierIconName = achievement.getName()
        dossierValue = achievement.getValue()
        template = backport.text(R.strings.awards.collector20.awardNameTemplate.medal())
        dossierLabel = template.format(name=achievement.getUserName())
        return cls._packSingleBonus(bonus, dossierIconName, DOSSIER_ACHIEVEMENT_POSTFIX, dossierValue, dossierLabel)

    @classmethod
    def __applyPackMethodsInOrder(cls, bonus, methodMapping):
        result = []
        for dossierBonusName in cls._REWARD_ORDER:
            method = methodMapping.get(dossierBonusName)
            if method is not None:
                result += method(bonus)
            _logger.warning('Unsupported dossier bonus: %s', dossierBonusName)

        return result

    @staticmethod
    def __getSortedBadges(bonus):
        return sorted(bonus.getBadges(), key=lambda bdg: not bdg.isSuffixLayout())


def getCollector20RewardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'dossier': Collector20DossierBonusUIPacker()})
    return BonusUIPacker(mapping)
