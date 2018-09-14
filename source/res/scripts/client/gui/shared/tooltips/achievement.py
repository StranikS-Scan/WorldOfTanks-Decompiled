# Embedded file name: scripts/client/gui/shared/tooltips/achievement.py
import constants
from debug_utils import LOG_ERROR
from helpers.i18n import makeString
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.ui.achievements import MARK_OF_MASTERY_RECORD
from gui.shared import g_itemsCache
from gui.shared.tooltips import ToolTipParameterField, ToolTipDataField, ToolTipData, ToolTipMethodField, ToolTipBaseData, TOOLTIP_TYPE
from gui.shared.gui_items.dossier.achievements.abstract import achievementHasVehiclesList, isSeriesAchievement
_ACHIEVEMENT_VEHICLES_MAX = 5
_ACHIEVEMENT_VEHICLES_SHOW = 5

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
        if not configuration.checkAchievementExistence:
            return True
        return achievement.isInDossier()


class AchievementRecordsField(ToolTipDataField):

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
                records['nearest'] = [[makeString('#tooltips:achievement/recordOnVehicle', vehicleName=g_itemsCache.items.getItemByCD(int(achievement.getCompDescr())).shortUserName), max(achievement.getMarkOfMastery(), achievement.getPrevMarkOfMastery()) or achievement.MIN_LVL]]
        elif dossier is not None and dossierType == constants.DOSSIER_TYPE.ACCOUNT and isCurrentUserDossier:
            if achievement.getType() == 'series':
                vehicleRecords = set()
                vehsWereInBattle = set(dossier.getTotalStats().getVehicles().keys())
                for vehCD in vehsWereInBattle:
                    totalStats = g_itemsCache.items.getVehicleDossier(vehCD).getTotalStats()
                    if totalStats.isAchievementInLayout(achievement.getRecordName()):
                        vehAchieve = totalStats.getAchievement(achievement.getRecordName())
                        if vehAchieve and vehAchieve.getValue():
                            vehicle = g_itemsCache.items.getItemByCD(vehCD)
                            vehicleRecords.add((vehicle.userName, vehAchieve.getValue()))
                            if vehAchieve.getValue() == achievement.getValue():
                                records['current'] = vehicle.userName

                records['nearest'] = sorted(vehicleRecords, key=lambda x: x[1], reverse=True)[:3]
        return records


class AchievementTooltipData(ToolTipData):

    def __init__(self, context):
        super(AchievementTooltipData, self).__init__(context, TOOLTIP_TYPE.ACHIEVEMENT)
        self.fields = (ToolTipMethodField(self, 'name', 'getUserName'),
         ToolTipMethodField(self, 'icon', 'getBigIcon'),
         ToolTipMethodField(self, 'type', 'getType'),
         ToolTipMethodField(self, 'section', 'getSection'),
         ToolTipMethodField(self, 'descr', 'getUserDescription'),
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
