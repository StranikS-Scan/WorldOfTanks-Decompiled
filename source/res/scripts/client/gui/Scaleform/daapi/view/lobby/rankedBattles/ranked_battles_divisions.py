# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_divisions.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_FIRST_ENTRY_BY_DIVISION_ID
from gui.impl import backport
from gui.impl.gen import R
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RankedBattlesDivisionsViewMeta import RankedBattlesDivisionsViewMeta
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.ranked_builders import divisions_vos
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesDivisionsView(RankedBattlesDivisionsViewMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__selectedDivisionIdx',)

    def __init__(self):
        super(RankedBattlesDivisionsView, self).__init__()
        self.__selectedDivisionIdx = None
        return

    def onDivisionChanged(self, index):
        self.__selectedDivisionIdx = index
        self.__updateSounds()
        self.__onRankedUpdate()

    def reset(self):
        self.__setDivisionHeader()
        self.__onRankedUpdate()

    def _populate(self):
        super(RankedBattlesDivisionsView, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.__rankedController.onUpdated += self.__onRankedUpdate
        self.__rankedController.onUpdated += self.__setDivisionHeader
        isFirstEntryMap = AccountSettings.getSettings(IS_FIRST_ENTRY_BY_DIVISION_ID)
        divisionID = self.__rankedController.getCurrentDivision().getID()
        isFirstEntry = isFirstEntryMap.get(divisionID, True)
        if isFirstEntry:
            isFirstEntryMap[divisionID] = False
            AccountSettings.setSettings(IS_FIRST_ENTRY_BY_DIVISION_ID, isFirstEntryMap)
        self.__setDivisionHeader(isFirstEntry)
        self.__onRankedUpdate()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__rankedController.onUpdated -= self.__setDivisionHeader
        self.__rankedController.onUpdated -= self.__onRankedUpdate
        super(RankedBattlesDivisionsView, self)._dispose()

    def __getSelectedDivision(self):
        return self.__rankedController.getDivisions()[self.__selectedDivisionIdx]

    def __onRankedUpdate(self):
        self.__setDivisionStats()
        self.__setBonusBattlesCount()
        self.__setRankedData()
        self.__setDivisionStatus()

    def __dossierUpdateCallBack(self, *args):
        self.__setDivisionStats()

    def __setBonusBattlesCount(self):
        selectedDivision = self.__getSelectedDivision()
        bonusCountLabel = None
        if selectedDivision.isUnlocked() and not selectedDivision.isCompleted():
            bonusCountLabel = ranked_helpers.getBonusBattlesLabel(self.__rankedController.getStatsComposer().bonusBattlesCount)
        self.as_setBonusBattlesLabelS(bonusCountLabel)
        return

    def __getDivisionsData(self):
        data = []
        currentDivisionIdx = 0
        for division in self.__rankedController.getDivisions():
            data.append(divisions_vos.getDivisionVO(division))
            if division.isCurrent():
                currentDivisionIdx = division.getID()

        return (data, currentDivisionIdx)

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
        return {'blocks': [ divisions_vos.getRankVO(rank) for rank in ranks ],
         'isLocked': not self.__getSelectedDivision().isUnlocked()}

    def __setDivisionHeader(self, isFirstEntry=False):
        divisions, newSelectedDivisionIdx = self.__getDivisionsData()
        if self.__selectedDivisionIdx != newSelectedDivisionIdx:
            self.__selectedDivisionIdx = newSelectedDivisionIdx
            self.as_setDataS({'isFirstEnter': isFirstEntry,
             'divisions': divisions})

    def __updateSounds(self):
        selectedDivision = self.__getSelectedDivision()
        soundManager = self.__rankedController.getSoundManager()
        if selectedDivision.isUnlocked():
            soundManager.setProgressSound(selectedDivision.getUserID())
        else:
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID(), isLoud=False)
