# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/mixins.py
from PlayerEvents import g_playerEvents

class DestroyWindowOnDisconnectMixin(object):
    __slots__ = ()

    def _initialize(self):
        super(DestroyWindowOnDisconnectMixin, self)._initialize()
        g_playerEvents.onDisconnected += self.__disconnectHandler

    def _finalize(self):
        g_playerEvents.onDisconnected -= self.__disconnectHandler
        super(DestroyWindowOnDisconnectMixin, self)._finalize()

    def __disconnectHandler(self):
        self.destroy()
