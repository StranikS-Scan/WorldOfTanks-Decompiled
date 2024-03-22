# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/winner_congrats.py
from gui.Scaleform.daapi.view.meta.BattleRoyaleWinnerCongratsMeta import BattleRoyaleWinnerCongratsMeta
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents

class BattleRoyaleWinnerCongrats(BattleRoyaleWinnerCongratsMeta):

    def playWinSound(self):
        BREvents.playSound(BREvents.BATTLE_WIN)
