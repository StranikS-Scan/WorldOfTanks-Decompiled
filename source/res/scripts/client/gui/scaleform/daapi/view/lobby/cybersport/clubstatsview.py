# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubStatsView.py
import itertools
from collections import namedtuple
from operator import itemgetter, attrgetter
import BigWorld
from adisp import process
from account_helpers import getAccountDatabaseID
from helpers.i18n import makeString as _ms
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from shared_utils import first
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.meta.StaticFormationStatsViewMeta import StaticFormationStatsViewMeta
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubPage
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items.dossier import dumpDossier
_STATS_GROUP_WIDTH = 286
_SeasonItem = namedtuple('_SeasonItem', ['seasonID', 'dossier', 'name'])

def _makeAchievements(dossier, club):
    achievements = dossier.getTotalStats().getAchievements()
    mergedList = list(itertools.chain(*achievements))
    isForClubMember = club.hasMember(getAccountDatabaseID())
    return AchievementsUtils.packAchievementList(mergedList, dossier.getDossierType(), dumpDossier(dossier), isForClubMember, True)


def _getKilledTanksStats(stats):
    killedTanks = stats.getKilledVehiclesCount()
    lostTanks = stats.getLostVehiclesCount()
    killedLostRatio = stats.getKilledLostVehiclesRatio() or 0
    return [{'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_KILLED),
      'value': text_styles.stats(BigWorld.wg_getIntegralFormat(killedTanks))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_LOST),
      'value': text_styles.stats(BigWorld.wg_getIntegralFormat(lostTanks))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_KILLEDLOSTRATIO),
      'value': text_styles.stats(BigWorld.wg_getNiceNumberFormat(killedLostRatio))}]


def _getDamageStats(totalStats):
    dmgInflicted = totalStats.getDamageDealt()
    dmgReceived = totalStats.getDamageReceived()
    damageEfficiency = totalStats.getDamageEfficiency() or 0
    return [{'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DMGINFLICTED),
      'value': text_styles.stats(BigWorld.wg_getIntegralFormat(dmgInflicted))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DMGRECEIVED),
      'value': text_styles.stats(BigWorld.wg_getIntegralFormat(dmgReceived))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DMGRATIO),
      'value': text_styles.stats(BigWorld.wg_getNiceNumberFormat(damageEfficiency))}]


def _getAvgStats(totalStats):
    avgAttackDmg = totalStats.getAttackDamageEfficiency() or 0
    avgDefenceDmg = totalStats.getDefenceDamageEfficiency() or 0
    return [{'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_ATTACKDAMAGEEFFICIENCY),
      'value': text_styles.stats(BigWorld.wg_getIntegralFormat(avgAttackDmg))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DEFENCEDAMAGEEFFICIENCY),
      'value': text_styles.stats(BigWorld.wg_getIntegralFormat(avgDefenceDmg))}]


class ClubStatsView(StaticFormationStatsViewMeta, ClubPage):

    def __init__(self):
        super(ClubStatsView, self).__init__()
        self._clubDbID = None
        self._owner = None
        self._seasons = []
        return

    def onClubUpdated(self, club):
        if club is not None:
            self.__updateData(club)
        return

    def onCompletedSeasonsInfoChanged(self):
        self._seasons = []
        club = self.clubsCtrl.getClub(self._clubDbID)
        self._initializeGui(club)

    def onClubDossierChanged(self, seasonDossier, totalDossier):
        self.__updateData(self.clubsCtrl.getClub(self._clubDbID))

    def selectSeason(self, menuIdx):
        try:
            self.__setStats(self._seasons[menuIdx].dossier.getTotalStats())
        except IndexError:
            LOG_ERROR('There is error while getting club dossier by index', menuIdx)
            LOG_CURRENT_EXCEPTION()

    def _dispose(self):
        super(ClubStatsView, self)._dispose()
        self.clearClub()

    def _initializeGui(self, club):
        self._seasons.insert(0, _SeasonItem(-1, club.getTotalDossier(), _ms(CYBERSPORT.STATICFORMATIONSTATSVIEW_SEASONFILTER_ALL)))
        self._seasons.insert(1, _SeasonItem(-1, club.getSeasonDossier(), _ms(CYBERSPORT.STATICFORMATIONSTATSVIEW_SEASONFILTER_CURRENT)))
        self.__updateData(club)
        self._requestClubSeasons()

    @process
    def _requestClubSeasons(self):
        seasons = yield self.clubsCtrl.requestClubSeasons(self._clubDbID)
        if len(seasons):
            for sID, dossier in sorted(seasons.iteritems(), key=itemgetter(0), reverse=True):
                if dossier.getTotalStats().getBattlesCount():
                    seasonUserName = self.clubsCtrl.getSeasonUserName(sID)
                    if seasonUserName:
                        self._seasons.append(_SeasonItem(sID, dossier, seasonUserName))

            self.__updateData(self.clubsCtrl.getClub(self._clubDbID))

    def __updateData(self, club):
        seasonFilters = []
        seasonFilters.extend(map(attrgetter('name'), self._seasons))
        achievements = _makeAchievements(club.getTotalDossier(), club)
        self.as_setDataS({'awardsText': text_styles.highTitle(CYBERSPORT.STATICFORMATIONSTATSVIEW_AWARDS),
         'noAwardsText': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_NOAWARDS),
         'achievements': achievements,
         'statsGroupWidth': _STATS_GROUP_WIDTH,
         'seasonFilterName': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_SEASONFILTER),
         'selectedSeason': 0,
         'seasonFilters': seasonFilters,
         'seasonFilterEnable': len(seasonFilters) > 1,
         'noAwards': len(achievements) < 1})
        self.__setStats(first(self._seasons).dossier.getTotalStats())

    def __setStats(self, stats):
        if stats.getWinsEfficiency():
            winsEfficiency = stats.getWinsEfficiency() * 100
        else:
            winsEfficiency = 0
        self.as_setStatsS({'battlesNumData': {'text': BigWorld.wg_getNiceNumberFormat(stats.getBattlesCount()),
                            'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_BATTLES),
                            'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_BATTLES40X32,
                            'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_BATTLES},
         'winsPercentData': {'text': BigWorld.wg_getNiceNumberFormat(winsEfficiency) + '%',
                             'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_WINSPERCENT),
                             'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINS40X32,
                             'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_WINSPERCENT},
         'winsByCaptureData': {'text': BigWorld.wg_getIntegralFormat(stats.getAttackDamageEfficiency() or 0),
                               'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_ATTACKDAMAGEEFFICIENCY),
                               'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_AVGATTACKDMG40X32,
                               'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_WINSBYCAPTURE},
         'techDefeatsData': {'text': BigWorld.wg_getIntegralFormat(stats.getDefenceDamageEfficiency() or 0),
                             'description': _ms(CYBERSPORT.STATICFORMATIONSUMMARYVIEW_STATS_DEFENCEDAMAGEEFFICIENCY),
                             'iconPath': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_AVGDEFENCEDMG40X32,
                             'tooltip': TOOLTIPS.STATICFORMATIONSUMMARYVIEW_STATS_TECHDEFEATS},
         'leftStats': _getKilledTanksStats(stats),
         'centerStats': _getDamageStats(stats),
         'rightStats': _getAvgStats(stats)})
