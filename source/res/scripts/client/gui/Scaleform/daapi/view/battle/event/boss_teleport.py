# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/boss_teleport.py
import typing
import CommandMapping
from gui.battle_control.controllers.teleport_spawn_ctrl import ISpawnListener
from gui import g_keyEventHandlers
from gui.Scaleform.daapi.view.meta.EventBossTeleportViewMeta import EventBossTeleportViewMeta
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.teleport_spawn_ctrl import TeleportSpawnController

class EventBossTeleportView(EventBossTeleportViewMeta, ISpawnListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventBossTeleportView, self).__init__()
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
        super(EventBossTeleportView, self)._populate()
        g_keyEventHandlers.add(self._handleKeyEvent)

    def _dispose(self):
        self._blur.fini()
        g_keyEventHandlers.discard(self._handleKeyEvent)
        super(EventBossTeleportView, self)._dispose()

    @property
    def _spawnCtrl(self):
        return self._sessionProvider.dynamic.teleport

    def _chooseSpawnPoint(self, pointGuid):
        if self._spawnCtrl and pointGuid:
            self._spawnCtrl.chooseSpawnKeyPoint(pointGuid)

    def _handleKeyEvent(self, event):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_AMMO_CHOICE_4, event.key) and event.isKeyDown() and not event.isRepeatedEvent():
            self.onCancel()
