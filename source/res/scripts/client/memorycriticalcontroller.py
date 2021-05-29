# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MemoryCriticalController.py
from functools import partial
import BigWorld
import Event
import WWISE
from debug_utils import LOG_NOTE, LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING

class MemoryCriticalController(object):
    ORIGIN_DEFAULT = -1
    messages = property(lambda self: self.__messages)
    originTexQuality = property(lambda self: self.__originTexQuality)

    def __init__(self):
        self.__messages = []
        self.__originTexQuality = -1
        self.__needReboot = False
        self.__loweredSettings = []
        self.onMemCrit = Event.Event()
        self.__selfCheckInProgress = False
        self.__pendingEvent = None
        return

    def destroy(self):
        if self.onMemCrit is not None:
            self.onMemCrit.clear()
            self.onMemCrit = None
        if self.__pendingEvent is not None:
            LOG_WARNING('There is MemoryCriticalEvent but it was not logged')
            self.__pendingEvent = None
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAccountShowGUI -= self.__logPendingMemCritEvent
        g_playerEvents.onAvatarBecomePlayer -= self.__logPendingMemCritEvent
        del self.__loweredSettings[:]
        return

    def __logMemCritEvent(self, memCriticalEvent):
        player = BigWorld.player()
        if player is not None and player.isPlayer:
            from PlayerEvents import g_playerEvents
            if not g_playerEvents.isPlayerEntityChanging:
                player.logMemoryCriticalEvent(memCriticalEvent)
                return True
        return False

    def __logPendingMemCritEvent(self, *args, **kwargs):
        if self.__pendingEvent is not None:
            if not self.__logMemCritEvent(self.__pendingEvent):
                LOG_WARNING('MemoryCriticalEvent was waiting to be logged but endpoint (Account or Avatar) is missing')
                return
            self.__pendingEvent = None
        else:
            LOG_ERROR('Pending MemoryCriticalEvent is missing')
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAccountShowGUI -= self.__logPendingMemCritEvent
        g_playerEvents.onAvatarBecomePlayer -= self.__logPendingMemCritEvent
        return

    def __postponeLogMemCritEvent(self, memCriticalEvent):
        self.__pendingEvent = memCriticalEvent
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAccountShowGUI += self.__logPendingMemCritEvent
        g_playerEvents.onAvatarBecomePlayer += self.__logPendingMemCritEvent

    def __call__(self):
        memCriticalEvent = BigWorld.collectLastMemoryCriticalEvent()
        if not self.__logMemCritEvent(memCriticalEvent):
            self.__postponeLogMemCritEvent(memCriticalEvent)
        if self.__needReboot:
            return
        WWISE.WW_onMemoryCritical()
        self.__selfCheckInProgress = False
        self.__needReboot = True
        self.__loweredSettings = [ t for t in BigWorld.graphicsSettings() if t[0] == 'TEXTURE_QUALITY' ]
        texQuality = BigWorld.getGraphicsSetting('TEXTURE_QUALITY')
        pipelineType = BigWorld.getGraphicsSetting('RENDER_PIPELINE')
        textureSettings = [ t for t in self.__loweredSettings if t[0] == 'TEXTURE_QUALITY' ][0][2]
        textureMinQuality = len(textureSettings) - 1
        if textureSettings[textureMinQuality][0] == 'OFF':
            textureMinQuality -= 1
        while 1:
            (textureSettings[textureMinQuality][1] is False or pipelineType == 1 and textureSettings[textureMinQuality][2] is True) and textureMinQuality -= 1

        if textureMinQuality < texQuality:
            textureMinQuality = texQuality
        if texQuality < textureMinQuality:
            if self.__originTexQuality == -1 and texQuality < textureMinQuality:
                self.__originTexQuality = texQuality
        else:
            message = (1, 'insufficient_memory_please_reboot')
            self.__messages.append(message)
            self.onMemCrit(message)
            LOG_NOTE("The free memory is too low, We can't do anything. Please, reboot the game.")
            return
        message = (0, 'tex_was_lowered_to_min')
        self.onMemCrit(message)
        message = (1, 'insufficient_memory_please_reboot')
        self.__messages.append(message)
        if texQuality < textureMinQuality:
            BigWorld.setGraphicsSetting('TEXTURE_QUALITY', textureMinQuality)
            LOG_NOTE('To save the memory the texture quality setting was force lowered to <%s>.' % textureSettings[textureMinQuality][0])
        BigWorld.commitPendingGraphicsSettings()

    def restore(self):
        toRestore = []
        if self.__originTexQuality != -1:
            toRestore.append(('TEXTURE_QUALITY', self.__originTexQuality))
        commit = False
        for label, originalIndex in toRestore:
            if self.__setGraphicsSetting(label, self.__originTexQuality):
                commit = True
                LOG_NOTE('The setting was restored to the original value.', label, self.__getLoweredOptionLabel(label, originalIndex))
            LOG_ERROR('The setting was not restored to the original value.', label, self.__getLoweredOptionLabel(label, originalIndex), BigWorld.getGraphicsSetting(label), self.__getLoweredOption(label))

        if commit:
            BigWorld.commitPendingGraphicsSettings()
            self.__originTexQuality = -1
            self.__needReboot = False
            self.__messages = []

    def startSelfcheck(self):
        if self.__selfCheckInProgress or self.__needReboot:
            LOG_NOTE('Cannot start selfcheck.')
            return
        self.__selfCheckInProgress = True
        self.__checkStep(30, 1.0)

    def cleanupCheck(self):
        BigWorld.wg_free()

    def __checkStep(self, blockSize, dt):
        if not self.__selfCheckInProgress:
            return
        BigWorld.wg_alloc(blockSize * 1024 * 1024)
        BigWorld.callback(dt, partial(self.__checkStep, blockSize, dt))

    @staticmethod
    def __setGraphicsSetting(label, index):
        isSet = True
        try:
            BigWorld.setGraphicsSetting(label, index)
        except ValueError:
            isSet = False
            LOG_CURRENT_EXCEPTION()

        return isSet

    def __getLoweredOption(self, token):
        for setting in self.__loweredSettings:
            label, _, options = setting[:3]
            if label == token:
                return options

        return []

    def __getLoweredOptionLabel(self, token, index):
        options = self.__getLoweredOption(token)
        return options[index][0] if -1 < index < len(options) else str(index)


g_critMemHandler = MemoryCriticalController()
