# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/awards_formatters.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import QuestsBonusComposer, AWARDS_SIZES
from gui.shared.formatters import text_styles
from helpers import i18n

class CardAwardComposer(QuestsBonusComposer):
    """
    Awards formatter for mission card in missions view
    """

    def __init__(self, displayedAwardsCount):
        self._displayedAwardsCount = displayedAwardsCount
        super(CardAwardComposer, self).__init__()

    @classmethod
    def getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        bonuses = []
        for bonus in preformattedBonuses:
            shortData = {'name': bonus.userName,
             'label': bonus.getFormattedLabel(),
             'imgSource': bonus.getImage(size)}
            bonuses.append(shortData)

        return bonuses

    def _packBonuses(self, preformattedBonuses, size):
        bonusCount = len(preformattedBonuses)
        mergedBonuses = []
        awardsCount = self._displayedAwardsCount
        if bonusCount > awardsCount:
            sliceIdx = awardsCount - 1
            displayBonuses = preformattedBonuses[:sliceIdx]
            mergedBonuses = preformattedBonuses[sliceIdx:]
        else:
            displayBonuses = preformattedBonuses
        result = []
        for b in displayBonuses:
            result.append(self._packBonus(b, size))

        if mergedBonuses:
            result.append(self._packMergedBonuses(mergedBonuses, size))
        return result

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return {'label': bonus.getFormattedLabel(),
         'imgSource': bonus.getImage(size),
         'tooltip': bonus.tooltip,
         'isSpecial': bonus.isSpecial,
         'specialAlias': bonus.specialAlias,
         'specialArgs': bonus.specialArgs,
         'compensationTooltip': QUESTS.BONUSES_COMPENSATION,
         'hasCompensation': bonus.isCompensation,
         'align': bonus.align,
         'highlightType': bonus.highlightType,
         'overlayType': bonus.overlayType}

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        mergedBonusCount = len(mergedBonuses)
        return {'label': text_styles.stats(i18n.makeString(QUESTS.MISSIONS_AWARDS_MERGED, count=mergedBonusCount)),
         'imgSource': RES_ICONS.getBonusIcon(size, 'default'),
         'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS,
         'specialArgs': self.getShortBonusesData(mergedBonuses, size)}


class DetailedCardAwardComposer(CardAwardComposer):
    """
    Awards formatter for detailed mission card in detailed missions view
    """
    BIG_AWARDS_COUNT = 6

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        size = AWARDS_SIZES.SMALL if len(preformattedBonuses) > self.BIG_AWARDS_COUNT else AWARDS_SIZES.BIG
        return self._packBonuses(preformattedBonuses, size)


class MarathonAwardComposer(CardAwardComposer):
    """
    Awards formatter for marathons header
    """
    AWARDS_PER_LINE_COUNT = 3

    def _packBonuses(self, preformattedBonuses, size):
        bonusCount = len(preformattedBonuses)
        mergedBonuses = []
        if self._displayedAwardsCount > bonusCount > self.AWARDS_PER_LINE_COUNT:
            awardsCount = self.AWARDS_PER_LINE_COUNT
            sliceIdx = awardsCount - 1
            displayBonuses = preformattedBonuses[:sliceIdx]
            mergedBonuses = preformattedBonuses[sliceIdx:]
        elif bonusCount > self.AWARDS_PER_LINE_COUNT and bonusCount > self._displayedAwardsCount:
            awardsCount = self._displayedAwardsCount
            sliceIdx = awardsCount - 1
            displayBonuses = preformattedBonuses[:sliceIdx]
            mergedBonuses = preformattedBonuses[sliceIdx:]
        else:
            displayBonuses = preformattedBonuses
        result = []
        for b in displayBonuses:
            result.append(self._packBonus(b, size))

        if mergedBonuses:
            result.append(self._packMergedBonuses(mergedBonuses, size))
        return result
