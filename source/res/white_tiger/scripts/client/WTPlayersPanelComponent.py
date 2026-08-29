# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTPlayersPanelComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
import BattleReplay
from ReplayEvents import g_replayEvents
from gui.shared.players_panel_items import getGuiItemType, isProcessReplayNeeded
from skeletons.gui.battle_session import IBattleSessionProvider

class WTPlayersPanelComponent(DynamicScriptComponent):
    __PLAYERS_PANEL_STYLE = 'CAMP'

    def __init__(self):
        super(WTPlayersPanelComponent, self).__init__()
        self.__guiComponent = None
        return

    def onDestroy(self):
        self.__hidePanel()
        super(WTPlayersPanelComponent, self).onDestroy()

    @property
    def uiCtrl(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        return sessionProvider.dynamic.playersPanel

    @property
    def guiComponent(self):
        return self.__guiComponent

    def _onAvatarReady(self):
        guiComponent = getGuiItemType(self.__PLAYERS_PANEL_STYLE)
        if guiComponent is not None and guiComponent.setValuesOnCreate(self.entity):
            self.uiCtrl.show(guiComponent)
        self.__guiComponent = guiComponent
        if BattleReplay.g_replayCtrl.isPlaying and isProcessReplayNeeded(self.__PLAYERS_PANEL_STYLE):
            g_replayEvents.onPause += self.__onReplayUpdate
        return

    def __onReplayUpdate(self, _):
        if self.__guiComponent is not None and self.__guiComponent.setValuesOnCreate(self.entity):
            self.uiCtrl.processReplay(self.__guiComponent)
        return

    def __hidePanel(self):
        if BattleReplay.g_replayCtrl.isPlaying and isProcessReplayNeeded(self.__PLAYERS_PANEL_STYLE):
            g_replayEvents.onPause -= self.__onReplayUpdate
        if self.__guiComponent is not None and self.__guiComponent.setValuesOnDestroy(self.entity):
            self.uiCtrl.hide(self.__guiComponent)
        self.__guiComponent = None
        return
