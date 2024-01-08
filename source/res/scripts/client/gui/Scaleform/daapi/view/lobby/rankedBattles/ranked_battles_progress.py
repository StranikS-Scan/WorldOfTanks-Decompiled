# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_progress.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_FIRST_ENTRY_BY_DIVISION_ID
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.Scaleform.daapi.view.meta.RankedBattlesDivisionProgressMeta import RankedBattlesDivisionProgressMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.ranked_builders import divisions_vos
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesProgress(RankedBattlesDivisionProgressMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__selectedDivisionIdx',)

    def __init__(self):
        super(RankedBattlesProgress, self).__init__()
        self.__selectedDivisionIdx = None
        return

    def selectDivision(self, index):
        self.__selectedDivisionIdx = index
        self.__onRankedUpdate()

    def reset(self):
        self.__onRankedUpdate()

    def _populate(self):
        super(RankedBattlesProgress, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.__rankedController.onUpdated += self.__onRankedUpdate

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__rankedController.onUpdated -= self.__onRankedUpdate
        super(RankedBattlesProgress, self)._dispose()

    def __getSelectedDivision(self):
        return self.__rankedController.getDivisions()[self.__selectedDivisionIdx]

    def __onRankedUpdate(self):
        if self.__selectedDivisionIdx is not None:
            self.__setDivisionStats()
            self.__setBonusBattlesCount()
            self.__setRankedData()
            self.__setDivisionStatus()
        return

    def __dossierUpdateCallBack(self, *args):
        self.__setDivisionStats()

    def __setBonusBattlesCount(self):
        selectedDivision = self.__getSelectedDivision()
        bonusCountLabel = None
        if selectedDivision.isUnlocked() and not selectedDivision.isCompleted():
            bonusCountLabel = ranked_helpers.getBonusBattlesLabel(self.__rankedController.getStatsComposer().bonusBattlesCount)
        self.as_setBonusBattlesLabelS(bonusCountLabel)
        return

    def __setDivisionStats(self):
        statsComposer = self.__rankedController.getStatsComposer()
        seasonEfficiency = statsComposer.currentSeasonEfficiency.efficiency
        divisionEfficiency = statsComposer.getDivisionEfficiencyPercent(self.__selectedDivisionIdx)
        self.as_setStatsDataS(divisions_vos.getDivisionStatsVO(divisionEfficiency, seasonEfficiency))

    def __setRankedData(self):
        self.as_setRankedDataS(self.__buildProgressData())

    def __setDivisionStatus(self):
        title = None
        descr = None
        selectedDivision = self.__getSelectedDivision()
        if not selectedDivision.isUnlocked():
            title = backport.text(R.strings.ranked_battles.division.status.locked())
            descr = backport.text(R.strings.ranked_battles.division.status.locked.description())
        elif selectedDivision.isCompleted():
            title = backport.text(R.strings.ranked_battles.division.status.completed())
            descr = backport.text(R.strings.ranked_battles.division.status.completed.description())
        self.as_setDivisionStatusS(title=title, description=descr)
        return

    def __buildProgressData(self):
        selectedDivisionIDs = self.__getSelectedDivision().getRanksIDs()
        ranksChain = self.__rankedController.getRanksChain(selectedDivisionIDs[0], selectedDivisionIDs[-1])
        ranks = ranksChain[selectedDivisionIDs[0]:selectedDivisionIDs[-1] + 1]
        isFirstEntryMap = AccountSettings.getSettings(IS_FIRST_ENTRY_BY_DIVISION_ID)
        isFirstEntry = isFirstEntryMap.get(self.__selectedDivisionIdx, True)
        if isFirstEntry:
            isFirstEntryMap[self.__selectedDivisionIdx] = False
            AccountSettings.setSettings(IS_FIRST_ENTRY_BY_DIVISION_ID, isFirstEntryMap)
        return {'blocks': [ divisions_vos.getRankVO(rank) for rank in ranks ],
         'isLocked': not self.__getSelectedDivision().isUnlocked(),
         'isFirstEnter': isFirstEntry}
