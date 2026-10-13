# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/respawn_view.py
from __future__ import absolute_import
import logging
from fort_rush.gui.battle_control.controllers.respawn_ctrl import ISpawnListener
from fort_rush.gui.scaleform.daapi.view.meta.FortRushRespawnViewMeta import FortRushRespawnViewMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class FortRushRespawnView(FortRushRespawnViewMeta, ISpawnListener):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FortRushRespawnView, self).__init__()
        self.__delayCallbackID = None
        return

    def onRespawnPointClick(self, id):
        _logger.debug('[FORT_RUSH][RESPAWN][VIEW] onRespawnPointClick: %s', id)
        if self._respawnCtrl and id:
            self._respawnCtrl.chooseSpawnKeyPoint(id)

    def showSpawnPoints(self):
        _logger.debug('[FORT_RUSH][RESPAWN][VIEW] showSpawnPoints')

    @property
    def _respawnCtrl(self):
        from fort_rush.gui.fort_rush_gui_constants import BATTLE_CTRL_ID
        return self._guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
