# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortClanStatisticsData.py
import BigWorld
from Event import Event
from adisp import async
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.formatters import icons, text_styles
from gui.shared.fortifications.fort_helpers import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE

@async
def getDataObject(callback):
    _FortClanStatisticsData(callback)


class _FortClanStatisticsData(FortListener):

    def __init__(self, initSuccessCallback):
        self.__data = {}
        self.listeningToFort = False
        self.__initSuccessCallback = initSuccessCallback
        self.onDataChanged = Event()
        self.startFortListening()
        if self.fortState.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            self.listeningToFort = True
            self.__initSuccessCallback(self)

    def onClientStateChanged(self, state):
        if not self.listeningToFort:
            if state.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
                self.__initSuccessCallback(self)
                self.listeningToFort = True
            else:
                self.stopFortListening()
                self.__initSuccessCallback(None)
        else:
            self.onDataChanged()
        return

    def onDossierChanged(self, _):
        self.onDataChanged()

    def getData(self):
        self.__data.clear()
        self.__updateSortieData()
        self.__updateDefenceData()
        return self.__data

    def __updateSortieData(self):
        ms = i18n.makeString
        dossier = self.fortCtrl.getFort().getFortDossier()
        sortiesStats = dossier.getSortiesStats()
        totalRes = sortiesStats.getLoot()
        defresValueStr = str(BigWorld.wg_getIntegralFormat(totalRes)) + ' '
        formattedDefresValue = ''.join((text_styles.defRes(defresValueStr), icons.nut()))
        middleBattlesCount = BigWorld.wg_getIntegralFormat(sortiesStats.getMiddleBattlesCount())
        championshipBattlesCount = BigWorld.wg_getIntegralFormat(sortiesStats.getChampionBattlesCount())
        absoluteBattlesCount = BigWorld.wg_getIntegralFormat(sortiesStats.getAbsoluteBattlesCount())
        self.__data.update({'clanName': g_clanCache.clanTag,
         'sortieBattlesCount': ProfileUtils.getTotalBattlesHeaderParam(sortiesStats, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP),
         'sortieWins': ProfileUtils.packLditItemData(ProfileUtils.getFormattedWinsEfficiency(sortiesStats), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP, 'wins40x32.png'),
         'sortieAvgDefres': ProfileUtils.packLditItemData(ProfileUtils.formatEfficiency(sortiesStats.getBattlesCount(), sortiesStats.getAvgLoot), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP, 'avgDefes40x32.png'),
         'sortieBattlesStats': [{'value': self.__getMiddleTitleText(middleBattlesCount),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_MIDDLEBATTLESCOUNT_LABEL)}, {'value': self.__getMiddleTitleText(championshipBattlesCount),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_CHAMPIONBATTLESCOUNT_LABEL)}, {'value': self.__getMiddleTitleText(absoluteBattlesCount),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_ABSOLUTEBATTLESCOUNT_LABEL)}],
         'sortieDefresStats': [{'value': formattedDefresValue,
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_DEFRES_LOOTINSORTIES_LABEL)}]})

    def __getMiddleTitleText(self, msg):
        return text_styles.middleTitle(msg)

    def __updateDefenceData(self):
        dossier = self.fortCtrl.getFort().getFortDossier()
        stats = dossier.getBattlesStats()
        ms = i18n.makeString
        resourceLossCount = stats.getResourceLossCount()
        defenceCount = stats.getDefenceCount()
        atackCount = stats.getAttackCount()
        sucessDefenceCount = stats.getSuccessDefenceCount()
        sucessAtackCount = stats.getSuccessAttackCount()
        resourceCaptureCount = stats.getResourceCaptureCount()
        resourcesProvitValue = resourceCaptureCount - resourceLossCount
        resourcesProfitStr = BigWorld.wg_getIntegralFormat(resourcesProvitValue)
        if resourcesProvitValue > 0:
            resourcesProfitStr = '+' + resourcesProfitStr
        attackEfficiencyValue = ProfileUtils.formatEfficiency(atackCount, lambda : float(sucessAtackCount) / atackCount)
        defEfficiencyValue = ProfileUtils.formatEfficiency(defenceCount, lambda : float(sucessDefenceCount) / defenceCount)
        self.__data.update({'periodBattles': ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(stats.getBattlesCount()), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLESCOUNT_LABEL, TOOLTIPS.FORTIFICATION_CLANSTATS_PERIODDEFENCE_BATTLES_BATTLESCOUNT, 'battles40x32.png', ProfileUtils.createToolTipData([BigWorld.wg_getIntegralFormat(stats.getWinsCount()), BigWorld.wg_getIntegralFormat(stats.getLossesCount())])),
         'periodWins': ProfileUtils.packLditItemData(ProfileUtils.getFormattedWinsEfficiency(stats), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_WINS_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_WINS_TOOLTIP, 'wins40x32.png'),
         'periodAvgDefres': ProfileUtils.packLditItemData(ProfileUtils.formatEfficiency(resourceLossCount, lambda : float(resourceCaptureCount) / resourceLossCount), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_AVGDEFRES_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_AVGDEFRES_TOOLTIP, 'defresRatio40x32.png'),
         'periodBattlesStats': [{'value': self.__getMiddleTitleText(BigWorld.wg_getIntegralFormat(stats.getEnemyBaseCaptureCount())),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_COUNTCAPTUREDCOMMANDCENTRES_LABEL)},
                                {'value': self.__getMiddleTitleText(BigWorld.wg_getIntegralFormat(stats.getCaptureEnemyBuildingTotalCount())),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_COUNTPLUNDEREDENEMYBUILDINGS_LABEL)},
                                {'value': self.__getMiddleTitleText(BigWorld.wg_getIntegralFormat(stats.getLossOwnBuildingTotalCount())),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_COUNTPLUNDEREDALLYBUILDINGS_LABEL)},
                                {'value': self.__getMiddleTitleText(attackEfficiencyValue),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_EFFICIENCYOFATTACK),
                                 'ttLabel': TOOLTIPS.FORTIFICATION_CLANSTATS_PERIODDEFENCE_BATTLES_EFFICIENCYOFATTACK,
                                 'ttBodyParams': {'countAtack': BigWorld.wg_getIntegralFormat(sucessAtackCount),
                                                  'countTotalAtack': BigWorld.wg_getIntegralFormat(atackCount)},
                                 'enabled': attackEfficiencyValue != -1},
                                {'value': self.__getMiddleTitleText(defEfficiencyValue),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_EFFICIENCYOFDEFENCE),
                                 'ttLabel': TOOLTIPS.FORTIFICATION_CLANSTATS_PERIODDEFENCE_BATTLES_EFFICIENCYOFDEFENCE,
                                 'ttBodyParams': {'countDefences': BigWorld.wg_getIntegralFormat(sucessDefenceCount),
                                                  'countTotalDefences': BigWorld.wg_getIntegralFormat(defenceCount)},
                                 'enabled': defEfficiencyValue != -1}],
         'periodDefresStats': [{'value': self.__getFormattedDefresValue(BigWorld.wg_getIntegralFormat(resourceCaptureCount)),
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_COUNTPROMRES_LABEL)}, {'value': self.__getFormattedDefresValue(BigWorld.wg_getIntegralFormat(resourceLossCount)),
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_LOSTPROMRES_LABEL)}, {'value': self.__getFormattedDefresValue(resourcesProfitStr),
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_PROFIT_LABEL)}]})

    def __getFormattedDefresValue(self, value):
        return ''.join((text_styles.defRes(ProfileUtils.getAvailableValueStr(value) + ' '), icons.nut()))
