# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/battle_buff_hint.py
from halloween.gui.Scaleform.daapi.view.battle.battle_hint import BattleHint

class BattleBuffHint(BattleHint):

    def _makeVO(self, hint, data):
        vo = hint.makeVO(data)
        param = data.get('param1', None)
        if param:
            vo['timer'] = float(param)
        return vo
