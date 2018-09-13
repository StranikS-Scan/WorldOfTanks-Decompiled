# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortClanStatisticsWindow.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortClanStatisticsWindowMeta import FortClanStatisticsWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.ClanCache import g_clanCache
from helpers import i18n

class FortClanStatisticsWindow(AbstractWindowView, View, FortClanStatisticsWindowMeta, FortViewHelper, AppRef):

    def __init__(self):
        super(FortClanStatisticsWindow, self).__init__()

    def _populate(self):
        super(FortClanStatisticsWindow, self)._populate()
        self.startFortListening()
        self.as_setDataS(self.getData())

    def _dispose(self):
        self.stopFortListening()
        super(FortClanStatisticsWindow, self)._dispose()

    def onDossierChanged(self, compDossierDescr):
        self.as_setDataS(self.getData())

    def getData(self):
        ms = i18n.makeString
        dossier = self.fortCtrl.getFort().getFortDossier()
        sortiesStats = dossier.getSortiesStats()
        totalRes = sortiesStats.getLoot()
        battlesCount = sortiesStats.getBattlesCount()
        winsCount = sortiesStats.getWinsCount()
        losesCount = sortiesStats.getLossesCount()
        drawsCount = sortiesStats.getDrawsCount()
        winsEff = sortiesStats.getWinsEfficiency()
        avgLoot = sortiesStats.getAvgLoot()
        winsPercent = '--'
        winsPercentEnabled = False
        if winsEff is not None:
            winsPercent = BigWorld.wg_getNiceNumberFormat(winsEff * 100) + '%'
            winsPercentEnabled = True
        avgDefRes = '--'
        avgDefResEnabled = False
        if avgLoot is not None:
            avgDefRes = BigWorld.wg_getNiceNumberFormat(avgLoot)
            avgDefResEnabled = True
        defresValueStr = str(BigWorld.wg_getIntegralFormat(totalRes)) + ' '
        formattedDefresValue = fort_text.concatStyles(((fort_text.PURPLE_TEXT, defresValueStr), (fort_text.NUT_ICON,)))
        data = {'clanName': g_clanCache.clanTag,
         'sortieBattlesCount': {'value': BigWorld.wg_getIntegralFormat(battlesCount),
                                'icon': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_BATTLES40X32,
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_LABEL),
                                'ttHeader': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP_HEADER),
                                'ttBody': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLESCOUNT_TOOLTIP_BODY) % {'wins': BigWorld.wg_getIntegralFormat(winsCount),
                                           'defeats': BigWorld.wg_getIntegralFormat(losesCount),
                                           'draws': BigWorld.wg_getIntegralFormat(drawsCount)}},
         'sortieWins': {'value': winsPercent,
                        'icon': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINS40X32,
                        'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_LABEL),
                        'ttHeader': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP_HEADER),
                        'ttBody': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_WINS_TOOLTIP_BODY),
                        'enabled': winsPercentEnabled},
         'sortieAvgDefres': {'value': avgDefRes,
                             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_AVGDEFES40X32,
                             'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_LABEL),
                             'ttHeader': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP_HEADER),
                             'ttBody': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_AVGDEFRES_TOOLTIP_BODY),
                             'enabled': avgDefResEnabled},
         'sortieBattlesStats': [{'value': BigWorld.wg_getIntegralFormat(sortiesStats.getMiddleBattlesCount()),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_MIDDLEBATTLESCOUNT_LABEL)}, {'value': BigWorld.wg_getIntegralFormat(sortiesStats.getChampionBattlesCount()),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_CHAMPIONBATTLESCOUNT_LABEL)}, {'value': BigWorld.wg_getIntegralFormat(sortiesStats.getAbsoluteBattlesCount()),
                                 'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_BATTLES_ABSOLUTEBATTLESCOUNT_LABEL)}],
         'sortieDefresStats': [{'value': formattedDefresValue,
                                'label': ms(FORTIFICATIONS.CLANSTATS_PARAMS_SORTIE_DEFRES_LOOTINSORTIES_LABEL)}]}
        return data

    def onWindowClose(self):
        self.destroy()
