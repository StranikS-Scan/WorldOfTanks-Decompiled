# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubSummaryView.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubPage
from gui.clubs.club_helpers import isSeasonInProgress
from helpers.i18n import makeString as _ms
from gui.clubs.settings import MIN_BATTLES_FOR_STATS, getLadderChevron256x256
from gui.clubs.formatters import getDivisionString, getLeagueString
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.meta.StaticFormationSummaryViewMeta import StaticFormationSummaryViewMeta
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import getArenaFullName
from gui.shared.gui_items.dossier import dumpDossier
BEST_TANKS_GROUP_WIDTH = 152
BEST_MAPS_GROUP_WIDTH = 211
MAX_ITEMS_IN_LIST = 5

class ClubSummaryView(StaticFormationSummaryViewMeta, ClubPage):

    def __init__(self):
        super(ClubSummaryView, self).__init__()
        self._clubDbID = None
        self._owner = None
        return

    def onClubUpdated(self, club):
        if club is not None:
            self._initializeGui(club)
        return

    def onClubLadderInfoChanged(self, ladderInfo):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club is not None:
            self.__setData(club)
        return

    def onClubDossierChanged(self, seasonDossier, totalDossier):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club is not None:
            self.__setData(club)
        return

    def _populate(self):
        super(ClubSummaryView, self)._populate()

    def _dispose(self):
        super(ClubSummaryView, self)._dispose()
        self.clearClub()

    def _initializeGui(self, club):
        self.__setData(club)

    def __setData(self, club):
        ladderInfo = club.getLadderInfo()
        seasonDossier = club.getSeasonDossier()
        totalStats = seasonDossier.getTotalStats()
        battlesNumData, winsPercentData, attackDamageEfficiency, defenceDamageEfficiency = _makeStats(totalStats)
        battleCounts = totalStats.getBattlesCount()
        ladderIconSource = getLadderChevron256x256(ladderInfo.getDivision() if battleCounts else None)
        globalStats = seasonDossier.getGlobalStats()
        registeredDate = text_styles.main(BigWorld.wg_getShortDateFormat(club.getCreationTime()))
        registeredText = text_styles.standard(_ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_REGISTERED, date=registeredDate))
        lastBattleText = _getLastBattleText(battleCounts, globalStats)
        bestTanksText = text_styles.stats(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_BESTTANKS)
        bestMapsText = text_styles.stats(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_BESTMAPS)
        notEnoughTanksText = notEnoughMapsText = text_styles.standard(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_NOTENOUGHTANKSMAPS)
        bestTanks = _getVehiclesList(totalStats)
        bestMaps = _getMapsList(totalStats)
        noAwardsText = text_styles.stats(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_NOAWARDS)
        ribbonSource = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_RIBBON
        self.as_setDataS({'clubId': club.getClubDbID(),
         'placeText': _getPositionText(ladderInfo),
         'leagueDivisionText': _getDivisionText(ladderInfo),
         'ladderPtsText': _getLadderPointsText(ladderInfo),
         'bestTanksText': bestTanksText,
         'bestMapsText': bestMapsText,
         'notEnoughTanksText': notEnoughTanksText,
         'notEnoughMapsText': notEnoughMapsText,
         'registeredText': registeredText,
         'lastBattleText': lastBattleText,
         'ladderIconSource': ladderIconSource,
         'noAwardsText': noAwardsText,
         'ribbonSource': ribbonSource,
         'battlesNumData': battlesNumData,
         'winsPercentData': winsPercentData,
         'attackDamageEfficiencyData': attackDamageEfficiency,
         'defenceDamageEfficiencyData': defenceDamageEfficiency,
         'bestTanks': bestTanks,
         'notEnoughTanksTFVisible': not len(bestTanks),
         'bestMaps': bestMaps,
         'notEnoughMapsTFVisible': not len(bestMaps),
         'achievements': _makeAchievements(seasonDossier),
         'bestTanksGroupWidth': BEST_TANKS_GROUP_WIDTH,
         'bestMapsGroupWidth': BEST_MAPS_GROUP_WIDTH})
        return


def _getLastBattleText(battlesCount, globalStats):
    lastBattleDate = text_styles.main(BigWorld.wg_getShortDateFormat(globalStats.getLastBattleTime()))
    if battlesCount > 0:
        return text_styles.standard(_ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LASTBATTLE, date=lastBattleDate))
    return ''


def _getVehiclesList(totalStats):
    battleCounts = totalStats.getBattlesCount()
    bestTanks = []
    if battleCounts >= MIN_BATTLES_FOR_STATS:
        vehList = sorted(totalStats.getVehicles().iteritems(), key=lambda (k, v): v.xp, reverse=True)
        if len(vehList) > MAX_ITEMS_IN_LIST:
            vehList = vehList[0:MAX_ITEMS_IN_LIST]
        for idx, (vehCD, vInfo) in enumerate(vehList):
            bestTanks.append(_makeVehicleVO(idx, vehCD))

    return bestTanks


def _makeVehicleVO(idx, vehCD):
    label = str(idx + 1) + '.'
    vehicle = g_itemsCache.items.getItemByCD(vehCD)
    return {'label': text_styles.standard(label),
     'value': text_styles.stats(vehicle.shortUserName),
     'iconSource': vehicle.iconContour}


def _getDivisionText(ladderInfo):
    if ladderInfo.isInLadder():
        leagueStr = text_styles.warning(getLeagueString(ladderInfo.getLeague()))
        divisionStr = text_styles.warning(getDivisionString(ladderInfo.division))
        return text_styles.middleTitle(_ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LADDER_LEAGUEDIVISION, league=leagueStr, division=divisionStr))
    else:
        return text_styles.alert(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_NOTENOUGHGAMES_WARNING)


def _getLadderPointsText(ladderInfo):
    if ladderInfo.isInLadder():
        ladderPtsStr = text_styles.warning(str(ladderInfo.getRatingPoints()))
        return text_styles.main(_ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LADDER_LADDERPTS, points=ladderPtsStr))
    else:
        return text_styles.main(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_NOTENOUGHGAMES_INFO)


def _getPositionText(ladderInfo):
    if ladderInfo.isInLadder():
        positionStr = _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_LADDER_PLACE, place=ladderInfo.position)
        return text_styles.promoSubTitle(positionStr)
    else:
        return ''


def _makeStats(totalStats):
    battlesNumData = {'text': BigWorld.wg_getIntegralFormat(totalStats.getBattlesCount()),
     'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_BATTLES),
     'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_BATTLES40X32,
     'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_BATTLES}
    winsEfficiency = totalStats.getWinsEfficiency() * 100 if totalStats.getWinsEfficiency() else 0
    winsPercentData = {'text': BigWorld.wg_getNiceNumberFormat(winsEfficiency) + '%',
     'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_WINSPERCENT),
     'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINS40X32,
     'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_WINSPERCENT}
    attackDamageEfficiency = {'text': BigWorld.wg_getIntegralFormat(totalStats.getAttackDamageEfficiency() or 0),
     'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_ATTACKDAMAGEEFFICIENCY),
     'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_AVGATTACKDMG40X32,
     'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_WINSBYCAPTURE}
    defenceDamageEfficiency = {'text': BigWorld.wg_getIntegralFormat(totalStats.getDefenceDamageEfficiency() or 0),
     'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_DEFENCEDAMAGEEFFICIENCY),
     'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_AVGDEFENCEDMG40X32,
     'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_TECHDEFEATS}
    return (battlesNumData,
     winsPercentData,
     attackDamageEfficiency,
     defenceDamageEfficiency)


def _makeAchievements(dossier):
    return AchievementsUtils.packAchievementList(dossier.getTotalStats().getSignificantAchievements(), dossier.getDossierType(), dumpDossier(dossier), True, False)


def _getMapsList(totalStats):
    battleCounts = totalStats.getBattlesCount()
    bestMaps = []
    if battleCounts >= MIN_BATTLES_FOR_STATS:
        mapsList = sorted(totalStats.getMaps().iteritems(), key=lambda (k, v): v.winsEfficiency, reverse=True)
        if len(mapsList) > MAX_ITEMS_IN_LIST:
            mapsList = mapsList[0:MAX_ITEMS_IN_LIST]
        for idx, (mapID, mapInfo) in enumerate(mapsList):
            bestMaps.append(_makeMapVO(idx, mapID, mapInfo))

    return bestMaps


def _makeMapVO(idx, mapID, mapInfo):
    label = str(idx + 1) + '.'
    mapName = text_styles.main(getArenaFullName(mapID))
    winsEfficiency = mapInfo.wins / float(mapInfo.battlesCount) * 100
    winsEfficiencyStr = BigWorld.wg_getNiceNumberFormat(winsEfficiency) + '%'
    return {'label': text_styles.standard(label + ' ' + mapName),
     'value': text_styles.stats(winsEfficiencyStr)}
