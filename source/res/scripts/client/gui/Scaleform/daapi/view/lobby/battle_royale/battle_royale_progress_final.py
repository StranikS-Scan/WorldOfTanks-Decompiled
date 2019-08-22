# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_progress_final.py
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from gui.Scaleform.daapi.view.meta.BattleRoyaleProgressFinalMeta import BattleRoyaleProgressFinalMeta
from gui.battle_royale.royale_builders import progress_final_vos
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleProgressFinal(BattleRoyaleProgressFinalMeta):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __slots__ = ()

    def _populate(self):
        super(BattleRoyaleProgressFinal, self)._populate()
        self.__battleRoyaleController.onUpdated += self.__onRoyaleUpdate
        self.__setStatsData()
        self.__setProgressData()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__battleRoyaleController.onUpdated -= self.__onRoyaleUpdate
        super(BattleRoyaleProgressFinal, self)._dispose()

    def __onRoyaleUpdate(self):
        self.__setStatsData()
        self.__setProgressData()

    def __setProgressData(self):
        maxTitle = self.__battleRoyaleController.getTitle(self.__battleRoyaleController.getMaxPossibleTitle())
        self.as_setDataS(progress_final_vos.getDataVO(maxTitle))

    def __setStatsData(self):
        statsComposer = self.__battleRoyaleController.getStatsComposer()
        self.as_setStatsDataS(progress_final_vos.getStatsVO(statsComposer))
