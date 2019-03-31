# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MemoryCriticalController.py
# Compiled at: 2011-11-28 22:38:18
import BigWorld
from debug_utils import LOG_NOTE
import Event

class MemoryCriticalController:
    QUALITY_MAP = ['high', 'medium', 'low']
    messages = property(lambda self: self.__messages)
    onMemCrit = property(lambda self: self.__event)
    originQuality = property(lambda self: self.__originQuality)

    def __init__(self):
        self.__messages = []
        self.__originQuality = -1
        self.__needReboot = False
        self.__event = Event.Event()

    def destroy(self):
        if self.__event is not None:
            self.__event.clear()
            self.__event = None
        return

    def __call__(self):
        if self.__needReboot:
            return
        texQuality = BigWorld.getGraphicsSetting('TEXTURE_QUALITY')
        if texQuality < 2:
            texQuality += 1
            if self.__originQuality == -1:
                self.__originQuality = texQuality - 1
            LOG_NOTE('To save the memory the texture quality setting was force lowered to <%s>.' % self.QUALITY_MAP[texQuality])
        else:
            message = (1, 'insufficient_memory_please_reboot')
            self.__messages.append(message)
            self.__event(message)
            LOG_NOTE("The free memory is too low, We can't do anything. Please, reboot the game.")
            self.__needReboot = True
            return
        message = (0, 'tex_was_lowered_to_' + self.QUALITY_MAP[texQuality])
        self.__messages.append(message)
        self.__event(message)
        BigWorld.setGraphicsSetting('TEXTURE_QUALITY', texQuality)
        BigWorld.commitPendingGraphicsSettings()

    def restore(self):
        if self.__originQuality != -1:
            BigWorld.setGraphicsSetting('TEXTURE_QUALITY', self.__originQuality)
            BigWorld.commitPendingGraphicsSettings()
            LOG_NOTE('The texture quality setting was restored to the original value <%s>.' % self.QUALITY_MAP[self.__originQuality])
            self.__originQuality = -1
            self.__needReboot = False
            self.__messages = []


g_critMemHandler = MemoryCriticalController()
