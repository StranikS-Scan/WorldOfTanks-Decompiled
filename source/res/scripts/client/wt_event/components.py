# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wt_event/components.py
from arena_component_system.client_arena_component_system import ClientArenaComponent
from helpers import isPlayerAvatar
from PlayerEvents import g_playerEvents

class WtArenaComponent(ClientArenaComponent):

    def activate(self):
        super(WtArenaComponent, self).activate()
        if isPlayerAvatar():
            self._initialize()
        else:
            g_playerEvents.onAvatarBecomePlayer += self._initialize
        g_playerEvents.onAvatarBecomeNonPlayer += self._finalize

    def deactivate(self):
        super(WtArenaComponent, self).deactivate()
        if isPlayerAvatar():
            self._finalize()
        g_playerEvents.onAvatarBecomePlayer -= self._initialize
        g_playerEvents.onAvatarBecomeNonPlayer -= self._finalize

    def _initialize(self):
        g_playerEvents.onAvatarBecomePlayer -= self._initialize

    def _finalize(self):
        g_playerEvents.onAvatarBecomeNonPlayer -= self._finalize
