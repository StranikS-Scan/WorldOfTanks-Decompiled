# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/postmortem_panel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.FDPostmortemPanelMeta import FDPostmortemPanelMeta
from gui.impl import backport
from gui.impl.gen import R

class HWPostmortemPanel(FDPostmortemPanelMeta):

    def _populate(self):
        super(HWPostmortemPanel, self)._populate()
        self.as_setHintTitleS(backport.text(R.strings.hw_ingame_help.postmortem_panel.do_not_leave_the_game()))

    def _addGameListeners(self):
        super(HWPostmortemPanel, self)._addGameListeners()
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl:
            respawnCtrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdated

    def _removeGameListeners(self):
        super(HWPostmortemPanel, self)._removeGameListeners()
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl:
            respawnCtrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdated

    def __onRespawnInfoUpdated(self, respawnInfo):
        timeToRespawn = int(round(respawnInfo.autoRespawnTime - BigWorld.serverTime()))
        self.as_setTimerS(timeToRespawn)
