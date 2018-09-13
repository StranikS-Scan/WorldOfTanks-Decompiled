# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/HistoricalAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from RegularAchievement import RegularAchievement
from mixins import HasVehiclesList, Quest

class HistoricalAchievement(Quest, HasVehiclesList, RegularAchievement):

    def getVehiclesListTitle(self):
        return 'vehiclesTakePart'

    def _getVehiclesDescrsList(self):
        vehsList = []
        try:
            from gui.shared import g_eventsCache
            for qIDs in self.__getQuestByDossierRecord(self._name).getChildren().itervalues():
                for qID in qIDs:
                    counterQuest = g_eventsCache.getQuests().get(qID)
                    histBattleCond = counterQuest.preBattleCond.getConditions().find('historicalBattleIDs')
                    allVehsCompDescrs = set()
                    for hID in histBattleCond._battlesIDs:
                        hb = g_eventsCache.getHistoricalBattles().get(hID)
                        if hb is not None:
                            allVehsCompDescrs.update(hb.getVehiclesData().keys())

                    vehsList = filter(lambda intCD: not counterQuest.isCompletedByGroup(intCD), allVehsCompDescrs)
                    break

        except Exception:
            pass

        return vehsList

    @classmethod
    def __getQuestByDossierRecord(cls, name):
        from gui.shared import g_eventsCache
        for qID, records in g_eventsCache.getQuestsDossierBonuses().iteritems():
            if (_AB.UNIQUE, name) in records:
                return g_eventsCache.getQuests().get(qID)

        return None
