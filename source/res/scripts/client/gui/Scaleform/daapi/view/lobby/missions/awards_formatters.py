# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/awards_formatters.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import finders
from gui.server_events.awards_formatters import QuestsBonusComposer, AWARDS_SIZES, PreformattedBonus, getPersonalMissionAwardPacker, getOperationPacker, getBattlePassAwardsPacker, formatCountLabel, LABEL_ALIGN, getLinkedSetAwardPacker, PACK_RENT_VEHICLES_BONUS, PostProcessTags
from gui.server_events.bonuses import FreeTokensBonus
from gui.shared.formatters import text_styles
from helpers import i18n, dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_OPERATION_AWARDS_COUNT = 3

class CurtailingAwardsComposer(QuestsBonusComposer):

    def __init__(self, displayedAwardsCount, awardsFormatter=None):
        self._displayedRewardsCount = displayedAwardsCount
        super(CurtailingAwardsComposer, self).__init__(awardsFormatter)

    def getShortBonusesData(self, bonuses):
        return self._getShortBonusesData(self.getPreformattedBonuses(bonuses))

    def _packBonuses(self, preformattedBonuses, size):
        bonusCount = len(preformattedBonuses)
        mergedBonuses = []
        if bonusCount > self._displayedRewardsCount:
            sliceIdx = self._displayedRewardsCount - 1
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
        compensationReason = None
        if bonus.compensationReason is not None:
            compensationReason = self._packBonus(bonus.compensationReason, size)
        return {'label': bonus.getFormattedLabel(),
         'imgSource': bonus.getImage(size),
         'tooltip': bonus.tooltip,
         'isSpecial': bonus.isSpecial,
         'specialAlias': bonus.specialAlias,
         'specialArgs': bonus.specialArgs,
         'hasCompensation': bonus.isCompensation,
         'hasAnimation': False,
         'compensationReason': compensationReason,
         'align': bonus.align,
         'highlightType': bonus.getHighlightType(size),
         'overlayType': bonus.getOverlayType(size),
         'highlightIcon': bonus.getHighlightIcon(size),
         'overlayIcon': bonus.getOverlayIcon(size),
         'isWulfTooltip': bonus.isWulfTooltip}

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
             'imgSource': bonus.getImage(size),
             'highlightIcon': bonus.getHighlightIcon(size),
             'overlayIcon': bonus.getOverlayIcon(size)}
            bonuses.append(shortData)

        return bonuses


class BattlePassAwardsComposer(CurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount=1, awardsFormatter=None):
        formatter = awardsFormatter or getBattlePassAwardsPacker()
        super(BattlePassAwardsComposer, self).__init__(displayedAwardsCount, formatter)

    def setDisplayedCount(self, count):
        self._displayedRewardsCount = count

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        blueprints = True
        for bonus in mergedBonuses:
            if bonus.postProcessTags != 'blueprints':
                blueprints = False

        if blueprints:
            return {'label': '',
             'imgSource': RES_ICONS.getBonusIcon(size, 'blueprint_tube'),
             'isSpecial': True,
             'specialAlias': TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS,
             'specialArgs': self._getShortBonusesData(mergedBonuses, size)}
        label = ''
        if self._displayedRewardsCount > 1:
            label = text_styles.stats(i18n.makeString(QUESTS.MISSIONS_AWARDS_MERGED, count=len(mergedBonuses)))
        return {'label': label,
         'imgSource': RES_ICONS.getBonusIcon(size, 'default'),
         'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS,
         'specialArgs': self._getShortBonusesData(mergedBonuses, size)}


class RawLabelBonusComposer(QuestsBonusComposer):
    __slots__ = ()

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        res = super(RawLabelBonusComposer, self)._packBonus(bonus, size)
        res.update({'label': bonus.label})
        return res


class AwardsWindowComposer(CurtailingAwardsComposer):

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        bonuses = []
        for bonus in preformattedBonuses:
            shortData = {'name': bonus.userName,
             'label': bonus.getFormattedLabel(),
             'imgSource': bonus.getImage(AWARDS_SIZES.SMALL)}
            bonuses.append(shortData)

        return bonuses


class LinkedSetAwardsComposer(CurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount, awardsFormatter=None):
        if awardsFormatter is None:
            awardsFormatter = getLinkedSetAwardPacker()
        super(LinkedSetAwardsComposer, self).__init__(displayedAwardsCount, awardsFormatter)
        return

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return {'label': bonus.label,
         'imgSource': bonus.getImage(size),
         'tooltip': bonus.tooltip,
         'isSpecial': bonus.isSpecial,
         'specialAlias': bonus.specialAlias,
         'specialArgs': bonus.specialArgs,
         'hasCompensation': bonus.isCompensation,
         'align': bonus.align,
         'highlightType': bonus.getHighlightType(size),
         'overlayType': bonus.getOverlayType(size)}


class DetailedCardAwardComposer(CurtailingAwardsComposer):

    def getFormattedBonuses(self, bonuses, bigAwardsCount=6):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        size = AWARDS_SIZES.SMALL if len(preformattedBonuses) > bigAwardsCount else AWARDS_SIZES.BIG
        return self._packBonuses(preformattedBonuses, size)


class PackRentVehiclesAwardComposer(CurtailingAwardsComposer):

    def _packBonuses(self, preformattedBonuses, size):
        bonusCount = len(preformattedBonuses)
        mergedBonuses = []
        packRentVehicles = None
        for index, bonus in enumerate(preformattedBonuses):
            if bonus.bonusName == PACK_RENT_VEHICLES_BONUS:
                packRentVehicles = preformattedBonuses.pop(index)
                break

        awardsCount = self._displayedRewardsCount
        if packRentVehicles:
            awardsCount -= 1
        if bonusCount > awardsCount:
            sliceIdx = awardsCount - 1
            displayBonuses = preformattedBonuses[:sliceIdx]
            mergedBonuses = preformattedBonuses[sliceIdx:]
        else:
            displayBonuses = preformattedBonuses
        result = []
        for b in displayBonuses:
            result.append(self._packBonus(b, size))

        if packRentVehicles:
            result.append(self._packBonus(packRentVehicles, size))
        if mergedBonuses:
            result.append(self._packMergedBonuses(mergedBonuses, size))
        return result


class BonusNameQuestsBonusComposer(PackRentVehiclesAwardComposer):

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        packBonus = super(BonusNameQuestsBonusComposer, self)._packBonus(bonus, size)
        packBonus['bonusName'] = bonus.bonusName
        return packBonus


class LootBoxBonusComposer(BonusNameQuestsBonusComposer):

    def getVisibleFormattedBonuses(self, bonuses, alwaysVisibleBonuses, size=AWARDS_SIZES.SMALL, sortKey=None):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        alwaysPreformatedBonuses = self.getPreformattedBonuses(alwaysVisibleBonuses)
        alwaysVisibleCount = len(alwaysPreformatedBonuses)
        if alwaysVisibleCount:
            totalCount = alwaysVisibleCount + len(preformattedBonuses)
            if totalCount > self._displayedRewardsCount:
                insertPos = self._displayedRewardsCount - alwaysVisibleCount - 1
                if insertPos < 0:
                    insertPos = 0
                preformattedBonuses[insertPos:insertPos] = alwaysPreformatedBonuses
            else:
                preformattedBonuses.extend(alwaysPreformatedBonuses)
        if sortKey is not None:
            preformattedBonuses = sorted(preformattedBonuses, key=sortKey)
        return self._packBonuses(preformattedBonuses, size)


class NewStyleBonusComposer(LootBoxBonusComposer):
    pass


def _getBonusesWithModifyTokens(bonuses, freeTokenName, addTokensCount, hasPawned):
    if addTokensCount > 0:
        newBonuses = []
        hasFreeTokens = False
        ctx = {}
        for bonus in bonuses:
            ctx = bonus.getContext()
            if bonus.getName() == 'freeTokens':
                value = {freeTokenName: {'count': bonus.getCount() + addTokensCount}}
                newBonuses.append(FreeTokensBonus(value, ctx=ctx, hasPawned=hasPawned))
                hasFreeTokens = True
            newBonuses.append(bonus)

        if not hasFreeTokens:
            value = {freeTokenName: {'count': addTokensCount}}
            newBonuses.append(FreeTokensBonus(value, ctx=ctx, hasPawned=hasPawned))
        bonuses = newBonuses
    return bonuses


class PersonalMissionsAwardComposer(CurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount, packer=None):
        self._displayedAwardsCount = displayedAwardsCount
        super(PersonalMissionsAwardComposer, self).__init__(displayedAwardsCount, packer or getPersonalMissionAwardPacker())

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, gap=0, isObtained=False, obtainedImage='', obtainedImageOffset=0):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(preformattedBonuses, size, gap, isObtained, obtainedImage, obtainedImageOffset)

    def getPawnedQuestBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, gap=0, isObtained=False, pawnedTokensCount=0, obtainedImage='', obtainedImageOffset=0, freeTokenName=''):
        bonuses = _getBonusesWithModifyTokens(bonuses, freeTokenName, pawnedTokensCount, True)
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(preformattedBonuses, size, gap, isObtained, obtainedImage, obtainedImageOffset)

    def getReturnTokensQuestBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, gap=0, isObtained=False, returnedTokensCount=0, obtainedImage='', obtainedImageOffset=0, freeTokenName=''):
        bonuses = _getBonusesWithModifyTokens(bonuses, freeTokenName, returnedTokensCount, False)
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
        ctx = {'branch': operation.getBranch()}
        hiddenQuests = self._eventsCache.getHiddenQuests()
        finder = finders.getQuestByTokenAndBonus
        extrasQuest = finder(hiddenQuests, finders.mainQuestTokenFinder(operation))
        baseQuest = finder(hiddenQuests, finders.tokenFinder(finders.PERSONAL_MISSION_TOKEN % (operation.getCampaignID(), operation.getID())))
        bonuses = baseQuest.getBonuses('dossier', ctx=ctx)
        bonuses.extend(extrasQuest.getBonuses(ctx=ctx))
        return bonuses

    def _getPreformattedTankwomanBonus(self, operation):
        _, total = _getTankwomansCountInOperation(operation)
        return PreformattedBonus(bonusName=self._TANKWOMAN_BONUS, label=formatCountLabel(total), images=dict(((size, RES_ICONS.getBonusIcon(size, self._TANKWOMAN_BONUS)) for size in AWARDS_SIZES.ALL())), labelFormatter=text_styles.stats, align=LABEL_ALIGN.RIGHT, specialAlias=TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_TANKWOMAN, isSpecial=True, specialArgs=[]) if total else None


class AddOperationAwardComposer(PersonalMissionsAwardComposer):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(PersonalMissionsAwardComposer, self).__init__(_OPERATION_AWARDS_COUNT, getOperationPacker())

    def getFormattedBonuses(self, operation, size=AWARDS_SIZES.BIG, gap=0):
        bonuses = self._getBonuses(operation)
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(preformattedBonuses, size, gap)

    def _getBonuses(self, operation):
        ctx = {'branch': operation.getBranch()}
        hiddenQuests = self._eventsCache.getHiddenQuests()
        finder = finders.getQuestByTokenAndBonus
        baseQuest = finder(hiddenQuests, finders.addQuestTokenFinder(operation))
        bonuses = baseQuest.getBonuses(ctx=ctx)
        if not operation.getNextOperationIDs():
            token = finders.PERSONAL_MISSION_BADGES_TOKEN % operation.getCampaignID()
            topBageQuest = finder(hiddenQuests, finders.tokenFinder(token))
            bonuses.extend(topBageQuest.getBonuses(ctx=ctx))
        return bonuses


class TooltipOperationAwardComposer(MainOperationAwardComposer):
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
            for _, bonuses in operation.getBonuses().iteritems():
                bonusList.extend(bonuses)

        else:
            hiddenQuests = self._eventsCache.getHiddenQuests()
            finder = finders.getQuestByTokenAndBonus
            if not operation.isFullCompleted():
                extrasQuest = finder(hiddenQuests, finders.addQuestTokenFinder(operation))
                bonusList.extend(extrasQuest.getBonuses())
        return bonusList

    def _getPreformattedTankwomanBonus(self, operation):
        if not operation.isFullCompleted():
            current, total = _getTankwomansCountInOperation(operation)
            currentStr = text_styles.bonusAppliedText(current) if current else text_styles.stats(current)
            images = dict(((size, RES_ICONS.getBonusIcon(size, 'tankwoman')) for size in AWARDS_SIZES.ALL()))
            return PreformattedBonus(bonusName=self._TANKWOMAN_BONUS, label='%s / %s' % (currentStr, str(total)), images=images, labelFormatter=text_styles.main)
        else:
            return None


class TooltipPostponedOperationAwardComposer(TooltipOperationAwardComposer):
    POSTPONE_PERSONAL_MISSION_TOKEN = 'pm2_t%s_early_access'

    def _getBonuses(self, operation):
        hiddenQuests = self._eventsCache.getHiddenQuests()
        awardQuestName = self.POSTPONE_PERSONAL_MISSION_TOKEN % operation.getID()
        for questID, quest in hiddenQuests.iteritems():
            if questID == awardQuestName:
                return quest.getBonuses()

        return []

    def _getPreformattedTankwomanBonus(self, operation):
        pass


class MarathonAwardComposer(CurtailingAwardsComposer):
    AWARDS_PER_LINE_COUNT = 3

    def _packBonuses(self, preformattedBonuses, size):
        bonusCount = len(preformattedBonuses)
        mergedBonuses = []
        if self._displayedRewardsCount > bonusCount > self.AWARDS_PER_LINE_COUNT:
            awardsCount = self.AWARDS_PER_LINE_COUNT
            sliceIdx = awardsCount - 1
            displayBonuses = preformattedBonuses[:sliceIdx]
            mergedBonuses = preformattedBonuses[sliceIdx:]
        elif bonusCount > self.AWARDS_PER_LINE_COUNT and bonusCount > self._displayedRewardsCount:
            awardsCount = self._displayedRewardsCount
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


class AnniversaryAwardComposer(CurtailingAwardsComposer):

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(self._doCustomSort(preformattedBonuses), size=AWARDS_SIZES.SMALL)

    def _doCustomSort(self, bonuses):
        for idx, bonus in enumerate(bonuses):
            if PostProcessTags.IS_SUFFIX_BADGE in bonus.postProcessTags:
                bonuses.pop(idx)
                bonuses.append(bonus)
                break

        return bonuses


class EpicCurtailingAwardsComposer(CurtailingAwardsComposer):

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        bonuses = []
        for bonus in preformattedBonuses:
            specialTooltipImg = bonus.getImage('tooltip')
            shortData = {'name': bonus.userName,
             'label': bonus.getFormattedLabel(),
             'imgSource': specialTooltipImg if specialTooltipImg else bonus.getImage(size)}
            bonuses.append(shortData)

        return bonuses


class RoyaleCurtailingAwardsComposer(CurtailingAwardsComposer):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        bonuses = []
        for bonus in preformattedBonuses:
            name = bonus.userName
            if bonus.specialAlias in (TOOLTIPS_CONSTANTS.BADGE, TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD):
                typeName = userName = name
                if bonus.specialAlias == TOOLTIPS_CONSTANTS.BADGE:
                    typeName = backport.text(R.strings.battle_royale.tooltips.awards.badge())
                if bonus.specialAlias == TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS:
                    typeName = backport.text(R.strings.battle_royale.tooltips.awards.achievement())
                if bonus.specialAlias == TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD:
                    item = cls.itemsCache.items.getItemByCD(bonus.specialArgs[0])
                    userName = item.userName
                name = backport.text(R.strings.battle_royale.tooltips.awards.pattern(), typeName=typeName, userName=userName)
            shortData = {'name': name,
             'label': bonus.getFormattedLabel(),
             'imgSource': bonus.getImage(size)}
            bonuses.append(shortData)

        return bonuses
