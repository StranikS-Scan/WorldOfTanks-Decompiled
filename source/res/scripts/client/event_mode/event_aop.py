# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_mode/event_aop.py
import logging
from helpers import aop
from event_disable_settings import EventDisabledSettings
_logger = logging.getLogger(__name__)

class _PointcutDisableSettingsControls(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.common.settings.SettingsWindow', 'SettingsWindow', 'as_setDataS', aspects=(_AspectDisableSettingsControls,))


class _AspectDisableSettingsControls(aop.Aspect):

    def __init__(self):
        self._eventSettings = EventDisabledSettings()

    def atCall(self, cd):
        for disableItem in self._eventSettings.disabledSetting:
            self.__disableControl(cd, disableItem)

    def atReturn(self, cd):
        cd.self.as_setPveEventS(True)

    def __disableControl(self, cd, controlPath):
        page = ''
        subpage = ''
        control = ''
        if len(controlPath) == 2:
            page, control = controlPath
        elif len(controlPath) == 3:
            page, subpage, control = controlPath
        try:
            cd.self.as_disableControlS(page, control, subpage)
        except Exception as e:
            _logger.debug('Error: No such page (%s), subpage (%s) or control (%s)?', page, subpage, control)
            _logger.exception(e)
