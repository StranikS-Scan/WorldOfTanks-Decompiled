# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/awards_formatters.py
from constants import PERSONAL_QUEST_FREE_TOKEN_NAME
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import finders
from gui.server_events.awards_formatters import QuestsBonusComposer, AWARDS_SIZES, PreformattedBonus, getPersonalMissionAwardPacker, getOperationPacker, formatCountLabel, LABEL_ALIGN
from gui.server_events.bonuses import FreeTokensBonus
from gui.shared.formatters import text_styles
from helpers import i18n, dependency
from skeletons.gui.server_events import IEventsCache
_OPERATION_AWARDS_COUNT = 3

class CurtailingAwardsComposer(QuestsBonusComposer):
    """
    Awards formatter which curtails formatted bonuses to count given in displayedAwardsCount.
    If there is more bonuses then specified they are wrapped in 'box' VO and listed in its tooltip
    """

    def __init__(self, displayedAwardsCount, awardsFormatter=None):
        self._displayedAwardsCount = displayedAwardsCount
        super(CurtailingAwardsComposer, self).__init__(awardsFormatter)

    def getShortBonusesData(self, bonuses):
        return self._getShortBonusesData(self.getPreformattedBonuses(bonuses))

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
         'specialArgs': self._getShortBonusesData(mergedBonuses, size)}

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        bonuses = []
        for bonus in preformattedBonuses:
            shortData = {'name': bonus.userName,
             'label': bonus.getFormattedLabel(),
             'imgSource': bonus.getImage(size)}
            bonuses.append(shortData)

        return bonuses


class DetailedCardAwardComposer(CurtailingAwardsComposer):
    """
    Awards formatter for detailed mission card in detailed missions view
    """

    def getFormattedBonuses(self, bonuses, bigAwardsCount=6):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        size = AWARDS_SIZES.SMALL if len(preformattedBonuses) > bigAwardsCount else AWARDS_SIZES.BIG
        return self._packBonuses(preformattedBonuses, size)


class PersonalMissionsAwardComposer(CurtailingAwardsComposer):
    """
    Awards formatter for personal mission bonuses.
    May display specific reward sheet and free reward sheets bonuses.
    Slots and berths are not shown in this formatter. UX requirement.
    """

    def __init__(self, displayedAwardsCount):
        self._displayedAwardsCount = displayedAwardsCount
        super(PersonalMissionsAwardComposer, self).__init__(displayedAwardsCount, getPersonalMissionAwardPacker())

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, gap=0, isObtained=False, areTokensPawned=False, pawnCost=0, obtainedImage='', obtainedImageOffset=0):
        if areTokensPawned:
            newBonuses = []
            context = {'pawnCost': pawnCost,
             'areTokensPawned': True}
            hasFreeTokens = False
            for bonus in bonuses:
                if bonus.getName() == 'freeTokens':
                    value = {PERSONAL_QUEST_FREE_TOKEN_NAME: {'count': bonus.getCount() + pawnCost}}
                    newBonuses.append(FreeTokensBonus(value, ctx=context))
                    hasFreeTokens = True
                newBonuses.append(bonus)

            if not hasFreeTokens:
                value = {PERSONAL_QUEST_FREE_TOKEN_NAME: {'count': pawnCost}}
                newBonuses.append(FreeTokensBonus(value, ctx=context))
            bonuses = newBonuses
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(preformattedBonuses, size, gap, isObtained, obtainedImage, obtainedImageOffset)

    def _packBonuses(self, preformattedBonuses, size, gap=0, isObtained=False, obtainedImage='', obtainedImageOffset=0):
        result = []
        for b in preformattedBonuses:
            result.append(self._packBonus(b, size, gap, isObtained, obtainedImage, obtainedImageOffset))

        return result

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL, gap=0, isObtained=False, obtainedImage='', obtainedImageOffset=0):
        data = super(PersonalMissionsAwardComposer, self)._packBonus(bonus, size=size)
        data.update(gap=gap)
        data.update(isObtained=isObtained)
        data.update(obtainedImage=obtainedImage)
        data.update(obtainedImageOffset=obtainedImageOffset)
        data.update(areTokensPawned=bonus.areTokensPawned)
        data.update(tokensPawnedImage=RES_ICONS.MAPS_ICONS_LIBRARY_LOCKINDICATOR if bonus.areTokensPawned else '')
        return data


def _getTankwomansCountInOperation(operation):
    total = 0
    current = 0
    for quest in operation.getFinalQuests().itervalues():
        tankmen = quest.getBonuses('tankmen')
        if tankmen:
            total += 1
            if quest.isCompleted():
                current += 1

    return (current, total)


class MainOperationAwardComposer(PersonalMissionsAwardComposer):
    """
    Awards formatter for operation bonuses.
    """
    _eventsCache = dependency.descriptor(IEventsCache)
    _TANKWOMAN_BONUS = 'tankwoman'

    def __init__(self):
        super(PersonalMissionsAwardComposer, self).__init__(_OPERATION_AWARDS_COUNT, getOperationPacker())

    def getFormattedBonuses(self, operation, size=AWARDS_SIZES.BIG, gap=0):
        bonuses = self._getBonuses(operation)
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        tankwomanBonus = self._getPreformattedTankwomanBonus(operation)
        if tankwomanBonus:
            preformattedBonuses.append(tankwomanBonus)
        return self._packBonuses(preformattedBonuses, size, gap)

    def _getBonuses(self, operation):
        hiddenQuests = self._eventsCache.getHiddenQuests()
        finder = finders.getQuestByTokenAndBonus
        extrasQuest = finder(hiddenQuests, finders.mainQuestTokenFinder(operation.getID()))
        baseQuest = finder(hiddenQuests, finders.tokenFinder(finders.PERSONAL_MISSION_TOKEN % operation.getID()))
        bonuses = baseQuest.getBonuses('dossier')
        bonuses.extend(extrasQuest.getBonuses())
        return bonuses

    def _getPreformattedTankwomanBonus(self, operation):
        _, total = _getTankwomansCountInOperation(operation)
        return PreformattedBonus(bonusName=self._TANKWOMAN_BONUS, label=formatCountLabel(total), images=dict(map(lambda size: (size, RES_ICONS.getBonusIcon(size, self._TANKWOMAN_BONUS)), AWARDS_SIZES.ALL())), labelFormatter=text_styles.stats, align=LABEL_ALIGN.RIGHT, specialAlias=TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_TANKWOMAN, isSpecial=True, specialArgs=[]) if total else None


class AddOperationAwardComposer(PersonalMissionsAwardComposer):
    """
    Awards formatter for operation bonuses.
    """
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(PersonalMissionsAwardComposer, self).__init__(_OPERATION_AWARDS_COUNT, getOperationPacker())

    def getFormattedBonuses(self, operation, size=AWARDS_SIZES.BIG, gap=0):
        bonuses = self._getBonuses(operation)
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(preformattedBonuses, size, gap)

    def _getBonuses(self, operation):
        hiddenQuests = self._eventsCache.getHiddenQuests()
        finder = finders.getQuestByTokenAndBonus
        baseQuest = finder(hiddenQuests, finders.addQuestTokenFinder(operation.getID()))
        bonuses = baseQuest.getBonuses()
        if not operation.getNextOperationID():
            topBageQuest = finder(hiddenQuests, finders.tokenFinder(finders.PERSONAL_MISSION_BADGES_TOKEN))
            bonuses.extend(topBageQuest.getBonuses())
        return bonuses


class TooltipOperationAwardComposer(MainOperationAwardComposer):
    """
    Awards formatter for operation tooltip bonuses.
    """
    _BONUSES_ORDER = ('vehicles', 'tankwoman', 'customizations', 'dossier')

    def _getKeySortOrder(self, key):
        return self._BONUSES_ORDER.index(key) if key in self._BONUSES_ORDER else -1

    def _sortFunc(self, b1, b2):
        return cmp(self._getKeySortOrder(b1.bonusName), self._getKeySortOrder(b2.bonusName))

    def _packBonuses(self, preformattedBonuses, size, gap=0, isObtained=False, obtainedImage='', obtainedImageOffset=0):
        result = []
        for b in sorted(preformattedBonuses, cmp=self._sortFunc):
            result.append(self._packBonus(b, size, gap, isObtained, obtainedImage, obtainedImageOffset))

        return result

    def _getBonuses(self, operation):
        bonusList = []
        if not operation.isAwardAchieved():
            for tID, bonuses in operation.getBonuses().iteritems():
                bonusList.extend(bonuses)

        else:
            hiddenQuests = self._eventsCache.getHiddenQuests()
            finder = finders.getQuestByTokenAndBonus
            if not operation.isFullCompleted():
                extrasQuest = finder(hiddenQuests, finders.addQuestTokenFinder(operation.getID()))
                bonusList.extend(extrasQuest.getBonuses())
        return bonusList

    def _getPreformattedTankwomanBonus(self, operation):
        if not operation.isFullCompleted():
            current, total = _getTankwomansCountInOperation(operation)
            currentStr = text_styles.success(current) if current else text_styles.stats(current)
            images = dict(map(lambda size: (size, RES_ICONS.getBonusIcon(size, 'tankwoman')), AWARDS_SIZES.ALL()))
            return PreformattedBonus(bonusName=self._TANKWOMAN_BONUS, label='%s / %s' % (currentStr, str(total)), images=images, labelFormatter=text_styles.main)
        else:
            return None


class MarathonAwardComposer(CurtailingAwardsComposer):
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
