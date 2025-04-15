# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_effect_settings.py
import ResMgr

class EventEffectsSettings(object):
    EVENTS_EFFECTS_CONFIG_FILE = 'scripts/event_effects.xml'
    DYNAMIC_OBJECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'

    def __init__(self):
        section = ResMgr.openSection(self.EVENTS_EFFECTS_CONFIG_FILE + '/effects_list')
        self.eventEffectsSettings = self._effectsSettingsReader(section)
        self.dynamicObjects = ResMgr.openSection(self.DYNAMIC_OBJECTS_CONFIG_FILE)

    def _effectsSettingsReader(self, section):
        result = {}
        for name, subSection in section.items():
            result[name] = self._readEffectList(subSection)

        return result

    def _readEffectList(self, section):
        result = {}
        for name, subSection in section.items():
            result[name] = self._readEffectSettins(subSection)

        return result

    def _readEffectSettins(self, section):
        result = {}
        result['name'] = section.readString('name', '')
        result['duration'] = section.readFloat('duration', 0.0)
        return result
