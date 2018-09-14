# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/clan_statistics_vos.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.clans.profile import getI18ArenaById
from gui.clans.items import formatField
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import BaseDictStatisticsVO
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils as PUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import DetailedStatisticsUtils as SUtils
from gui.Scaleform.locale.CLANS import CLANS as CL, CLANS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip, getArenaGeomentryName

def _resourceParam(value):
    return ''.join((text_styles.defRes(value), icons.nutStat()))


def _getTooltip(headerKey, bodyKey, ratingOutdated = False):
    if ratingOutdated:
        return makeTooltip(headerKey, bodyKey, None, CL.GLOBALMAPVIEW_TOOLTIP_RATINGOUTDATED)
    else:
        return makeTooltip(headerKey, bodyKey)
        return None


def _getDataObject(key, i18nFunc, value, ratingOutdated = False, tooltipData = None):
    tooltip = _getTooltip(i18nFunc(key + '/tooltip/header'), i18nFunc(key + '/tooltip/body'), ratingOutdated)
    if ratingOutdated:
        value = text_styles.standard(value)
    else:
        value = text_styles.stats(value)
    return SUtils.getDetailedDataObject(i18nFunc(key), value, tooltip, tooltipData)


def _getDataObjectTruncatedValue(key, i18nFunc, value):
    tooltip = _getTooltip(_ms(i18nFunc(key + '/tooltip/header'), value=value), _ms(i18nFunc(key + '/tooltip/body'), value=value))
    data = SUtils.getDetailedDataObject(i18nFunc(key), value, tooltip)
    data.update({'isUseTextStyle': True,
     'truncateVo': {'isUseTruncate': True,
                    'textStyle': 'statsText',
                    'maxWidthTF': 100}})
    return data


def _getLevelParams(i18nFunc, battlesCountGetter, winsEfficiencyGetter, eloRatingGetter, placeGetter, favArenaNameGetter, ratingOutdated):
    battlesCount = formatField(getter=battlesCountGetter, formatter=BigWorld.wg_getIntegralFormat)
    winsEfficiency = formatField(getter=winsEfficiencyGetter, formatter=lambda x: PUtils.formatFloatPercent(x))
    eloRating = formatField(getter=eloRatingGetter, formatter=BigWorld.wg_getIntegralFormat)
    place = formatField(getter=placeGetter, formatter=BigWorld.wg_getIntegralFormat)
    favArenaName = formatField(getter=favArenaNameGetter, formatter=lambda x: getI18ArenaById(getArenaGeomentryName(x)))
    return [_getDataObject('battles', i18nFunc, battlesCount),
     _getDataObject('wins', i18nFunc, winsEfficiency),
     _getDataObject('eloRating', i18nFunc, eloRating),
     _getDataObject('place', i18nFunc, place, ratingOutdated),
     _getDataObjectTruncatedValue('favoriteMap', i18nFunc, favArenaName)]


class FortSortiesStatisticsVO(BaseDictStatisticsVO):

    def __init__(self, data, fsBattlesCountLast28days, sortiesWinsCountLast28d):
        self.__sortiesBattlesCountLast28d = fsBattlesCountLast28days
        self.__sortiesWinsCountLast28d = sortiesWinsCountLast28d or 0
        super(FortSortiesStatisticsVO, self).__init__(data)

    def _getHeaderText(self, data):
        return _ms(CLANS.SECTION_FORT_VIEW_STATISTICS_SORTIES_HEADER)

    def _getHeaderData(self, data):
        return (PUtils.getTotalBattlesHeaderParam(data, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP), PUtils.packLditItemData(PUtils.getFormattedWinsEfficiency(data), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP, 'wins40x32.png'), PUtils.packLditItemData(PUtils.formatEfficiency(data.getBattlesCount(), data.getAvgLoot), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP, 'avgDefes40x32.png'))

    def _getDetailedData(self, data):
        return PUtils.getLabelDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_HEADER, [SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_MIDDLEBATTLESCOUNT, BigWorld.wg_getIntegralFormat(data.getMiddleBattlesCount()), CL.SECTION_FORT_TOOLTIPS_MIDDLEBATTLESCOUNT),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_CHAMPIONBATTLESCOUNT, BigWorld.wg_getIntegralFormat(data.getChampionBattlesCount()), CL.SECTION_FORT_TOOLTIPS_CHAMPIONBATTLESCOUNT),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_ABSOLUTEBATTLESCOUNT, BigWorld.wg_getIntegralFormat(data.getAbsoluteBattlesCount()), CL.SECTION_FORT_TOOLTIPS_ABSOLUTEBATTLESCOUNT),
         None,
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_WINSEFFICIENCY28, PUtils.getEfficiencyPercent(self.__sortiesWinsCountLast28d, self.__sortiesBattlesCountLast28d), CL.SECTION_FORT_TOOLTIPS_WINSEFFICIENCY28),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_AVGBATTLESCOUNT28, BigWorld.wg_getIntegralFormat(self.__sortiesBattlesCountLast28d), CL.SECTION_FORT_TOOLTIPS_AVGBATTLESCOUNT28),
         None,
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_SORTIES_DETAILED_LOOTINSORTIES, _resourceParam(BigWorld.wg_getIntegralFormat(data.getLoot())), CL.SECTION_FORT_TOOLTIPS_LOOTINSORTIES)])


class FortBattlesStatisticsVO(BaseDictStatisticsVO):

    def __init__(self, data, fbBattlesCountAbs, fbBattlesCountChemp):
        self.__fbBattlesCountAbs = fbBattlesCountAbs
        self.__fbBattlesCountChemp = fbBattlesCountChemp
        self.__resourceLossCount = data.getResourceLossCount()
        self.__resourceCaptureCount = data.getResourceCaptureCount()
        super(FortBattlesStatisticsVO, self).__init__(data)

    def _getHeaderText(self, data):
        return _ms(CLANS.SECTION_FORT_VIEW_STATISTICS_BATTLES_HEADER)

    def _getHeaderData(self, data):
        return (PUtils.packLditItemData(BigWorld.wg_getIntegralFormat(data.getBattlesCount()), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLESCOUNT_LABEL, TOOLTIPS.FORTIFICATION_CLANSTATS_PERIODDEFENCE_BATTLES_BATTLESCOUNT, 'battles40x32.png', PUtils.createToolTipData([BigWorld.wg_getIntegralFormat(data.getWinsCount()), BigWorld.wg_getIntegralFormat(data.getLossesCount())])), PUtils.packLditItemData(PUtils.getFormattedWinsEfficiency(data), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_WINS_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_WINS_TOOLTIP, 'wins40x32.png'), PUtils.packLditItemData(PUtils.formatEfficiency(self.__resourceLossCount, lambda : float(self.__resourceCaptureCount) / self.__resourceLossCount), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_AVGDEFRES_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_AVGDEFRES_TOOLTIP, 'defresRatio40x32.png'))

    def _getDetailedData(self, stats):
        defenceCount = stats.getDefenceCount()
        atackCount = stats.getAttackCount()
        sucessDefenceCount = stats.getSuccessDefenceCount()
        sucessAtackCount = stats.getSuccessAttackCount()
        resourceCaptureCount = stats.getResourceCaptureCount()
        resourceLossCount = stats.getResourceLossCount()
        resourcesProfitValue = resourceCaptureCount - resourceLossCount
        return PUtils.getLabelDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_HEADER, [SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_COUNTCAPTUREDCOMMANDCENTRES, BigWorld.wg_getIntegralFormat(stats.getEnemyBaseCaptureCount()), CL.SECTION_FORT_TOOLTIPS_COUNTCAPTUREDCOMMANDCENTRES),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_COUNTPLUNDEREDENEMYBUILDINGS, BigWorld.wg_getIntegralFormat(stats.getCaptureEnemyBuildingTotalCount()), CL.SECTION_FORT_TOOLTIPS_COUNTPLUNDEREDENEMYBUILDINGS),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_COUNTPLUNDEREDALLYBUILDINGS, BigWorld.wg_getIntegralFormat(stats.getLossOwnBuildingTotalCount()), CL.SECTION_FORT_TOOLTIPS_COUNTPLUNDEREDALLYBUILDINGS),
         None,
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_EFFICIENCYOFATTACK, PUtils.formatEfficiency(atackCount, lambda : float(sucessAtackCount) / atackCount), CL.SECTION_FORT_TOOLTIPS_EFFICIENCYOFATTACK, PUtils.createToolTipData([BigWorld.wg_getIntegralFormat(sucessAtackCount), BigWorld.wg_getIntegralFormat(atackCount)])),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_EFFICIENCYOFDEFENCE, PUtils.formatEfficiency(defenceCount, lambda : float(sucessDefenceCount) / defenceCount), CL.SECTION_FORT_TOOLTIPS_EFFICIENCYOFDEFENCE, PUtils.createToolTipData([BigWorld.wg_getIntegralFormat(sucessDefenceCount), BigWorld.wg_getIntegralFormat(defenceCount)])),
         None,
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_COUNTPROMRES, _resourceParam(BigWorld.wg_getIntegralFormat(resourceCaptureCount)), CL.SECTION_FORT_TOOLTIPS_COUNTPROMRES),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_LOSTPROMRES, _resourceParam(BigWorld.wg_getIntegralFormat(resourceLossCount)), CL.SECTION_FORT_TOOLTIPS_LOSTPROMRES),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_PROFIT, _resourceParam(BigWorld.wg_getIntegralFormat(resourcesProfitValue)), CL.SECTION_FORT_TOOLTIPS_PROFIT),
         None,
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_CHEMPIONLVLBATTLES, BigWorld.wg_getIntegralFormat(self.__fbBattlesCountAbs), CL.SECTION_FORT_TOOLTIPS_CHEMPIONLVLBATTLES),
         SUtils.getDetailedDataObject(CL.SECTION_FORT_VIEW_STATISTICS_BATTLES_DETAILED_ABSOLUTELVLBATTLES, BigWorld.wg_getIntegralFormat(self.__fbBattlesCountChemp), CL.SECTION_FORT_TOOLTIPS_ABSOLUTELVLBATTLES)])


class FortGlobalMapStatistics(BaseDictStatisticsVO):

    def _getHeaderData(self, data):
        stats = data['stats']
        return (PUtils.packLditItemData(formatField(getter=stats.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat), CLANS.GLOBALMAPVIEW_STATS_BATTLES, CLANS.GLOBALMAPVIEW_STATS_BATTLES_TOOLTIP, 'battles40x32.png'), PUtils.packLditItemData(formatField(getter=stats.getWinsEfficiency, formatter=PUtils.formatFloatPercent), CLANS.GLOBALMAPVIEW_STATS_WINS, CLANS.GLOBALMAPVIEW_STATS_WINS_TOOLTIP, 'wins40x32.png'), PUtils.packLditItemData(formatField(getter=stats.getCapturedProvincesCount, formatter=BigWorld.wg_getIntegralFormat), CLANS.GLOBALMAPVIEW_STATS_SEIZED, CLANS.GLOBALMAPVIEW_STATS_SEIZED_TOOLTIP, 'seizedProvinces40x32.png'))

    def _getDetailedData(self, data):
        stats = data['stats']
        ratings = data['ratings']
        favouriteAttrs = data['favouriteAttrs']
        ratingsOutDated = ratings.isGlobalMapOutdated()
        columns = [[PUtils.getLabelDataObject(CL.GLOBALMAPVIEW_LEVEL10, _getLevelParams(CL.globalmapview_statistics10, stats.getBattles10LevelCount, stats.getWins10LevelEfficiency, ratings.getGlobalMapEloRating10, ratings.getGlobalMapEloRatingRank10, favouriteAttrs.getFavouriteArena10, ratingsOutDated))], [PUtils.getLabelDataObject(CL.GLOBALMAPVIEW_LEVEL8, _getLevelParams(CL.globalmapview_statistics8, stats.getBattles8LevelCount, stats.getWins8LevelEfficiency, ratings.getGlobalMapEloRating8, ratings.getGlobalMapEloRatingRank8, favouriteAttrs.getFavouriteArena8, ratingsOutDated))], [PUtils.getLabelDataObject(CL.GLOBALMAPVIEW_LEVEL6, _getLevelParams(CL.globalmapview_statistics6, stats.getBattles6LevelCount, stats.getWins6LevelEfficiency, ratings.getGlobalMapEloRating6, ratings.getGlobalMapEloRatingRank6, favouriteAttrs.getFavouriteArena6, ratingsOutDated))]]
        return (PUtils.getLabelViewTypeDataObject(CLANS.GLOBALMAPVIEW_TABS_STATS, columns, PUtils.VIEW_TYPE_TABLES), PUtils.getLabelViewTypeDataObject(CLANS.GLOBALMAPVIEW_TABS_PROVINCES, None, PUtils.VIEW_TYPE_TABLE))
