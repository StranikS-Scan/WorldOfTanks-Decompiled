# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/wt_battle_sounds_player.py
import SoundGroups
from gui.battle_control.controllers.battle_hints_ctrl import IBattleHintView

class BattleHintSoundPlayer(IBattleHintView):

    def showHint(self, hint, data):
        super(BattleHintSoundPlayer, self).showHint(hint, data)
        hintName = hint.name
        if hintName == 'wtGeneratorSpawned_hunters' or hintName == 'wtGeneratorSpawned_boss':
            SoundGroups.g_instance.playSound2D('ev_white_tiger_widget_icon_generator_03')

    def getAlias(self):
        pass
