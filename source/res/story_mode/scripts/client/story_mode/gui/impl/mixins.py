# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/mixins.py
from PlayerEvents import g_playerEvents

class DestroyWindowOnDisconnectMixin(object):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(DestroyWindowOnDisconnectMixin, self).__init__(*args, **kwargs)
        g_playerEvents.onDisconnected += self.__disconnectHandler

    def _finalize(self):
        g_playerEvents.onDisconnected -= self.__disconnectHandler
        super(DestroyWindowOnDisconnectMixin, self)._finalize()

    def __disconnectHandler(self):
        self.destroy()
