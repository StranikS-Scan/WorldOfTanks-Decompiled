# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/profile_statistics_vos.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils as PUtils, FALLOUT_STATISTICS_LAYOUT, FORT_STATISTICS_LAYOUT, STATISTICS_LAYOUT
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import DetailedStatisticsUtils as DSUtils
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.fortifications import isFortificationBattlesEnabled
from gui.Scaleform.locale.PROFILE import PROFILE
from helpers import i18n
from gui import GUI_NATIONS, getNationIndex
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from dossiers2.ui import layouts
import nations

def _packAvgDmgLditItemData(avgDmg):
    return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgDmg), PROFILE.SECTION_SUMMARY_SCORES_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDAMAGE, 'avgDamage40x32.png')


def _packAvgXPLditItemData(avgExp):
    return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgExp), PROFILE.SECTION_STATISTICS_SCORES_AVGEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGEXP, 'avgExp40x32.png')


def _getDetailedStatisticsData(label, targetData, isCurrentUser, layout = STATISTICS_LAYOUT):
    detailedStatisticsData = DSUtils.getStatistics(targetData, isCurrentUser, layout)
    result = []
    for val in detailedStatisticsData:
        result.append([val])

    return PUtils.getLabelViewTypeDataObject(label, result, PUtils.VIEW_TYPE_TABLES)


def _getBattleChartsStatistics(battlesStats, levelDisabledTooltip):
    outcome = []
    tDict = battlesStats[0]
    typesRes = []
    for vehType in VEHICLE_TYPES_ORDER:
        typesRes.append({'xField': i18n.makeString(DIALOGS.vehicleselldialog_vehicletype(vehType)),
         'icon': '../maps/icons/filters/tanks/{0}.png'.format(vehType),
         'yField': tDict[vehType],
         'tooltip': PROFILE.SECTION_STATISTICS_CHART_TYPE_TOOLTIP})

    _setChartDataPercentages(typesRes)
    outcome.append(typesRes)
    tDict = battlesStats[1]
    nationRes = []
    for guiNationIdx, _ in enumerate(GUI_NATIONS):
        nationIdx = getNationIndex(guiNationIdx)
        nationName = nations.NAMES[nationIdx]
        nationRes.append({'xField': i18n.makeString(MENU.nations(nationName)),
         'icon': '../maps/icons/filters/nations/{0}.png'.format(nationName),
         'yField': tDict[nationIdx],
         'tooltip': PROFILE.SECTION_STATISTICS_CHART_NATION_TOOLTIP})

    _setChartDataPercentages(nationRes)
    outcome.append(nationRes)
    tDict = battlesStats[2]
    lvlRes = len(tDict) * [None]
    for level, value in tDict.iteritems():
        tooltip = PROFILE.SECTION_STATISTICS_CHART_LEVEL_TOOLTIP
        if value is None:
            value = -1
            if levelDisabledTooltip != None:
                tooltip = levelDisabledTooltip
        lvlRes[level - 1] = {'xField': str(level),
         'icon': '../maps/icons/levels/tank_level_{0}.png'.format(level),
         'yField': value,
         'tooltip': tooltip}

    _setChartDataPercentages(lvlRes)
    outcome.append(lvlRes)
    return {'data': outcome}


def _setChartDataPercentages(chartData):
    yMax = max([ x['yField'] for x in chartData ])
    if yMax == 0:
        yMax = 1
    for data in chartData:
        data['percentValue'] = int(100 * data['yField'] / yMax)


def _getChartsData(targetData, levelDisabledTooltip = None):
    return PUtils.getLabelViewTypeDataObject(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CHARTS, _getBattleChartsStatistics(targetData.getBattlesStats(), levelDisabledTooltip), PUtils.VIEW_TYPE_CHARTS)


def _getFortAvgLoot(targetData, totalLootValue):
    battlesCount = targetData.getBattlesCountVer2()
    if battlesCount > 0:
        return BigWorld.wg_getNiceNumberFormat(totalLootValue / battlesCount)
    return PUtils.UNAVAILABLE_VALUE


class BaseDictStatisticsVO(dict):

    def __init__(self, data):
        super(BaseDictStatisticsVO, self).__init__({})
        headerText = self._getHeaderText(data)
        if headerText:
            self['headerText'] = headerText
        self['headerParams'] = self._getHeaderData(data)
        self['bodyParams'] = {'dataList': self._getDetailedData(data)}

    def _getHeaderText(self, data):
        return None

    def _getHeaderData(self, data):
        raise NotImplementedError

    def _getDetailedData(self, data):
        raise NotImplementedError


class ProfileDictStatisticsVO(BaseDictStatisticsVO):

    def __init__(self, targetData, accountDossier, isCurrentUser):
        self._isCurrentUser = isCurrentUser
        self._formattedWinsEfficiency = PUtils.getFormattedWinsEfficiency(targetData)
        self._dmgDealt = targetData.getDamageDealt()
        self._dmgReceived = targetData.getDamageReceived()
        self._damageEfficiency = BigWorld.wg_getNiceNumberFormat(PUtils.getValueOrUnavailable(targetData.getDamageEfficiency()))
        damageBlockedByArmor = targetData.getDamageBlockedByArmor()
        potentialDamageReceived = targetData.getPotentialDamageReceived()
        pResDmg = potentialDamageReceived - damageBlockedByArmor
        self._armorUsingEfficiency = PUtils.getValueOrUnavailable(targetData.getArmorUsingEfficiency())
        self._avgXP = PUtils.getValueOrUnavailable(targetData.getAvgXP())
        self._avgDmg = PUtils.getValueOrUnavailable(targetData.getAvgDamage())
        maxXP = targetData.getMaxXp()
        self._maxXP_formattedStr = BigWorld.wg_getIntegralFormat(maxXP)
        self._armorUsingToolTipData = PUtils.createToolTipData([PUtils.getAvgDamageBlockedValue(targetData)])
        self._avgAssistDmg = BigWorld.wg_getNiceNumberFormat(PUtils.getValueOrUnavailable(targetData.getDamageAssistedEfficiency()))
        super(ProfileDictStatisticsVO, self).__init__((targetData, accountDossier))


class ProfileAllStatisticsVO(ProfileDictStatisticsVO):

    def _getHeaderText(self, data):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_ALL)

    def _getHeaderData(self, data):
        targetData = data[0]
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'),
         _packAvgDmgLditItemData(self._avgDmg),
         _packAvgXPLditItemData(self._avgXP),
         PUtils.packLditItemData(self._maxXP_formattedStr, PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, 'maxExp40x32.png', PUtils.getVehicleRecordTooltipData(targetData.getMaxXpVehicle)),
         PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(targetData.getMarksOfMastery()[3]), PROFILE.SECTION_STATISTICS_SCORES_COOLSIGNS, PROFILE.PROFILE_PARAMS_TOOLTIP_MARKOFMASTERY, 'markOfMastery40x32.png'))

    def _getDetailedData(self, data):
        targetData = data[0]
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser), _getChartsData(targetData))


class ProfileHistoricalStatisticsVO(ProfileDictStatisticsVO):

    def _getHeaderText(self, data):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_HISTORICAL)

    def _getHeaderData(self, data):
        targetData = data[0]
        histBattleFieldAchievesCount = 0
        for record in layouts.HISTORY_BATTLEFIELD_GROUP:
            achieve = targetData.getAchievement(record)
            if achieve.isInDossier():
                histBattleFieldAchievesCount += 1

        histBattleFieldAchievesCount = BigWorld.wg_getIntegralFormat(histBattleFieldAchievesCount)
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'),
         PUtils.packLditItemData(histBattleFieldAchievesCount, PROFILE.SECTION_STATISTICS_SCORES_ACHIEVEMENTSCOUNT, PROFILE.PROFILE_PARAMS_TOOLTIP_ACHIEVEMENTSCOUNT, 'honors40x32.png'),
         PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(len(targetData.getVehicles())), PROFILE.SECTION_STATISTICS_SCORES_USEDTECHNICS, PROFILE.PROFILE_PARAMS_TOOLTIP_USEDTECHNICS, 'techRatio40x32.png'))

    def _getDetailedData(self, data):
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, data[0], self._isCurrentUser),)


class Profile7x7StatisticsVO(ProfileDictStatisticsVO):

    def _getHeaderText(self, data):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_TEAM)

    def _getHeaderData(self, data):
        return (PUtils.getTotalBattlesHeaderParam(data[0], PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._damageEfficiency, PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF, 'dmgRatio40x32.png', PUtils.createToolTipData((BigWorld.wg_getIntegralFormat(self._dmgDealt), BigWorld.wg_getIntegralFormat(self._dmgReceived)))),
         _packAvgDmgLditItemData(self._avgDmg),
         _packAvgXPLditItemData(self._avgXP),
         PUtils.packLditItemData(self._avgAssistDmg, PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE, 'assist40x32.png'),
         PUtils.packLditItemData(BigWorld.wg_getNiceNumberFormat(self._armorUsingEfficiency), PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING, 'armorUsing40x32.png', self._armorUsingToolTipData))

    def _getDetailedData(self, data):
        targetData = data[0]
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser), _getChartsData(targetData, PROFILE.SECTION_STATISTICS_CHART_LEVELDISABLED7X7_TOOLTIP))


class StaticProfile7x7StatisticsVO(Profile7x7StatisticsVO):

    def _getDetailedData(self, data):
        targetData = data[0]
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser),)


class ProfileFortStatisticsVO(ProfileDictStatisticsVO):

    def __init__(self, targetData, accountDossier, isCurrentUser):
        self.__fortMiscTargetData = accountDossier.getFortMiscStats()
        self.__totalSortiesLoot = self.__fortMiscTargetData.getLootInSorties()
        self.__fortBattlesTargetData = accountDossier.getFortBattlesStats()
        self.__avgFortSortiesLoot = _getFortAvgLoot(targetData, self.__totalSortiesLoot)
        super(ProfileFortStatisticsVO, self).__init__(targetData, accountDossier, isCurrentUser)

    def _getHeaderText(self, data):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_FORTIFICATIONS)

    def _getHeaderData(self, data):
        headerParams = []
        if isFortificationBattlesEnabled():
            headerParams.append(PUtils.getTotalBattlesHeaderParam(self.__fortBattlesTargetData, PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLES))
            headerParams.append(PUtils.packLditItemData(PUtils.getFormattedWinsEfficiency(self.__fortBattlesTargetData), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLESWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLESWINSEFFICIENCY, 'wins40x32.png'))
        else:
            headerParams.append(PUtils.packLditItemData(str(PUtils.UNAVAILABLE_VALUE), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLE_FORT_BATTLES, 'battles40x32.png'))
            headerParams.append(PUtils.packLditItemData(str(PUtils.UNAVAILABLE_VALUE), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLESWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLE_FORT_WINSEFFICIENCY, 'wins40x32.png'))
        headerParams.append(PUtils.getTotalBattlesHeaderParam(data[0], PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIE, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIE))
        headerParams.append(PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIEWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIEWINSEFFICIENCY, 'wins40x32.png'))
        headerParams.append(PUtils.packLditItemData(str(self.__avgFortSortiesLoot), PROFILE.SECTION_STATISTICS_SCORES_FORT_RESOURCE, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_RESOURCE, 'resources40x32.png'))
        return headerParams

    def _getDetailedData(self, data):
        targetData = data[0]
        dataList = []
        if isFortificationBattlesEnabled():
            dataList.append(_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_FORTBATTLES, self.__fortBattlesTargetData, isCurrentUser=self._isCurrentUser, layout=FORT_STATISTICS_LAYOUT))
        dataList.append(_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_FORTSORTIE, targetData, isCurrentUser=self._isCurrentUser))
        specificData = []
        battlesCount = self.__fortBattlesTargetData.getBattlesCount()
        lossesCount = self.__fortBattlesTargetData.getLossesCount()
        winsCount = self.__fortBattlesTargetData.getWinsCount()
        formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
        specificDataColumn1 = []
        if isFortificationBattlesEnabled():
            specificDataColumn1.append(PUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_FORTBATTLES, (DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTTOTALBATTLES, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLES, PUtils.createToolTipData((BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount)))),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLESTOTALWINS, PUtils.getFormattedWinsEfficiency(self.__fortBattlesTargetData), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLESWINS),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_LOOTING, self.__fortMiscTargetData.getEnemyBasePlunderNumber(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_LOOTING),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_ATTACKS, self.__fortMiscTargetData.getAttackNumber(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_ATTACKS),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_DEFENCES, self.__fortMiscTargetData.getDefenceHours(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_DEFENCES))))
        battlesCount = targetData.getBattlesCount()
        lossesCount = targetData.getLossesCount()
        winsCount = targetData.getWinsCount()
        drawsCount = targetData.getDrawsCount()
        formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
        specificDataColumn1.append(PUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_FORTSORTIE, (DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIE, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIE, PUtils.createToolTipData((BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount), BigWorld.wg_getIntegralFormat(drawsCount)))), DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIETOTALWINS, self._formattedWinsEfficiency, PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIEWINS))))
        specificData.append(specificDataColumn1)
        resourcesDataList = [DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIES_AVGRESOURCES, self.__avgFortSortiesLoot, PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIES_AVGRESOURCES), DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIES_TOTALRESOURCES, BigWorld.wg_getIntegralFormat(self.__totalSortiesLoot), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIES_TOTALRESOURCES)]
        specificDataColumn2 = []
        if isFortificationBattlesEnabled():
            resourcesDataList.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_TOTALRESOURCES, BigWorld.wg_getIntegralFormat(self.__fortMiscTargetData.getLootInBattles()), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_TOTALRESOURCES))
            resourcesDataList.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_MAXRESOURCES, BigWorld.wg_getIntegralFormat(self.__fortMiscTargetData.getMaxLootInBattles()), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_MAXRESOURCES))
        specificDataColumn2.append(PUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RESOURCE, resourcesDataList))
        specificData.append(specificDataColumn2)
        dataList.append(PUtils.getLabelViewTypeDataObject(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_SPECIFIC, specificData, PUtils.VIEW_TYPE_TABLES))
        return dataList


class ProfileGlobalMapStatisticsVO(ProfileDictStatisticsVO):

    def _getHeaderText(self, data):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_CLAN)

    def _getHeaderData(self, data):
        targetData = data[0]
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'),
         _packAvgDmgLditItemData(self._avgDmg),
         _packAvgXPLditItemData(self._avgXP),
         PUtils.packLditItemData(self._maxXP_formattedStr, PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, 'maxExp40x32.png', PUtils.getVehicleRecordTooltipData(targetData.getMaxXpVehicle)),
         PUtils.packLditItemData(self._damageEfficiency, PROFILE.SECTION_STATISTICS_SCORES_CLAN_SUMMARYDAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_CLAN_SUMMARYDAMAGECOEFFICIENT, 'dmgRatio40x32.png', PUtils.createToolTipData((BigWorld.wg_getIntegralFormat(self._dmgDealt), BigWorld.wg_getIntegralFormat(self._dmgReceived)))))

    def _getDetailedData(self, data):
        accountDossier = data[1]
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CLAN6, accountDossier.getGlobalMapMiddleStats(), self._isCurrentUser), _getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CLAN8, accountDossier.getGlobalMapChampionStats(), self._isCurrentUser), _getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CLAN10, accountDossier.getGlobalMapAbsoluteStats(), self._isCurrentUser))


class ProfileFalloutStatisticsVO(ProfileDictStatisticsVO):

    def __init__(self, targetData, accountDossier, isCurrentUser):
        self.__avgVictoryPoints = PUtils.getValueOrUnavailable(targetData.getAvgVictoryPoints())
        self.__maxVictoryPoints = targetData.getMaxVictoryPoints()
        self.__kdr = targetData.getFragsEfficiency()
        self.__kills = targetData.getFragsCount()
        self.__consumablesKills = targetData.getConsumablesFragsCount()
        self.__deaths = targetData.getDeathsCount()
        super(ProfileFalloutStatisticsVO, self).__init__(targetData, accountDossier, isCurrentUser)

    def _getHeaderText(self, data):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_FALLOUT)

    def _getHeaderData(self, data):
        targetData = data[0]
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_BATTLESCOUNT),
         self.__packAvgVictoryPointsData(self.__avgVictoryPoints),
         _packAvgXPLditItemData(self._avgXP),
         self.__packAvgDmgData(self._avgDmg),
         self.__packMaxVictoryPoints(self.__maxVictoryPoints),
         self.__packKDR(self.__kdr, self.__kills, self.__consumablesKills, self.__deaths))

    def _getDetailedData(self, data):
        targetData = data[0]
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser, FALLOUT_STATISTICS_LAYOUT), _getChartsData(targetData, PROFILE.SECTION_STATISTICS_CHART_LEVELDISABLEDFALLOUT_TOOLTIP))

    def __packAvgVictoryPointsData(self, avgVictoryPoints):
        return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgVictoryPoints), PROFILE.SECTION_STATISTICS_SCORES_AVGVICTORYPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGVICTORYPOINTS, 'avgVictoryPoints48x48.png')

    def __packMaxVictoryPoints(self, maxVictoryPoints):
        return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(maxVictoryPoints), PROFILE.SECTION_STATISTICS_SCORES_MAXVICTORYPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXVICTORYPOINTS, 'maxVictoryPoints48x48.png')

    def __packKDR(self, kdr, kills, consumablesKills, deaths):
        return PUtils.packLditItemData(BigWorld.wg_getNiceNumberFormat(kdr) if kdr is not None else PUtils.UNAVAILABLE_VALUE, PROFILE.SECTION_STATISTICS_SCORES_KILLDEATHRATIO, PROFILE.PROFILE_PARAMS_TOOLTIP_KDR, 'kdr48x48.png', PUtils.createToolTipData([kills, consumablesKills, deaths]))

    def __packAvgDmgData(self, avgDmg):
        return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgDmg), PROFILE.SECTION_SUMMARY_SCORES_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_AVGDAMAGE, 'avgDamage40x32.png')


_VO_MAPPING = {PROFILE_DROPDOWN_KEYS.ALL: ProfileAllStatisticsVO,
 PROFILE_DROPDOWN_KEYS.FALLOUT: ProfileFalloutStatisticsVO,
 PROFILE_DROPDOWN_KEYS.HISTORICAL: ProfileHistoricalStatisticsVO,
 PROFILE_DROPDOWN_KEYS.TEAM: Profile7x7StatisticsVO,
 PROFILE_DROPDOWN_KEYS.STATICTEAM: StaticProfile7x7StatisticsVO,
 PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON: StaticProfile7x7StatisticsVO,
 PROFILE_DROPDOWN_KEYS.CLAN: ProfileGlobalMapStatisticsVO,
 PROFILE_DROPDOWN_KEYS.FORTIFICATIONS: ProfileFortStatisticsVO}

def getStatisticsVO(battlesType, targetData, accountDossier, isCurrentUser):
    return _VO_MAPPING[battlesType](targetData=targetData, accountDossier=accountDossier, isCurrentUser=isCurrentUser)
