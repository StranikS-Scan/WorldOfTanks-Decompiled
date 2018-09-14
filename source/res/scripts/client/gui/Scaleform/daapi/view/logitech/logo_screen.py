# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/logitech/logo_screen.py
from gui.Scaleform.daapi.view.logitech.LogitechMonitorMeta import LogitechMonitorMonoScreenMeta, LogitechMonitorColoredScreenMeta
from helpers import i18n

class LogitechMonitorLogoMonoScreen(LogitechMonitorMonoScreenMeta):

    def _onLoaded(self):
        self.as_setText(i18n.makeString('#menu:login/version'))


class LogitechMonitorLogoColoredScreen(LogitechMonitorColoredScreenMeta):
    pass
