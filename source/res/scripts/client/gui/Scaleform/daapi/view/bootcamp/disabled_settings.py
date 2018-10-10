# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/disabled_settings.py
import resource_helper
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP

class BCDisabledSettings(object):

    def __init__(self):
        self.__disabledSettings = []
        self.__readSettingsTemplate()

    @property
    def disabledSetting(self):
        for item in self.__disabledSettings:
            yield item

    def __readSettingsTemplate(self):
        LOG_DEBUG_DEV_BOOTCAMP('Reading BootCamp template settings')
        ctx, section = resource_helper.getRoot('gui/bootcamp_blocked_settings.xml')
        self.__disabledSettings = []
        for ctx, subSection in resource_helper.getIterator(ctx, section):
            item = resource_helper.readItem(ctx, subSection).value
            if 'controlPath' in item:
                path = item['controlPath'].split('/')
                self.__disabledSettings.append(path)
