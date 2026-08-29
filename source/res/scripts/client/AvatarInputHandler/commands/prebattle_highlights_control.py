# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/prebattle_highlights_control.py
from __future__ import absolute_import
import BigWorld
import CommandMapping
import BattleReplay
import Keys
import VOIP
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from helpers import dependency
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.battle_control import event_dispatcher as gui_event_dispatcher, avatar_getter
from skeletons.gui.battle_session import IBattleSessionProvider

class PrebattleHighlightsCommandsSetup(InputHandlerCommand):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        pbhCtrl = self.guiSessionProvider.dynamic.prebattleHighlightsController
        pbhShowing = pbhCtrl is not None and pbhCtrl.displayingHighlights
        if not pbhShowing or key in (Keys.KEY_ESCAPE, Keys.KEY_SYSRQ):
            return False
        cmdMap = CommandMapping.g_instance
        arena = avatar_getter.getArena()
        arenaBonusType = None if not arena else arena.bonusType
        player = BigWorld.player()
        isBR = player is not None and player.hasBonusCap(_CAPS.BATTLEROYALE)
        isComp7 = player is not None and player.hasBonusCap(_CAPS.COMP7)
        if not isComp7 and not isBR and cmdMap.isFired(CommandMapping.CMD_VOICECHAT_ENABLE, key) and not isDown:
            if player.isPlayerInSquad() and not BattleReplay.isPlaying():
                if VOIP.getVOIPManager().isVoiceSupported():
                    gui_event_dispatcher.toggleVoipChannelEnabled(arenaBonusType)
            return True
        elif player is not None and cmdMap.isFired(CommandMapping.CMD_VOICECHAT_MUTE, key):
            player.bwProto.voipController.setMicrophoneMute(not isDown)
            return True
        else:
            return True
