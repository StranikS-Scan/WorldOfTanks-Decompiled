# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/achievement.py
import logging
import constants
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.utils import getPlayerName
from helpers import dependency
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
         AchievementRecordsField(self, 'records'))


class GlobalRatingTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(GlobalRatingTooltipData, self).__init__(context, TOOLTIP_TYPE.ACHIEVEMENT)

    def getDisplayableData(self, *args):
        return {'name': makeString('#achievements:globalRating'),
         'descr': makeString('#achievements:globalRating_descr'),
         'isInDossier': True}


class BadgeTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BadgeTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=16)
        self._setWidth(364)

    def _packBlocks(self, badgeID):
        blocks = super(BadgeTooltipData, self)._packBlocks()
        badge = self._context.buildItem(badgeID)
        paramsConfig = self._context.getParamsConfiguration(badge)
        if badge is None:
            _logger.warning('Missing tooltip text for %r, please check badge.po', int(badgeID))
            return blocks
        else:
            tooltipData = [formatters.packTextBlockData(text_styles.highTitle(badge.getUserName())), formatters.packImageBlockData(badge.getHugeIcon(), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=11))]
            if g_currentVehicle.isPresent() and paramsConfig.showVehicle:
                vehicle = g_currentVehicle.item
                tooltipData.append(formatters.packBadgeInfoBlockData(badge.getThumbnailIcon(), vehicle.iconContour, text_styles.bonusPreviewText(getPlayerName()), text_styles.bonusPreviewText(vehicle.shortUserName)))
            blocks.append(formatters.packBuildUpBlockData(tooltipData))
            blocks.append(formatters.packTextBlockData(text_styles.main(badge.getUserDescription())))
            return blocks
