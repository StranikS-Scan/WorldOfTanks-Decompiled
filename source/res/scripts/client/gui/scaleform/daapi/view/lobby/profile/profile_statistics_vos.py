# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/profile_statistics_vos.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils as PUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import DetailedStatisticsUtils as DSUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import HeaderItemsTypes
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.shared.fortifications import isFortificationBattlesEnabled
from gui.Scaleform.locale.PROFILE import PROFILE
from helpers import i18n
from gui import GUI_NATIONS, getNationIndex
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from dossiers2.ui import layouts

def _packAvgDmgLditItemData(avgDmg):
    return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgDmg), PROFILE.SECTION_SUMMARY_SCORES_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDAMAGE, 'avgDamage40x32.png')


def _packAvgXPLditItemData(avgExp):
    return PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(avgExp), PROFILE.SECTION_STATISTICS_SCORES_AVGEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGEXP, 'avgExp40x32.png')


def _getDetailedStatisticsData(label, targetData, isCurrentUser):
    detailedStatisticsData = DSUtils.getStatistics(targetData, isCurrentUser)
    additionalDataBlock = detailedStatisticsData[0]['data']
    additionalDataBlock.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_CAPTUREPOINTS, BigWorld.wg_getIntegralFormat(targetData.getCapturePoints()), PROFILE.PROFILE_PARAMS_TOOLTIP_CAPTUREPOINTS))
    additionalDataBlock.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_DROPPEDCAPTUREPOINTS, BigWorld.wg_getIntegralFormat(targetData.getDroppedCapturePoints()), PROFILE.PROFILE_PARAMS_TOOLTIP_DROPPEDCAPTUREPOINTS))
    result = []
    for val in detailedStatisticsData:
        result.append([val])

    return PUtils.getLabelViewTypeDataObject(label, result, PUtils.VIEW_TYPE_TABLES)


def _getBattleChartsStatistics(battlesStats):
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


def _getChartsData(targetData):
    return PUtils.getLabelViewTypeDataObject(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CHARTS, _getBattleChartsStatistics(targetData.getBattlesStats()), PUtils.VIEW_TYPE_CHARTS)


def _getFortAvgLoot(targetData, totalLootValue):
    battlesCount = targetData.getBattlesCountVer2()
    if battlesCount > 0:
        return BigWorld.wg_getNiceNumberFormat(totalLootValue / battlesCount)
    return PUtils.UNAVAILABLE_VALUE


class ProfileStatisticsVO(dict):

    def __init__(self, targetData, accountDossier, isCurrentUser):
        super(ProfileStatisticsVO, self).__init__()
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
        self['headerText'] = self._getHeaderText()
        self['headerParams'] = self._getHeaderData(targetData, accountDossier)
        self['bodyParams'] = {'dataList': self._getDetailedData(targetData, accountDossier)}

    def _getHeaderText(self):
        raise NotImplementedError

    def _getHeaderData(self, targetData, accountDossier):
        raise NotImplementedError

    def _getDetailedData(self, targetData, accountDossier):
        raise NotImplementedError


class ProfileAllStatisticsVO(ProfileStatisticsVO):

    def _getHeaderText(self):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_ALL)

    def _getHeaderData(self, targetData, accountDossier):
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'),
         _packAvgDmgLditItemData(self._avgDmg),
         _packAvgXPLditItemData(self._avgXP),
         PUtils.packLditItemData(self._maxXP_formattedStr, PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, 'maxExp40x32.png', PUtils.getVehicleRecordTooltipData(targetData.getMaxXpVehicle)),
         PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(targetData.getMarksOfMastery()[3]), PROFILE.SECTION_STATISTICS_SCORES_COOLSIGNS, PROFILE.PROFILE_PARAMS_TOOLTIP_MARKOFMASTERY, 'markOfMastery40x32.png'))

    def _getDetailedData(self, targetData, accountDossier):
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser), _getChartsData(targetData))


class ProfileHistoricalStatisticsVO(ProfileStatisticsVO):

    def _getHeaderText(self):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_HISTORICAL)

    def _getHeaderData(self, targetData, accountDossier):
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

    def _getDetailedData(self, targetData, accountDossier):
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser),)


class Profile7x7StatisticsVO(ProfileStatisticsVO):

    def _getHeaderText(self):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_TEAM)

    def _getHeaderData(self, targetData, accountDossier):
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._damageEfficiency, PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF, 'dmgRatio40x32.png', PUtils.createToolTipData((BigWorld.wg_getIntegralFormat(self._dmgDealt), BigWorld.wg_getIntegralFormat(self._dmgReceived)))),
         _packAvgDmgLditItemData(self._avgDmg),
         _packAvgXPLditItemData(self._avgXP),
         PUtils.packLditItemData(self._avgAssistDmg, PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE, 'assist40x32.png'),
         PUtils.packLditItemData(BigWorld.wg_getNiceNumberFormat(self._armorUsingEfficiency), PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING, 'armorUsing40x32.png', self._armorUsingToolTipData))

    def _getDetailedData(self, targetData, accountDossier):
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser), _getChartsData(targetData))


class StaticProfile7x7StatisticsVO(Profile7x7StatisticsVO):

    def _getDetailedData(self, targetData, accountDossier):
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser),)


class ProfileFortStatisticsVO(ProfileStatisticsVO):

    def __init__(self, targetData, accountDossier, isCurrentUser):
        self.__fortMiscTargetData = accountDossier.getFortMiscStats()
        self.__totalSortiesLoot = self.__fortMiscTargetData.getLootInSorties()
        self.__fortBattlesTargetData = accountDossier.getFortBattlesStats()
        self.__avgFortSortiesLoot = _getFortAvgLoot(targetData, self.__totalSortiesLoot)
        super(ProfileFortStatisticsVO, self).__init__(targetData, accountDossier, isCurrentUser)

    def _getHeaderText(self):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_FORTIFICATIONS)

    def _getHeaderData(self, targetData, accountDossier):
        headerParams = []
        if isFortificationBattlesEnabled():
            headerParams.append(PUtils.getTotalBattlesHeaderParam(self.__fortBattlesTargetData, PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLES))
            headerParams.append(PUtils.packLditItemData(PUtils.getFormattedWinsEfficiency(self.__fortBattlesTargetData), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLESWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLESWINSEFFICIENCY, 'wins40x32.png'))
        else:
            headerParams.append(PUtils.packLditItemData(str(PUtils.UNAVAILABLE_VALUE), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLE_FORT_BATTLES, 'battles40x32.png'))
            headerParams.append(PUtils.packLditItemData(str(PUtils.UNAVAILABLE_VALUE), PROFILE.SECTION_STATISTICS_SCORES_FORT_BATTLESWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLE_FORT_WINSEFFICIENCY, 'wins40x32.png'))
        headerParams.append(PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIE, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIE))
        headerParams.append(PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIEWINSEFFICIENCY, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIEWINSEFFICIENCY, 'wins40x32.png'))
        headerParams.append(PUtils.packLditItemData(str(self.__avgFortSortiesLoot), PROFILE.SECTION_STATISTICS_SCORES_FORT_RESOURCE, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_RESOURCE, 'resources40x32.png'))
        return headerParams

    def _getDetailedData(self, targetData, accountDossier):
        dataList = []
        if isFortificationBattlesEnabled():
            fortBattlesDetaildStatisticsTabData = _getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_FORTBATTLES, self.__fortBattlesTargetData, isCurrentUser=self._isCurrentUser)
            discToolTip = PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FORT_BATTLESCOUNT
            fortBattlesDetaildStatisticsTabData['data'][0][0]['data'][0]['tooltip'] = discToolTip
            dataList.append(fortBattlesDetaildStatisticsTabData)
        dataList.append(_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_FORTSORTIE, targetData, isCurrentUser=self._isCurrentUser))
        specificData = []
        battlesCount = self.__fortBattlesTargetData.getBattlesCount()
        lossesCount = self.__fortBattlesTargetData.getLossesCount()
        winsCount = self.__fortBattlesTargetData.getWinsCount()
        battlesToolTipData = [BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount)]
        formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
        specificDataColumn1 = []
        if isFortificationBattlesEnabled():
            specificDataColumn1.append(PUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_FORTBATTLES, [DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTTOTALBATTLES, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_BATTLES, PUtils.createToolTipData(battlesToolTipData)),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLESTOTALWINS, PUtils.getFormattedWinsEfficiency(self.__fortBattlesTargetData), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLESWINS),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_LOOTING, self.__fortMiscTargetData.getEnemyBasePlunderNumber(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_LOOTING),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_ATTACKS, self.__fortMiscTargetData.getAttackNumber(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_ATTACKS),
             DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_DEFENCES, self.__fortMiscTargetData.getDefenceHours(), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_DEFENCES)]))
        battlesCount = targetData.getBattlesCount()
        lossesCount = targetData.getLossesCount()
        winsCount = targetData.getWinsCount()
        drawsCount = PUtils.getDrawCount(battlesCount, lossesCount, winsCount)
        battlesToolTipData = [BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount), BigWorld.wg_getIntegralFormat(drawsCount)]
        formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
        specificDataColumn1.append(PUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_FORTSORTIE, [DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORT_SORTIE, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_FORT_SORTIE, PUtils.createToolTipData(battlesToolTipData)), DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIETOTALWINS, self._formattedWinsEfficiency, PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIEWINS)]))
        specificData.append(specificDataColumn1)
        resourcesDataList = []
        resourcesDataList.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIES_AVGRESOURCES, self.__avgFortSortiesLoot, PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIES_AVGRESOURCES))
        resourcesDataList.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTSORTIES_TOTALRESOURCES, BigWorld.wg_getIntegralFormat(self.__totalSortiesLoot), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTSORTIES_TOTALRESOURCES))
        if isFortificationBattlesEnabled():
            resourcesDataList.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_TOTALRESOURCES, BigWorld.wg_getIntegralFormat(self.__fortMiscTargetData.getLootInBattles()), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_TOTALRESOURCES))
            resourcesDataList.append(DSUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FORTBATTLES_MAXRESOURCES, BigWorld.wg_getIntegralFormat(self.__fortMiscTargetData.getMaxLootInBattles()), PROFILE.PROFILE_PARAMS_TOOLTIP_FORTBATTLES_MAXRESOURCES))
        specificData.append([PUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RESOURCE, resourcesDataList)])
        dataList.append(PUtils.getLabelViewTypeDataObject(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_SPECIFIC, specificData, PUtils.VIEW_TYPE_TABLES))
        return dataList


class ProfileGlobalMapStatisticsVO(ProfileStatisticsVO):

    def _getHeaderText(self):
        return i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_CLAN)

    def _getHeaderData(self, targetData, accountDossier):
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'),
         _packAvgDmgLditItemData(self._avgDmg),
         _packAvgXPLditItemData(self._avgXP),
         PUtils.packLditItemData(self._maxXP_formattedStr, PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, 'maxExp40x32.png', PUtils.getVehicleRecordTooltipData(targetData.getMaxXpVehicle)),
         PUtils.packLditItemData(self._damageEfficiency, PROFILE.SECTION_STATISTICS_SCORES_CLAN_SUMMARYDAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_CLAN_SUMMARYDAMAGECOEFFICIENT, 'dmgRatio40x32.png', PUtils.createToolTipData((BigWorld.wg_getIntegralFormat(self._dmgDealt), BigWorld.wg_getIntegralFormat(self._dmgReceived)))))

    def _getDetailedData(self, targetData, accountDossier):
        return (_getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CLAN6, accountDossier.getGlobalMapMiddleStats(), self._isCurrentUser), _getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CLAN8, accountDossier.getGlobalMapChampionStats(), self._isCurrentUser), _getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_CLAN10, accountDossier.getGlobalMapAbsoluteStats(), self._isCurrentUser))


_VO_MAPPING = {PROFILE_DROPDOWN_KEYS.ALL: ProfileAllStatisticsVO,
 PROFILE_DROPDOWN_KEYS.HISTORICAL: ProfileHistoricalStatisticsVO,
 PROFILE_DROPDOWN_KEYS.TEAM: Profile7x7StatisticsVO,
 PROFILE_DROPDOWN_KEYS.STATICTEAM: StaticProfile7x7StatisticsVO,
 PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON: StaticProfile7x7StatisticsVO,
 PROFILE_DROPDOWN_KEYS.CLAN: ProfileGlobalMapStatisticsVO,
 PROFILE_DROPDOWN_KEYS.FORTIFICATIONS: ProfileFortStatisticsVO}

def getStatisticsVO(battlesType, targetData, accountDossier, isCurrentUser):
    return _VO_MAPPING[battlesType](targetData=targetData, accountDossier=accountDossier, isCurrentUser=isCurrentUser)
