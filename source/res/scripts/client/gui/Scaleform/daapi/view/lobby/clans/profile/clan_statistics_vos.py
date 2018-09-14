# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/clan_statistics_vos.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.clans.profile import getI18ArenaById
from gui.clans.items import formatField
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import BaseDictStatisticsVO
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils as PUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import DetailedStatisticsUtils as SUtils
from gui.Scaleform.locale.CLANS import CLANS as CL
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip

def _resourceParam(value):
    return ''.join((text_styles.defRes(value), icons.nutStat()))


def _getTooltip(headerKey, bodyKey, ratingOutdated=False):
    if ratingOutdated:
        return makeTooltip(headerKey, bodyKey, None, CL.GLOBALMAPVIEW_TOOLTIP_RATINGOUTDATED)
    else:
        return makeTooltip(headerKey, bodyKey)
        return None


def _getDataObject(key, i18nFunc, value, ratingOutdated=False, tooltipData=None):
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
    favArenaName = formatField(getter=favArenaNameGetter, formatter=lambda arena_id: getI18ArenaById(arena_id))
    return [_getDataObject('battles', i18nFunc, battlesCount),
     _getDataObject('wins', i18nFunc, winsEfficiency),
     _getDataObject('eloRating', i18nFunc, eloRating),
     _getDataObject('place', i18nFunc, place, ratingOutdated),
     _getDataObjectTruncatedValue('favoriteMap', i18nFunc, favArenaName)]


class FortGlobalMapStatistics(BaseDictStatisticsVO):

    def _getHeaderData(self, data):
        stats = data['stats']
        return (PUtils.packLditItemData(formatField(getter=stats.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat), CL.GLOBALMAPVIEW_STATS_BATTLES, CL.GLOBALMAPVIEW_STATS_BATTLES_TOOLTIP, 'battles40x32.png'), PUtils.packLditItemData(formatField(getter=stats.getWinsEfficiency, formatter=PUtils.formatFloatPercent), CL.GLOBALMAPVIEW_STATS_WINS, CL.GLOBALMAPVIEW_STATS_WINS_TOOLTIP, 'wins40x32.png'), PUtils.packLditItemData(formatField(getter=stats.getCapturedProvincesCount, formatter=BigWorld.wg_getIntegralFormat), CL.GLOBALMAPVIEW_STATS_SEIZED, CL.GLOBALMAPVIEW_STATS_SEIZED_TOOLTIP, 'seizedProvinces40x32.png'))

    def _getDetailedData(self, data):
        stats = data['stats']
        ratings = data['ratings']
        favouriteAttrs = data['favouriteAttrs']
        ratingsOutDated = ratings.isGlobalMapOutdated()
        columns = [[PUtils.getLabelDataObject(CL.GLOBALMAPVIEW_LEVEL10, _getLevelParams(CL.globalmapview_statistics10, stats.getBattles10LevelCount, stats.getWins10LevelEfficiency, ratings.getGlobalMapEloRating10, ratings.getGlobalMapEloRatingRank10, favouriteAttrs.getFavouriteArena10, ratingsOutDated))], [PUtils.getLabelDataObject(CL.GLOBALMAPVIEW_LEVEL8, _getLevelParams(CL.globalmapview_statistics8, stats.getBattles8LevelCount, stats.getWins8LevelEfficiency, ratings.getGlobalMapEloRating8, ratings.getGlobalMapEloRatingRank8, favouriteAttrs.getFavouriteArena8, ratingsOutDated))], [PUtils.getLabelDataObject(CL.GLOBALMAPVIEW_LEVEL6, _getLevelParams(CL.globalmapview_statistics6, stats.getBattles6LevelCount, stats.getWins6LevelEfficiency, ratings.getGlobalMapEloRating6, ratings.getGlobalMapEloRatingRank6, favouriteAttrs.getFavouriteArena6, ratingsOutDated))]]
        return (PUtils.getLabelViewTypeDataObject(CL.GLOBALMAPVIEW_TABS_STATS, columns, PUtils.VIEW_TYPE_TABLES), PUtils.getLabelViewTypeDataObject(CL.GLOBALMAPVIEW_TABS_PROVINCES, None, PUtils.VIEW_TYPE_TABLE))
