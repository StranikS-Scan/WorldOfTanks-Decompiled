# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_settings/event_disabled_settings.py
import resource_helper
_CONFIG_PATH = 'gui/event_blocked_settings.xml'

class EventDisabledSettings(object):

    def __init__(self):
        self.__disabledSettings = []
        self.__readSettingsTemplate()

    @property
    def disabledSetting(self):
        for item in self.__disabledSettings:
            yield item

    def __readSettingsTemplate(self):
        ctx, section = resource_helper.getRoot(_CONFIG_PATH)
        self.__disabledSettings = []
        for ctx, subSection in resource_helper.getIterator(ctx, section):
            item = resource_helper.readItem(ctx, subSection).value
            if 'controlPath' in item:
                path = item['controlPath'].split('/')
                self.__disabledSettings.append(path)

        resource_helper.purgeResource(_CONFIG_PATH)
