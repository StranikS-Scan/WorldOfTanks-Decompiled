# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/hangar_battle_royale_results.py
import GUI
from gui.Scaleform.daapi.view.meta.HangarBattleRoyaleResultsMeta import HangarBattleRoyaleResultsMeta
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.game_control.br_battle_sounds import BREvents
from gui.server_events import battle_royale_formatters
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from soft_exception import SoftException
from gui.sounds.ambients import BattleResultsEnv
from gui.shared import event_dispatcher
from skeletons.gui.game_control import IBattleRoyaleController

class HangarBattleRoyaleResults(HangarBattleRoyaleResultsMeta):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __brController = dependency.descriptor(IBattleRoyaleController)
    __sound_env__ = BattleResultsEnv

    def __init__(self, ctx, *args, **kwargs):
        super(HangarBattleRoyaleResults, self).__init__(*args, **kwargs)
        self.__blur = GUI.WGUIBackgroundBlur()
        if not ctx or not ctx.get('arenaUniqueID'):
            raise SoftException('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx.get('arenaUniqueID')

    def _populate(self):
        super(HangarBattleRoyaleResults, self)._populate()
        BREvents.playSound(BREvents.BATTLE_SUMMARY_SHOW)
        self.__brController.voiceoverController.setBattleResultsShown(True)
        self.__blur.enable = True
        if self.__battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setTabInfo()

    def _dispose(self):
        self.__brController.voiceoverController.setBattleResultsShown(False)
        self.__blur.enable = False
        super(HangarBattleRoyaleResults, self)._dispose()

    def onClose(self):
        self.destroy()
        event_dispatcher.showHangar()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == BATTLEROYALE_ALIASES.BATTLE_ROYALE_SUMMARY_RESULTS_CMP:
            if self.__battleResults.areResultsPosted(self.__arenaUniqueID):
                battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)
                data = battle_royale_formatters.PostBattleRoyaleSummaryFormatter(battleResultsVO).getInfo()
                viewPy.setData(data)
        if alias == BATTLEROYALE_ALIASES.BATTLE_ROYALE_SCORE_RESULTS_CMP:
            if self.__battleResults.areResultsPosted(self.__arenaUniqueID):
                battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)
                data = battle_royale_formatters.PostBattleRoyaleScoreFormatter(battleResultsVO).getInfo()
                viewPy.setData(data)
        if alias == BATTLEROYALE_ALIASES.BATTLE_ROYALE_RESULTS_WIDGET:
            battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)
            data = battle_royale_formatters.PostBattleWidgetFormatter(battleResultsVO).getInfo()
            viewPy.update(**data)

    def __setTabInfo(self):
        battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)
        if battleResultsVO:
            self.as_setDataS({'viewTabBar': battleResultsVO.get('tabInfo', tuple())})
