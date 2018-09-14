# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import GUI_NATIONS, getNationIndex
from dossiers2.ui import layouts
from gui.shared.fortifications import isFortificationEnabled, isFortificationBattlesEnabled
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, HeaderItemsTypes, DetailedStatisticsUtils
from gui.Scaleform.daapi.view.meta.ProfileStatisticsMeta import ProfileStatisticsMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from helpers import i18n

class ProfileStatistics(ProfileSection, ProfileStatisticsMeta):

    def __init__(self, *args):
        try:
            _, _, _, self.__ctx = args
        except Exception:
            LOG_ERROR('There is error while parsing profile stats page arguments', args)
            self.__ctx = {}

        ProfileSection.__init__(self, *args)
        ProfileStatisticsMeta.__init__(self)
        self.__battleChartsStats = _BattleChartsStatistics()

    def _populate(self):
        super(ProfileStatistics, self)._populate()
        self._setInitData(PROFILE.PROFILE_DROPDOWN_LABELS_ALL, False)

    def _setInitData(self, battlesType, showCurrentSeason):
        dropDownProvider = [PROFILE.PROFILE_DROPDOWN_LABELS_ALL,
         PROFILE.PROFILE_DROPDOWN_LABELS_HISTORICAL,
         PROFILE.PROFILE_DROPDOWN_LABELS_TEAM,
         PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM]
        if isFortificationEnabled():
            dropDownProvider.append(PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS)
        seasonItems = [{'key': PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM,
          'label': PROFILE.PROFILE_SEASONSDROPDOWN_ALL}]
        if showCurrentSeason:
            seasonItems.append({'key': PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM_SEASON,
             'label': PROFILE.PROFILE_SEASONSDROPDOWN_CURRENT})
        seasonIndex = 0
        for idx, season in enumerate(seasonItems):
            if season['key'] == battlesType:
                seasonIndex = idx

        self.as_setInitDataS({'dropDownProvider': dropDownProvider,
         'seasonItems': seasonItems,
         'seasonIndex': seasonIndex})

    def _sendAccountData(self, targetData, accountDossier):
        formattedWinsEfficiency = ProfileUtils.getFormattedWinsEfficiency(targetData)
        dmgDealt = targetData.getDamageDealt()
        dmgReceived = targetData.getDamageReceived()
        damageEfficiency = BigWorld.wg_getNiceNumberFormat(ProfileUtils.getValueOrUnavailable(targetData.getDamageEfficiency()))
        damageBlockedByArmor = targetData.getDamageBlockedByArmor()
        potentialDamageReceived = targetData.getPotentialDamageReceived()
        pResDmg = potentialDamageReceived - damageBlockedByArmor
        armorUsingEfficiency = ProfileUtils.getValueOrUnavailable(targetData.getArmorUsingEfficiency())
        avgXP = ProfileUtils.getValueOrUnavailable(targetData.getAvgXP())
        avgDmg = ProfileUtils.getValueOrUnavailable(targetData.getAvgDamage())
        maxXP = targetData.getMaxXp()
        maxXP_formattedStr = BigWorld.wg_getIntegralFormat(maxXP)
        armorUsingToolTipData = ProfileUtils.createToolTipData([ProfileUtils.getAvgDamageBlockedValue(targetData)])
        avgAssistDmg = BigWorld.wg_getNiceNumberFormat(ProfileUtils.getValueOrUnavailable(targetData.getDamageAssistedEfficiency()))
        vehicles = targetData.getVehicles()
        vehiclesLen = len(vehicles)
        headerParams = []
        dataList = []
        if self._battlesType in (PROFILE.PROFILE_DROPDOWN_LABELS_TEAM, PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM, PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM_SEASON):
            headerText = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_TEAM)
            if self._battlesType in (PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM, PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM_SEASON):
                headerText = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_STATICTEAM)
                self._setInitData(self._battlesType, targetData.getBattlesCount() > 0)
                self._battlesType = PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM
            headerParams.append(ProfileUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT))
            headerParams.append(ProfileUtils.packLditItemData(damageEfficiency, PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF, 'dmgRatio40x32.png', {'tooltipData': ProfileUtils.createToolTipData((BigWorld.wg_getIntegralFormat(dmgDealt), BigWorld.wg_getIntegralFormat(dmgReceived)))}, HeaderItemsTypes.VALUES))
            headerParams.append(self.__packAvgDmgLditItemData(avgDmg))
            headerParams.append(self.__packAvgXPLditItemData(avgXP))
            headerParams.append(ProfileUtils.packLditItemData(avgAssistDmg, PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE, 'assist40x32.png'))
            headerParams.append(ProfileUtils.packLditItemData(BigWorld.wg_getNiceNumberFormat(armorUsingEfficiency), PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING, 'armorUsing40x32.png', {'tooltipData': armorUsingToolTipData}, HeaderItemsTypes.VALUES))
            dataList.append(self.__getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData))
            dataList.append(self.__getChartsData(targetData))
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_HISTORICAL:
            headerParams.append(ProfileUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT))
            headerText = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_HISTORICAL)
            histBattleFieldAchievesCount = 0
            for record in layouts.HISTORY_BATTLEFIELD_GROUP:
                achieve = targetData.getAchievement(record)
                if achieve.isInDossier():
                    histBattleFieldAchievesCount += 1

            histBattleFieldAchievesCount = BigWorld.wg_getIntegralFormat(histBattleFieldAchievesCount)
            histBattleFieldAchievesCountTotal = BigWorld.wg_getIntegralFormat(len(layouts.HISTORY_BATTLEFIELD_GROUP))
            headerParams.append(ProfileUtils.packLditItemData(formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'))
            headerParams.append(ProfileUtils.packLditItemData(histBattleFieldAchievesCount, PROFILE.SECTION_STATISTICS_SCORES_ACHIEVEMENTSCOUNT, PROFILE.PROFILE_PARAMS_TOOLTIP_ACHIEVEMENTSCOUNT, 'honors40x32.png', {'total': histBattleFieldAchievesCountTotal}, HeaderItemsTypes.RATIO))
            headerParams.append(ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(vehiclesLen), PROFILE.SECTION_STATISTICS_SCORES_USEDTECHNICS, PROFILE.PROFILE_PARAMS_TOOLTIP_USEDTECHNICS, 'techRatio40x32.png'))
            dataList.append(self.__getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData))
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS:
            headerText = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_FORTIFICATIONS)
            fortBattlesTargetData = accountDossier.getFortBattlesStats()
            fortMiscTargetData = accountDossier.getFortMiscStats()
            if isFortificationBattlesEnabled():
                headerParams.append(ProfileUtils.getTotalBattlesHeaderParam(fortBattlesTargetData, PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLES))
                headerParams.append(ProfileUtils.packLditItemData(ProfileUtils.getFormattedWinsEfficiency(fortBattlesTargetData), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLESWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLESWINSEFFICIENCY, 'wins40x32.png'))
            else:
                headerParams.append(ProfileUtils.packLditItemData(str(ProfileUtils.UNAVAILABLE_VALUE), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLE_FORT_BATTLES, 'battles40x32.png'))
                headerParams.append(ProfileUtils.packLditItemData(str(ProfileUtils.UNAVAILABLE_VALUE), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLESWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLE_FORT_WINSEFFICIENCY, 'wins40x32.png'))
            headerParams.append(ProfileUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIE, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIE))
            headerParams.append(ProfileUtils.packLditItemData(formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIEWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIEWINSEFFICIENCY, 'wins40x32.png'))
            totalSortiesLoot = fortMiscTargetData.getLootInSorties()
            avgFortSortiesLoot = self.__getFortAvgLoot(targetData, totalSortiesLoot)
            headerParams.append(ProfileUtils.packLditItemData(str(avgFortSortiesLoot), PROFILE.SECTION_STATISTICS_SCORES_FORT_RESOURCE, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_RESOURCE, 'resources40x32.png'))
            if isFortificationBattlesEnabled():
                fortBattlesDetaildStatisticsTabData = self.__getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_FORTBATTLES, fortBattlesTargetData)
                fortBattlesDetaildStatisticsTabData['data'][0][0]['data'][0]['tooltip'] = PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FORT_BATTLESCOUNT
                dataList.append(fortBattlesDetaildStatisticsTabData)
            dataList.append(self.__getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_FORTSORTIE, targetData))
            specificData = []
            battlesCount = fortBattlesTargetData.getBattlesCount()
            lossesCount = fortBattlesTargetData.getLossesCount()
            winsCount = fortBattlesTargetData.getWinsCount()
            battlesToolTipData = [BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount)]
            formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
            specificDataColumn1 = []
            if isFortificationBattlesEnabled():
                specificDataColumn1.append(ProfileUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_FORTBATTLES, [DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTTOTALBATTLES, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLES, ProfileUtils.createToolTipData(battlesToolTipData)),
                 DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLESTOTALWINS, ProfileUtils.getFormattedWinsEfficiency(fortBattlesTargetData), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLESWINS),
                 DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_LOOTING, fortMiscTargetData.getEnemyBasePlunderNumber(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_LOOTING),
                 DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_ATTACKS, fortMiscTargetData.getAttackNumber(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_ATTACKS),
                 DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_DEFENCES, fortMiscTargetData.getDefenceHours(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_DEFENCES)]))
            battlesCount = targetData.getBattlesCount()
            lossesCount = targetData.getLossesCount()
            winsCount = targetData.getWinsCount()
            drawsCount = ProfileUtils.getDrawCount(battlesCount, lossesCount, winsCount)
            battlesToolTipData = [BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount), BigWorld.wg_getIntegralFormat(drawsCount)]
            formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
            specificDataColumn1.append(ProfileUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_FORTSORTIE, [DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIE, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIE, ProfileUtils.createToolTipData(battlesToolTipData)), DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIETOTALWINS, formattedWinsEfficiency, PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIEWINS)]))
            specificData.append(specificDataColumn1)
            resourcesDataList = []
            resourcesDataList.append(DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIES_AVGRESOURCES, avgFortSortiesLoot, PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIES_AVGRESOURCES))
            resourcesDataList.append(DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIES_TOTALRESOURCES, BigWorld.wg_getIntegralFormat(totalSortiesLoot), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIES_TOTALRESOURCES))
            if isFortificationBattlesEnabled():
                resourcesDataList.append(DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_TOTALRESOURCES, BigWorld.wg_getIntegralFormat(fortMiscTargetData.getLootInBattles()), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_TOTALRESOURCES))
                resourcesDataList.append(DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_MAXRESOURCES, BigWorld.wg_getIntegralFormat(fortMiscTargetData.getMaxLootInBattles()), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_MAXRESOURCES))
            specificData.append([ProfileUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RESOURCE, resourcesDataList)])
            dataList.append(ProfileUtils.getLabelViewTypeDataObject(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_SPECIFIC, specificData, ProfileUtils.VIEW_TYPE_TABLES))
        else:
            maxExpToolTipData = ProfileUtils.getVehicleRecordTooltipData(targetData.getMaxXpVehicle)
            headerText = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_ALL)
            headerParams.append(ProfileUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT))
            headerParams.append(ProfileUtils.packLditItemData(formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'))
            headerParams.append(self.__packAvgDmgLditItemData(avgDmg))
            headerParams.append(self.__packAvgXPLditItemData(avgXP))
            headerParams.append(ProfileUtils.packLditItemData(maxXP_formattedStr, PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, 'maxExp40x32.png', {'tooltipData': maxExpToolTipData}, HeaderItemsTypes.VALUES))
            headerParams.append(ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(targetData.getMarksOfMastery()[3]), PROFILE.SECTION_STATISTICS_SCORES_COOLSIGNS, PROFILE.PROFILE_PARAMS_TOOLTIP_MARKOFMASTERY, 'markOfMastery40x32.png', {'total': BigWorld.wg_getIntegralFormat(vehiclesLen)}, HeaderItemsTypes.RATIO))
            dataList.append(self.__getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData))
            dataList.append(self.__getChartsData(targetData))
        bodyParams = {'dataList': dataList}
        showSeasonDropdown = self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_STATICTEAM
        self.as_responseDossierS(self._battlesType, {'headerText': headerText,
         'showSeasonDropdown': showSeasonDropdown,
         'headerParams': headerParams,
         'bodyParams': bodyParams})

    def __getFortAvgLoot(self, targetData, totalLootValue):
        battlesCount = targetData.getBattlesCountVer2()
        if battlesCount > 0:
            return BigWorld.wg_getNiceNumberFormat(totalLootValue / battlesCount)
        return ProfileUtils.UNAVAILABLE_VALUE

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def __getDetailedStatisticsData(self, label, targetData):
        detailedStatisticsData = DetailedStatisticsUtils.getStatistics(targetData, self._userID is None)
        detailedStatisticsData[0]['data'].append(DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_CAPTUREPOINTS, BigWorld.wg_getIntegralFormat(targetData.getCapturePoints()), PROFILE.PROFILE_PARAMS_TOOLTIP_CAPTUREPOINTS))
        detailedStatisticsData[0]['data'].append(DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_DROPPEDCAPTUREPOINTS, BigWorld.wg_getIntegralFormat(targetData.getDroppedCapturePoints()), PROFILE.PROFILE_PARAMS_TOOLTIP_DROPPEDCAPTUREPOINTS))
        result = []
        for val in detailedStatisticsData:
            result.append([val])

        return ProfileUtils.getLabelViewTypeDataObject(label, result, ProfileUtils.VIEW_TYPE_TABLES)

    def __getChartsData(self, targetData):
        return ProfileUtils.getLabelViewTypeDataObject(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CHARTS, self.__battleChartsStats.getData(targetData.getBattlesStats()), ProfileUtils.VIEW_TYPE_CHARTS)

    def __packAvgDmgLditItemData(self, avgDmg):
        return ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgDmg), PROFILE.SECTION_SUMMARY_SCORES_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDAMAGE, 'avgDamage40x32.png')

    def __packAvgXPLditItemData(self, avgExp):
        return ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgExp), PROFILE.SECTION_STATISTICS_SCORES_AVGEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGEXP, 'avgExp40x32.png')

    def setSeason(self, seasonId):
        self.requestDossier(seasonId)

    def _dispose(self):
        super(ProfileStatistics, self)._dispose()


class _BattleChartsStatistics(object):

    def __init__(self):
        super(_BattleChartsStatistics, self).__init__()

    def getData(self, battlesStats):
        outcome = []
        tDict = battlesStats[0]
        typesRes = []
        for value in VEHICLE_TYPES_ORDER:
            typesRes.append({value: tDict[value]})

        outcome.append(typesRes)
        tDict = battlesStats[1]
        nationRes = []
        for guiNationIdx, _ in enumerate(GUI_NATIONS):
            nationIdx = getNationIndex(guiNationIdx)
            nationRes.append({str(nationIdx): tDict[nationIdx]})

        outcome.append(nationRes)
        tDict = battlesStats[2]
        lvlRes = len(tDict) * [None]
        for level, value in tDict.iteritems():
            if value is None:
                value = -1
            lvlRes[level - 1] = {str(level): value}

        outcome.append(lvlRes)
        return {'data': outcome}
