# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/sound_systems/wwise_system.py
import WWISE
import SoundGroups
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.sounds.abstract import SoundSystemAbstract
from gui.sounds.sound_constants import SoundSystems, SPEAKERS_CONFIG
_LAPTOP_SOUND_PRESET = 2

class WWISESoundSystem(SoundSystemAbstract):

    def getID(self):
        return SoundSystems.WWISE

    def isMSR(self):
        return WWISE.WG_isMSR()

    def enableDynamicPreset(self):
        wwiseEvent = 'ue_set_preset_high_dynamic_range'
        self.sendGlobalEvent(wwiseEvent)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))

    def disableDynamicPreset(self):
        wwiseEvent = 'ue_set_preset_low_dynamic_range'
        self.sendGlobalEvent(wwiseEvent)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))

    def setBassBoost(self, isEnabled):
        if isEnabled:
            wwiseEvent = 'ue_set_preset_bassboost_on'
        else:
            wwiseEvent = 'ue_set_preset_bassboost_off'
        WWISE.WW_eventGlobalSync(wwiseEvent)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))

    def getSystemSpeakersPresetID(self):
        return WWISE.WW_getSystemSpeakersConfig()

    def getUserSpeakersPresetID(self):
        return WWISE.WW_getUserSpeakersConfig()

    def setUserSpeakersPresetID(self, presetID):
        if presetID not in SPEAKERS_CONFIG.RANGE:
            LOG_ERROR('Invalid value of presetID {}'.format(presetID))
            return
        if self.getUserSpeakersPresetID() == presetID:
            LOG_DEBUG('WWISE: Sounds preset is already set. Do nothing')
        else:
            WWISE.WW_setUserSpeakersConfig(presetID)
            LOG_DEBUG('WWISE: New sounds preset is set. New value is {}'.format(presetID))
            WWISE.WW_reinit()
            LOG_DEBUG('WWISE: Sound system is reinitialized')

    def setSoundSystem(self, soundSystemID):
        if soundSystemID == _LAPTOP_SOUND_PRESET:
            wwiseEvent = 'ue_set_preset_acoustic_device_laptop'
            soundSystemID = 0
            WWISE.WW_setSoundSystem(soundSystemID)
            WWISE.WW_eventGlobalSync(wwiseEvent)
        else:
            wwiseEvent = 'ue_set_preset_acoustic_device_reset'
            WWISE.WW_eventGlobalSync(wwiseEvent)
            WWISE.WW_setSoundSystem(soundSystemID)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))
        LOG_DEBUG('WWISE: sound system has been applied: %d' % soundSystemID)

    def sendGlobalEvent(self, eventName, **params):
        WWISE.WW_eventGlobalSync(eventName)

    def onEnvStart(self, environment):
        if SoundGroups.g_instance is not None:
            SoundGroups.g_instance.onEnvStart(environment)
        return

    def onEnvStop(self, environment):
        if SoundGroups.g_instance is not None:
            SoundGroups.g_instance.onEnvStop(environment)
        return
