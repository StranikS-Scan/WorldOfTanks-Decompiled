# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableRTSLeaderboard.py
from ClientSelectableObject import ClientSelectableObject
import WWISE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.meta_tab_model import Tabs
from gui.shared.event_dispatcher import showRTSMetaRootWindow
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController

class ClientSelectableRTSLeaderboard(ClientSelectableObject):
    _rtsBattleController = dependency.descriptor(IRTSBattlesController)

    def onEnterWorld(self, prereqs):
        super(ClientSelectableRTSLeaderboard, self).onEnterWorld(prereqs)
        self._rtsBattleController.onIsPrbActive += self.__onIsRTSActive
        self.__onIsRTSActive(self._rtsBattleController.isPrbActive())

    def onLeaveWorld(self):
        self._rtsBattleController.onIsPrbActive -= self.__onIsRTSActive
        super(ClientSelectableRTSLeaderboard, self).onLeaveWorld()

    def onMouseClick(self):
        super(ClientSelectableRTSLeaderboard, self).onMouseClick()
        if self.enabled:
            WWISE.WW_eventGlobal(backport.sound(R.sounds.tabb()))
            showRTSMetaRootWindow(Tabs.LEADERBOARD.value)

    def __onIsRTSActive(self, isActive):
        self.setEnable(isActive)
