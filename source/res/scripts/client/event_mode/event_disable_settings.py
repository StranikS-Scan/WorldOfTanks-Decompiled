# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_mode/event_disable_settings.py
import resource_helper

class EventDisabledSettings(object):

    def __init__(self):
        self._disabledSettings = []
        self._readSettingsTemplate()

    @property
    def disabledSetting(self):
        for item in self._disabledSettings:
            yield item

    def _readSettingsTemplate(self):
        ctx, section = resource_helper.getRoot('gui/event_disable_settings.xml')
        self._disabledSettings = []
        for ctx, subSection in resource_helper.getIterator(ctx, section):
            item = resource_helper.readItem(ctx, subSection).value
            if 'controlPath' in item:
                path = item['controlPath'].split('/')
                self._disabledSettings.append(path)
