# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/achievement.py
import logging
import constants
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.formatters.icons import makeImageTag
from gui.shared.money import Money
from gui.shared.utils import getPlayerName
from helpers import dependency, int2roman
from helpers.i18n import makeString
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.ui.achievements import MARK_OF_MASTERY_RECORD
from gui.shared.tooltips import ToolTipParameterField, ToolTipDataField, ToolTipData, ToolTipMethodField, ToolTipBaseData, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.gui_items.dossier.achievements.abstract import achievementHasVehiclesList, isSeriesAchievement
from skeletons.gui.shared import IItemsCache
_ACHIEVEMENT_VEHICLES_MAX = 5
_ACHIEVEMENT_VEHICLES_SHOW = 5
_logger = logging.getLogger(__name__)

class AchievementParamsField(ToolTipParameterField):

    def _getValue(self):
        result = [[]]
        achievement = self._tooltip.item
        if achievement is None:
            LOG_ERROR('There is error while building achievement tooltip', achievement)
            return result
        else:
            label, lvlUpValue = achievement.getNextLevelInfo()
            if label and lvlUpValue and lvlUpValue > 0:
                result[-1].append([label, lvlUpValue])
            if isSeriesAchievement(achievement):
                record, maxSeries = achievement.getMaxSeriesInfo()
                if record is not None and maxSeries:
                    result[-1].append([record[1], maxSeries])
            if achievementHasVehiclesList(achievement):
                vehiclesList = achievement.getVehiclesData()
                fullVehListLen = len(vehiclesList)
                if fullVehListLen >= _ACHIEVEMENT_VEHICLES_MAX:
                    vehiclesList = vehiclesList[:_ACHIEVEMENT_VEHICLES_SHOW]
                if fullVehListLen:
                    result[-1].append([achievement.getVehiclesListTitle(), vehiclesList, fullVehListLen])
            return result


class AchievementStatsField(ToolTipDataField):

    def _getValue(self):
        result = dict()
        achievement = self._tooltip.item
        if achievement and achievement.getType() == 'class':
            result['classParams'] = RECORD_CONFIGS.get(achievement.getName())
        return result


class AchievementIsInDossierField(ToolTipDataField):

    def _getValue(self):
        achievement = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(achievement)
        return True if not configuration.checkAchievementExistence else achievement.isInDossier()


class AchievementRecordsField(ToolTipDataField):
    itemsCache = dependency.descriptor(IItemsCache)

    def _getValue(self):
        records = {'current': None,
         'nearest': None}
        achievement = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(achievement)
        dossier = configuration.dossier
        dossierType = configuration.dossierType
        isCurrentUserDossier = configuration.isCurrentUserDossier
        if achievement.getRecordName() == MARK_OF_MASTERY_RECORD:
            if achievement.getCompDescr() is not None:
                if achievement.getPrevMarkOfMastery() < achievement.getMarkOfMastery():
                    records['current'] = makeString('#tooltips:achievement/newRecord')
                records['nearest'] = [[makeString('#tooltips:achievement/recordOnVehicle', vehicleName=self.itemsCache.items.getItemByCD(int(achievement.getCompDescr())).shortUserName), max(achievement.getMarkOfMastery(), achievement.getPrevMarkOfMastery()) or achievement.MIN_LVL]]
        elif dossier is not None and dossierType == constants.DOSSIER_TYPE.ACCOUNT and isCurrentUserDossier:
            if achievement.getType() == 'series':
                vehicleRecords = set()
                vehsWereInBattle = set(dossier.getTotalStats().getVehicles().keys())
                for vehCD in vehsWereInBattle:
                    totalStats = self.itemsCache.items.getVehicleDossier(vehCD).getTotalStats()
                    if totalStats.isAchievementInLayout(achievement.getRecordName()):
                        vehAchieve = totalStats.getAchievement(achievement.getRecordName())
                        if vehAchieve and vehAchieve.getValue():
                            vehicle = self.itemsCache.items.getItemByCD(vehCD)
                            vehicleRecords.add((vehicle.userName, vehAchieve.getValue()))
                            if vehAchieve.getValue() == achievement.getValue():
                                records['current'] = vehicle.userName

                records['nearest'] = sorted(vehicleRecords, key=lambda x: x[1], reverse=True)[:3]
        return records


class AchievementCrystalRewardField(ToolTipDataField):
    itemsCache = dependency.descriptor(IItemsCache)
    _rewardsLabels = None
    _rewardsValues = None
    _playerVehicleLevel = 0
    _playerRangeIndex = -1

    def _getValue(self):
        self._rewardsLabels = []
        self._rewardsValues = []
        self._playerRangeIndex = -1
        achievement = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(achievement)
        arenaType = configuration.arenaType
        rewardData = self.itemsCache.items.shop.getAchievementReward(achievement, arenaType)
        if not rewardData:
            return
        else:
            self._playerVehicleLevel = configuration.vehicleLevel
            baseReward = Money.makeMoney(rewardData['bonus'])
            vehLevelMultipliers = self._applyMultiplierToReward(baseReward, rewardData['vehicleMultipliers'])
            count = len(vehLevelMultipliers) - 1
            i = 0
            lastMulIndex = -1
            lastMulValue = None
            while i <= count:
                mulValue = vehLevelMultipliers[i]
                if lastMulIndex == -1:
                    lastMulIndex = i
                    lastMulValue = mulValue
                else:
                    isLastIndex = i == count
                    if lastMulValue != mulValue:
                        self._appendRewardsRange(lastMulIndex, i - 1, vehLevelMultipliers[lastMulIndex])
                        if isLastIndex:
                            self._appendRewardsRange(i, i, vehLevelMultipliers[i])
                        else:
                            lastMulIndex = i
                            lastMulValue = mulValue
                    elif isLastIndex:
                        self._appendRewardsRange(lastMulIndex, i, vehLevelMultipliers[lastMulIndex])
                i += 1

            rewardsCount = len(self._rewardsLabels)
            if rewardsCount > 0:
                headerValue = ''
                if rewardsCount == 10:
                    headerValue = self._rewardsValues[0]
                return {'selectedIndex': self._playerRangeIndex,
                 'header': makeString(TOOLTIPS.ACHIEVEMENT_REWARD_HEADER),
                 'headerValue': headerValue,
                 'labels': self._rewardsLabels,
                 'values': self._rewardsValues}
            return
            return

    def _applyMultiplierToReward(self, money, multipliers):
        result = []
        for multiplier in multipliers:
            moneyWithMultiplier = money * multiplier
            result.append(moneyWithMultiplier.apply(lambda v: int(round(v))))

        return result

    def _getRangeStr(self, currentIndex, lastIndex):
        if currentIndex - lastIndex > 0:
            levelsRange = '{0}-{1}'.format(int2roman(lastIndex + 1), int2roman(currentIndex + 1))
        else:
            levelsRange = int2roman(lastIndex + 1)
        return levelsRange

    def _appendRewardsRange(self, startIndex, endIndex, rewardValue):
        if rewardValue:
            levelsRangeStr = self._getRangeStr(endIndex, startIndex)
            self._rewardsLabels.append(makeString(TOOLTIPS.ACHIEVEMENT_REWARD_TANKLEVELS, range=levelsRangeStr))
            if self._playerVehicleLevel > 0:
                if self._playerVehicleLevel >= startIndex + 1 and self._playerVehicleLevel <= endIndex + 1:
                    imgId = RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTAL_16X16
                    self._playerRangeIndex = len(self._rewardsLabels) - 1
                else:
                    imgId = RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTALICONINACTIVE_2
            else:
                imgId = RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTAL_16X16
            rewardStr = BigWorld.wg_getIntegralFormat(rewardValue.crystal)
            self._rewardsValues.append(rewardStr + ' ' + makeImageTag(imgId, 16, 16, -3, 0))


class AchievementTooltipData(ToolTipData):

    def __init__(self, context):
        super(AchievementTooltipData, self).__init__(context, TOOLTIP_TYPE.ACHIEVEMENT)
        self.fields = (ToolTipMethodField(self, 'name', 'getUserName'),
         ToolTipMethodField(self, 'icon', 'getHugeIcon'),
         ToolTipMethodField(self, 'type', 'getType'),
         ToolTipMethodField(self, 'section', 'getSection'),
         ToolTipMethodField(self, 'descr', 'getUserDescription'),
         ToolTipMethodField(self, 'showCondSeparator', 'getShowCondSeparator'),
         ToolTipMethodField(self, 'value', 'getValue'),
         ToolTipMethodField(self, 'localizedValue', 'getI18nValue'),
         ToolTipMethodField(self, 'historyDescr', 'getUserHeroInfo'),
         ToolTipMethodField(self, 'inactive', False, 'isActive'),
         ToolTipMethodField(self, 'condition', 'getUserCondition'),
         AchievementParamsField(self, 'params'),
         AchievementStatsField(self, 'stats'),
         AchievementIsInDossierField(self, 'isInDossier'),
         AchievementRecordsField(self, 'records'),
         AchievementCrystalRewardField(self, 'crystalAwards'))


class GlobalRatingTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(GlobalRatingTooltipData, self).__init__(context, TOOLTIP_TYPE.ACHIEVEMENT)

    def getDisplayableData(self, *args):
        return {'name': makeString('#achievements:globalRating'),
         'descr': makeString('#achievements:globalRating_descr'),
         'isInDossier': True}


class BadgeTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(BadgeTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=16)
        self._setWidth(364)

    def _packBlocks(self, badgeID):
        blocks = super(BadgeTooltipData, self)._packBlocks()
        badge = self.__itemsCache.items.getBadges().get(int(badgeID))
        if badge is None:
            _logger.warning('Missing tooltip text for %r, please check badge.po', int(badgeID))
            return blocks
        else:
            tooltipData = [formatters.packTextBlockData(text_styles.highTitle(badge.getUserName())), formatters.packImageBlockData(badge.getHugeIcon(), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=11))]
            if g_currentVehicle.isPresent():
                vehicle = g_currentVehicle.item
                tooltipData.append(formatters.packBadgeInfoBlockData(badge.getThumbnailIcon(), vehicle.iconContour, text_styles.bonusPreviewText(getPlayerName()), text_styles.bonusPreviewText(vehicle.shortUserName)))
            blocks.append(formatters.packBuildUpBlockData(tooltipData))
            blocks.append(formatters.packTextBlockData(text_styles.main(badge.getUserDescription())))
            return blocks
