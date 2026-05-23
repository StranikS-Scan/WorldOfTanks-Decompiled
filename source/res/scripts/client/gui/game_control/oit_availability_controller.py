# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/oit_availability_controller.py
import BigWorld
from PlayerEvents import g_playerEvents
from config_schemas.oit_availability import oitAvailabilitySchema
from skeletons.gui.game_control import IOitAvailabilityController

class OitAvailabilityController(IOitAvailabilityController):

    def init(self):
        g_playerEvents.onConfigModelUpdated += self._onConfigModelUpdated

    def fini(self):
        g_playerEvents.onConfigModelUpdated -= self._onConfigModelUpdated

    def onAccountBecomePlayer(self):
        self._pushToEngine()

    def onAvatarBecomePlayer(self):
        self._pushToEngine()

    def isOitEnabledForPreset(self, qualityLevel):
        return BigWorld.isOitEnabledForPreset(qualityLevel)

    def _onConfigModelUpdated(self, gpKey):
        if oitAvailabilitySchema.gpKey == gpKey:
            self._pushToEngine()

    def _pushToEngine(self):
        config = oitAvailabilitySchema.getModel()
        if config is not None:
            BigWorld.configureOitPresets(config.min, config.low, config.medium, config.high, config.ultra)
        return
