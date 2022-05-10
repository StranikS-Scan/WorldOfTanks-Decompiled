# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/battle_royale_prime_time.py
from constants import Configs
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_prime_time import EpicBattlesPrimeTimeView
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_prime_time import EpicBattleServerPresenter
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.impl import backport
from gui.impl.gen import R

class BattleRoyaleServerPresenter(EpicBattleServerPresenter):
    _periodsController = dependency.descriptor(IBattleRoyaleController)

    def _getEndOfCycleTooltipText(self):
        return backport.text(R.strings.battle_royale.primeTime.tooltip.endOfCycleOnThisServer(), server=self.getName())


class BattleRoyalePrimeTimeView(EpicBattlesPrimeTimeView):
    _serverPresenterClass = BattleRoyaleServerPresenter
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)

    def _getController(self):
        return self.__battleRoyale

    def _setHeaderText(self):
        self.as_setHeaderTextS(backport.text(R.strings.epic_battle.primeTime.steelhunter.title()))

    def _setBackground(self):
        self.as_setBackgroundSourceS(backport.image(R.images.gui.maps.icons.battleRoyale.primeTime.prime_time_back_default()))

    def _getTimeText(self, serverInfo):
        if serverInfo:
            serverName = serverInfo.getName()
            timeLeft = serverInfo.getTimeLeft()
        else:
            _, timeLeft, _ = self._getController().getPrimeTimeStatus()
            serverName = ''
        currentSeason = self._getController().getCurrentSeason()
        return backport.text(R.strings.battle_royale.primeTime.tooltip.endOfCycleOnThisServer(), server=serverName) if currentSeason and not timeLeft else super(BattleRoyalePrimeTimeView, self)._getTimeText(serverInfo)

    def _getCycleFinishedOnThisServerText(self, cycleNumber, serverName):
        return backport.text(R.strings.battle_royale.primeTime.status.cycleFinishedOnThisServer(), cycleNo=cycleNumber, server=serverName)

    def _getPrbActionName(self):
        return PREBATTLE_ACTION_NAME.BATTLE_ROYALE

    def _getPrbForcedActionName(self):
        return PREBATTLE_ACTION_NAME.BATTLE_ROYALE

    def _onServerSettingsChange(self, diff):
        if diff.get(Configs.BATTLE_ROYALE_CONFIG.value, {}).get('isEnabled') is False:
            showHangar()
