# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortClanStatisticsWindow.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.daapi.view.meta.FortClanStatisticsWindowMeta import FortClanStatisticsWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import i18n

class FortClanStatisticsWindow(AbstractWindowView, View, FortClanStatisticsWindowMeta, FortViewHelper, AppRef):

    def __init__(self):
        super(FortClanStatisticsWindow, self).__init__()

    def _populate(self):
        super(FortClanStatisticsWindow, self)._populate()
        self.startFortListening()
        if self.fortState.getStateID() == CLIENT_FORT_STATE.HAS_FORT:
            self.as_setDataS(self.getData())

    def onClientStateChanged(self, state):
        self.as_setDataS(self.getData())

    def _dispose(self):
        self.stopFortListening()
        super(FortClanStatisticsWindow, self)._dispose()

    def getData(self):
        data = self.__getSortieData()
        data.update(self.__getPeriodDefenceData())
        return data

    def onDossierChanged(self, compDossierDescr):
        self.as_setDataS(self.getData())

    def __getSortieData(self):
        ms = i18n.makeString
        dossier = self.fortCtrl.getFort().getFortDossier()
        sortiesStats = dossier.getSortiesStats()
        totalRes = sortiesStats.getLoot()
        defresValueStr = str(BigWorld.wg_getIntegralFormat(totalRes)) + ' '
        formattedDefresValue = fort_text.concatStyles(((fort_text.PURPLE_TEXT, defresValueStr), (fort_text.NUT_ICON,)))
        middleBattlesCount = BigWorld.wg_getIntegralFormat(sortiesStats.getMiddleBattlesCount())
        championshipBattlesCount = BigWorld.wg_getIntegralFormat(sortiesStats.getChampionBattlesCount())
        absoluteBattlesCount = BigWorld.wg_getIntegralFormat(sortiesStats.getAbsoluteBattlesCount())
        data = {'clanName': g_clanCache.clanTag,
         'sortieBattlesCount': ProfileUtils.getTotalBattlesHeaderParam(sortiesStats, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP),
         'sortieWins': ProfileUtils.packLditItemData(ProfileUtils.getFormattedWinsEfficiency(sortiesStats), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP, 'wins40x32.png'),
         'sortieAvgDefres': ProfileUtils.packLditItemData(ProfileUtils.formatEfficiency(sortiesStats.getBattlesCount(), sortiesStats.getAvgLoot), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP, 'avgDefes40x32.png'),
         'sortieBattlesStats': [{'value': self.__getMiddleTitleText(middleBattlesCount),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_MIDDLEBATTLESCOUNT_LABEL)}, {'value': self.__getMiddleTitleText(championshipBattlesCount),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_CHAMPIONBATTLESCOUNT_LABEL)}, {'value': self.__getMiddleTitleText(absoluteBattlesCount),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_ABSOLUTEBATTLESCOUNT_LABEL)}],
         'sortieDefresStats': [{'value': formattedDefresValue,
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_DEFRES_LOOTINSORTIES_LABEL)}]}
        return data

    def __getMiddleTitleText(self, msg):
        return fort_text.getText(fort_text.MIDDLE_TITLE, msg)

    def __getPeriodDefenceData(self):
        dossier = self.fortCtrl.getFort().getFortDossier()
        stats = dossier.getBattlesStats()
        ms = i18n.makeString
        resourceLossCount = stats.getResourceLossCount()
        combatCount = stats.getCombatCount()
        combatWinsCount = stats.getCombatWins()
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
        data = {'periodBattles': ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(combatCount), FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLESCOUNT_LABEL, TOOLTIPS.FORTIFICATION_CLANSTATS_PERIODDEFENCE_BATTLES_BATTLESCOUNT, 'battles40x32.png', {'tooltipData': ProfileUtils.createToolTipData([BigWorld.wg_getIntegralFormat(combatWinsCount), BigWorld.wg_getIntegralFormat(combatCount - combatWinsCount)])}),
         'periodWins': ProfileUtils.packLditItemData(ProfileUtils.getFormattedWinsEfficiency(stats), FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_LABEL, FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP, 'wins40x32.png'),
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
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_PERIODDEFENCE_BATTLES_PROFIT_LABEL)}]}
        return data

    def __getFormattedDefresValue(self, value):
        return fort_text.concatStyles(((fort_text.PURPLE_TEXT, ProfileUtils.getAvailableValueStr(value) + ' '), (fort_text.NUT_ICON,)))

    def onWindowClose(self):
        self.destroy()
