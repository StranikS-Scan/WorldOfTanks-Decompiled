# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MemoryCriticalController.py
import BigWorld
from debug_utils import LOG_NOTE, LOG_CURRENT_EXCEPTION, LOG_ERROR
import Event

class MemoryCriticalController:
    ORIGIN_DEFAULT = -1
    messages = property(lambda self: self.__messages)
    onMemCrit = property(lambda self: self.__event)
    originTexQuality = property(lambda self: self.__originTexQuality)
    originFloraQuality = property(lambda self: self.__originFloraQuality)
    originTerrainQuality = property(lambda self: self.__originTerrainQuality)

    def __init__(self):
        self.__messages = []
        self.__originTexQuality = -1
        self.__originFloraQuality = -1
        self.__originTerrainQuality = -1
        self.__needReboot = False
        self.__loweredSettings = []
        self.__event = Event.Event()

    def destroy(self):
        if self.__event is not None:
            self.__event.clear()
            self.__event = None
        del self.__loweredSettings[:]
        return

    def __call__(self):
        if self.__needReboot:
            return
        self.__needReboot = True
        self.__loweredSettings = [ t for t in BigWorld.graphicsSettings() if t[0] == 'TEXTURE_QUALITY' or t[0] == 'FLORA_QUALITY' or t[0] == 'TERRAIN_QUALITY' ]
        texQuality = BigWorld.getGraphicsSetting('TEXTURE_QUALITY')
        floraQuality = BigWorld.getGraphicsSetting('FLORA_QUALITY')
        terrainQuality = BigWorld.getGraphicsSetting('TERRAIN_QUALITY')
        pipelineType = BigWorld.getGraphicsSetting('RENDER_PIPELINE')
        textureSettings = [ t for t in self.__loweredSettings if t[0] == 'TEXTURE_QUALITY' ][0][2]
        floraSettings = [ t for t in self.__loweredSettings if t[0] == 'FLORA_QUALITY' ][0][2]
        terrainSettings = [ t for t in self.__loweredSettings if t[0] == 'TERRAIN_QUALITY' ][0][2]
        textureMinQuality = len(textureSettings) - 1
        floraMinQuality = len(floraSettings) - 1
        terrainMinQuality = len(terrainSettings) - 1
        if textureSettings[textureMinQuality][0] == 'OFF':
            textureMinQuality -= 1
        while 1:
            (textureSettings[textureMinQuality][1] is False or pipelineType == 1 and textureSettings[textureMinQuality][2] is True) and textureMinQuality -= 1

        if textureMinQuality < texQuality:
            textureMinQuality = texQuality
        while 1:
            (floraSettings[floraMinQuality][1] is False or pipelineType == 1 and floraSettings[floraMinQuality][2] is True) and floraMinQuality -= 1

        if floraMinQuality < floraQuality:
            floraMinQuality = floraQuality
        while 1:
            (terrainSettings[terrainMinQuality][1] is False or pipelineType == 1 and terrainSettings[terrainMinQuality][2] is True) and terrainMinQuality -= 1

        if terrainMinQuality < terrainQuality:
            terrainMinQuality = terrainQuality
        if texQuality < textureMinQuality or floraQuality < floraMinQuality or terrainQuality < terrainMinQuality:
            if self.__originTexQuality == -1 and texQuality < textureMinQuality:
                self.__originTexQuality = texQuality
            if self.__originFloraQuality == -1 and floraQuality < floraMinQuality:
                self.__originFloraQuality = floraQuality
            if self.__originTerrainQuality == -1 and terrainQuality < terrainMinQuality:
                self.__originTerrainQuality = terrainQuality
        else:
            message = (1, 'insufficient_memory_please_reboot')
            self.__messages.append(message)
            self.__event(message)
            LOG_NOTE("The free memory is too low, We can't do anything. Please, reboot the game.")
            return
        message = (0, 'tex_was_lowered_to_min')
        self.__event(message)
        message = (1, 'insufficient_memory_please_reboot')
        self.__messages.append(message)
        if texQuality < textureMinQuality:
            BigWorld.setGraphicsSetting('TEXTURE_QUALITY', textureMinQuality)
            LOG_NOTE('To save the memory the texture quality setting was force lowered to <%s>.' % textureSettings[textureMinQuality][0])
        if floraQuality < floraMinQuality:
            BigWorld.setGraphicsSetting('FLORA_QUALITY', floraMinQuality)
            LOG_NOTE('To save the memory the flora quality setting was force lowered to <%s>.' % floraSettings[floraMinQuality][0])
        if terrainQuality < terrainMinQuality:
            BigWorld.setGraphicsSetting('TERRAIN_QUALITY', terrainMinQuality)
            LOG_NOTE('To save the memory the terrain quality setting was force lowered to <%s>.' % terrainSettings[terrainMinQuality][0])
        BigWorld.commitPendingGraphicsSettings()

    def restore(self):
        toRestore = []
        if self.__originTexQuality != -1:
            toRestore.append(('TEXTURE_QUALITY', self.__originTexQuality))
        if self.__originFloraQuality != -1:
            toRestore.append(('FLORA_QUALITY', self.__originFloraQuality))
        if self.__originTerrainQuality != -1:
            toRestore.append(('TERRAIN_QUALITY', self.__originTerrainQuality))
        commit = False
        for label, originalIndex in toRestore:
            if self.__setGraphicsSetting(label, self.__originTexQuality):
                commit = True
                LOG_NOTE('The setting was restored to the original value.', label, self.__getLoweredOptionLabel(label, originalIndex))
            LOG_ERROR('The setting was not restored to the original value.', label, self.__getLoweredOptionLabel(label, originalIndex), BigWorld.getGraphicsSetting(label), self.__getLoweredOption(label))

        if commit:
            BigWorld.commitPendingGraphicsSettings()
            self.__originTexQuality = -1
            self.__originFloraQuality = -1
            self.__originTerrainQuality = -1
            self.__needReboot = False
            self.__messages = []

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
