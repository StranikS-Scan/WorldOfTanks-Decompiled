# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/winner_congrats.py
import BigWorld
from gui.Scaleform.daapi.view.meta.BattleRoyaleWinnerCongratsMeta import BattleRoyaleWinnerCongratsMeta
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleRoyaleWinnerCongrats(BattleRoyaleWinnerCongratsMeta):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(BattleRoyaleWinnerCongrats, self)._populate()
        self.__winnerStpCoins = self.__battleRoyaleController.getStpCoinsPerPlace(1)

    def onBecomeVisible(self):
        self.__setStpCoins()
        BREvents.playSound(BREvents.BATTLE_WIN)

    def __setStpCoins(self):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        stPatrickComp = vehicle.dynamicComponents.get('vehicleBRStPatrickComponent')
        if stPatrickComp:
            brComponent = self.__sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent
            self.as_setStpCoinsS(stPatrickComp.totalCoins, factor=brComponent.stpDailyBonusFactor, placeBonus=self.__winnerStpCoins)
