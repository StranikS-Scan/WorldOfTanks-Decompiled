# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PlayersPanelComponent.py
from gui.shared.players_panel_items import getGuiItemType, isProcessReplayNeeded
from helpers import dependency
from script_component.ScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
import BattleReplay
from ReplayEvents import g_replayEvents

class PlayersPanelComponent(DynamicScriptComponent):

    def __init__(self):
        self.__guiComponent = None
        super(PlayersPanelComponent, self).__init__()
        return

    def onAvatarReady(self):
        guiComponent = getGuiItemType(self.style)
        if guiComponent is not None and guiComponent.setValuesOnCreate(self.entity):
            self.uiCtrl.show(guiComponent)
        self.__guiComponent = guiComponent
        if BattleReplay.g_replayCtrl.isPlaying and isProcessReplayNeeded(self.style):
            g_replayEvents.onPause += self.__onReplayUpdate
        return

    def onLeaveWorld(self):
        pass

    @property
    def uiCtrl(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        return sessionProvider.dynamic.playersPanel

    @property
    def guiComponent(self):
        return self.__guiComponent

    def onDestroy(self):
        super(PlayersPanelComponent, self).onDestroy()
        if BattleReplay.g_replayCtrl.isPlaying and isProcessReplayNeeded(self.style):
            g_replayEvents.onPause -= self.__onReplayUpdate
        if self.__guiComponent is not None and self.__guiComponent.setValuesOnDestroy(self.entity):
            self.uiCtrl.hide(self.__guiComponent)
        self.__guiComponent = None
        return

    def __onReplayUpdate(self, _):
        if self.__guiComponent is not None and self.__guiComponent.setValuesOnCreate(self.entity):
            self.uiCtrl.processReplay(self.__guiComponent)
        return
