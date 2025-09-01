# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/boss_teleport.py
import typing
import CommandMapping
from gui import g_keyEventHandlers
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerBossTeleportViewMeta import WhiteTigerBossTeleportViewMeta
from white_tiger.gui.white_tiger_gui_constants import BATTLE_CTRL_ID
from white_tiger.skeletons.white_tiger_spawn_listener import ISpawnListener
if typing.TYPE_CHECKING:
    from white_tiger.gui.battle_control.controllers.teleport_spawn_ctrl import TeleportSpawnController

class WhiteTigerBossTeleportView(WhiteTigerBossTeleportViewMeta, ISpawnListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerBossTeleportView, self).__init__()
        self._blur = CachedBlur()
        self._isActive = False

    def showSpawnPoints(self):
        self._blur.enable()
        self._isActive = True

    def closeSpawnPoints(self):
        self._blur.disable()
        self._isActive = False

    def onTeleportPointClick(self, pointGuid):
        self._chooseSpawnPoint(pointGuid)

    def onCancel(self):
        if self._isActive and self._spawnCtrl:
            self._spawnCtrl.cancelEquipment()

    def _populate(self):
        super(WhiteTigerBossTeleportView, self)._populate()
        g_keyEventHandlers.add(self._handleKeyEvent)

    def _dispose(self):
        self._blur.fini()
        g_keyEventHandlers.discard(self._handleKeyEvent)
        super(WhiteTigerBossTeleportView, self)._dispose()

    @property
    def _spawnCtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)

    def _chooseSpawnPoint(self, pointGuid):
        if self._spawnCtrl and pointGuid:
            self._spawnCtrl.chooseSpawnKeyPoint(pointGuid)

    def _handleKeyEvent(self, event):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_AMMO_CHOICE_4, event.key) and event.isKeyDown() and not event.isRepeatedEvent():
            self.onCancel()
