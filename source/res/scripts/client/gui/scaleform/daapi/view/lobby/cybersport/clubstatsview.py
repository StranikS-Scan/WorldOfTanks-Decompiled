# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubStatsView.py
import itertools
import BigWorld
from account_helpers import getPlayerDatabaseID
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubPage
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.meta.StaticFormationStatsViewMeta import StaticFormationStatsViewMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items.dossier import dumpDossier
STATS_GROUP_WIDTH = 286

class ClubStatsView(StaticFormationStatsViewMeta, ClubPage):

    def __init__(self):
        super(ClubStatsView, self).__init__()
        self._clubDbID = None
        self._owner = None
        return

    def onClubUpdated(self, club):
        if club is not None:
            self._initializeGui(club)
        return

    def onClubDossierChanged(self, seasonDossier, totalDossier):
        club = self.clubsCtrl.getClub(self._clubDbID)
        self.__setData(club)

    def _populate(self):
        super(ClubStatsView, self)._populate()

    def _dispose(self):
        super(ClubStatsView, self)._dispose()
        self.clearClub()

    def _initializeGui(self, club):
        self.__setData(club)

    def __setData(self, club):
        commonDossier = club.getTotalDossier()
        totalStats = commonDossier.getTotalStats()
        battlesNumData, winsPercentData, winsByCaptureData, techDefeatsData = self.__makeStats(totalStats)
        leftStats, centerStats, rightStats = self.__makeAdditionalStats(totalStats)
        self.as_setDataS({'awardsText': text_styles.middleTitle(CYBERSPORT.STATICFORMATIONSTATSVIEW_AWARDS),
         'noAwardsText': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_NOAWARDS),
         'battlesNumData': battlesNumData,
         'winsPercentData': winsPercentData,
         'winsByCaptureData': winsByCaptureData,
         'techDefeatsData': techDefeatsData,
         'leftStats': leftStats,
         'centerStats': centerStats,
         'rightStats': rightStats,
         'achievements': self.__makeAchievements(commonDossier, club),
         'statsGroupWidth': STATS_GROUP_WIDTH})

    def __makeStats(self, totalStats):
        battlesNumData = {'text': BigWorld.wg_getNiceNumberFormat(totalStats.getBattlesCount()),
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

    def __makeAdditionalStats(self, totalStats):
        killedTanks = totalStats.getKilledVehiclesCount()
        lostTanks = totalStats.getLostVehiclesCount()
        killedLostRatio = totalStats.getKilledLostVehiclesRatio() or 0
        dmgInflicted = totalStats.getDamageDealt()
        dmgReceived = totalStats.getDamageReceived()
        damageEfficiency = totalStats.getDamageEfficiency() or 0
        avgAttackDmg = totalStats.getAttackDamageEfficiency() or 0
        avgDefenceDmg = totalStats.getDefenceDamageEfficiency() or 0
        leftStats = [{'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_KILLED),
          'value': text_styles.stats(BigWorld.wg_getIntegralFormat(killedTanks))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_LOST),
          'value': text_styles.stats(BigWorld.wg_getIntegralFormat(lostTanks))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_KILLEDLOSTRATIO),
          'value': text_styles.stats(BigWorld.wg_getNiceNumberFormat(killedLostRatio))}]
        centerStats = [{'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DMGINFLICTED),
          'value': text_styles.stats(BigWorld.wg_getIntegralFormat(dmgInflicted))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DMGRECEIVED),
          'value': text_styles.stats(BigWorld.wg_getIntegralFormat(dmgReceived))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DMGRATIO),
          'value': text_styles.stats(BigWorld.wg_getNiceNumberFormat(damageEfficiency))}]
        rightStats = [{'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_ATTACKDAMAGEEFFICIENCY),
          'value': text_styles.stats(BigWorld.wg_getIntegralFormat(avgAttackDmg))}, {'label': text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_ADDSTATS_DEFENCEDAMAGEEFFICIENCY),
          'value': text_styles.stats(BigWorld.wg_getIntegralFormat(avgDefenceDmg))}]
        return (leftStats, centerStats, rightStats)

    def __makeAchievements(self, dossier, club):
        achievements = dossier.getTotalStats().getAchievements()
        mergedList = list(itertools.chain(*achievements))
        isForClubMember = club.getMember(getPlayerDatabaseID()) is not None
        return AchievementsUtils.packAchievementList(mergedList, dossier.getDossierType(), dumpDossier(dossier), isForClubMember, True)
