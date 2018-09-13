# Embedded file name: scripts/client/MemoryCriticalController.py
import BigWorld
from debug_utils import LOG_NOTE
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
        self.__event = Event.Event()

    def destroy(self):
        if self.__event is not None:
            self.__event.clear()
            self.__event = None
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
        while textureSettings[textureMinQuality][1] == False or pipelineType == 1 and textureSettings[textureMinQuality][2] == True:
            textureMinQuality -= 1

        if textureMinQuality < texQuality:
            textureMinQuality = texQuality
        while floraSettings[floraMinQuality][1] == False or pipelineType == 1 and floraSettings[floraMinQuality][2] == True:
            floraMinQuality -= 1

        if floraMinQuality < floraQuality:
            floraMinQuality = floraQuality
        while terrainSettings[terrainMinQuality][1] == False or pipelineType == 1 and terrainSettings[terrainMinQuality][2] == True:
            terrainMinQuality -= 1

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
        if self.__originTexQuality != -1 or self.__originFloraQuality != -1 or self.__originTerrainQuality != -1:
            if self.__originTexQuality != -1:
                BigWorld.setGraphicsSetting('TEXTURE_QUALITY', self.__originTexQuality)
                textureSettings = [ t for t in self.__loweredSettings if t[0] == 'TEXTURE_QUALITY' ][0][2]
                LOG_NOTE('The texture quality setting was restored to the original value <%s>.' % textureSettings[self.__originTexQuality][0])
            if self.__originFloraQuality != -1:
                BigWorld.setGraphicsSetting('FLORA_QUALITY', self.__originFloraQuality)
                floraSettings = [ t for t in self.__loweredSettings if t[0] == 'FLORA_QUALITY' ][0][2]
                LOG_NOTE('The flora quality setting was restored to the original value <%s>.' % floraSettings[self.__originFloraQuality][0])
            if self.__originTerrainQuality != -1:
                BigWorld.setGraphicsSetting('TERRAIN_QUALITY', self.__originTerrainQuality)
                terrainSettings = [ t for t in self.__loweredSettings if t[0] == 'TERRAIN_QUALITY' ][0][2]
                LOG_NOTE('The terrain quality setting was restored to the original value <%s>.' % terrainSettings[self.__originTerrainQuality][0])
            BigWorld.commitPendingGraphicsSettings()
            self.__originTexQuality = -1
            self.__originFloraQuality = -1
            self.__originTerrainQuality = -1
            self.__needReboot = False
            self.__messages = []


g_critMemHandler = MemoryCriticalController()
