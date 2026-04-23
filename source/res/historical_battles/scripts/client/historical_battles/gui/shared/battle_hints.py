# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/battle_hints.py
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintsController
from gui.shared.battle_hints import makeHintsData, BattleHintData

class HBBattleHintData(BattleHintData):

    def makeVO(self, data=None):
        vo = super(HBBattleHintData, self).makeVO(data)
        battleHints = R.images.historical_battles.gui.maps.icons.dyn('battleHints')
        if battleHints:
            vo.update({'iconSource': backport.image(battleHints.event.dyn(self.iconPath)()) if self.iconPath else None,
             'iconSourceBlind': backport.image(battleHints.event.dyn(self.blindIconPath)()) if self.blindIconPath else None})
        return vo


def createBattleHintsController():
    return BattleHintsController(makeHintsData(HBBattleHintData))
