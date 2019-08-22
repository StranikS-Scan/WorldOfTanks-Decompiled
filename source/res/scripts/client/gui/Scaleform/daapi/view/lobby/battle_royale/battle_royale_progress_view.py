# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_progress_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_FIRST_ENTRY_IN_BATTLE_ROYALE
from gui.Scaleform.daapi.view.meta.BattleRoyaleProgressMeta import BattleRoyaleProgressMeta
from gui.battle_royale.royale_builders import progress_vos
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleProgressView(BattleRoyaleProgressMeta):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)

    def _populate(self):
        super(BattleRoyaleProgressView, self)._populate()
        self.__battleRoyale.onUpdated += self.__onTitlesUpdate
        self.__onTitlesUpdate()

    def _dispose(self):
        self.__battleRoyale.onUpdated -= self.__onTitlesUpdate
        super(BattleRoyaleProgressView, self)._dispose()

    def __onTitlesUpdate(self):
        self.__setBattleRoyaleStats()

    def __setBattleRoyaleStats(self):
        statsComposer = self.__battleRoyale.getStatsComposer()
        isFirstEntry = AccountSettings.getSettings(IS_FIRST_ENTRY_IN_BATTLE_ROYALE)
        if isFirstEntry:
            AccountSettings.setSettings(IS_FIRST_ENTRY_IN_BATTLE_ROYALE, False)
        titles = self.__battleRoyale.getCachedTitlesChain()[1:]
        blocks = [ progress_vos.getTitleVO(title) for title in titles ]
        firstTitleStepsCount = titles[0].getStepsCountToAchieve()
        self.as_setDataS(progress_vos.getProgressStatsVO(statsComposer, isFirstEntry, blocks, firstTitleStepsCount))
