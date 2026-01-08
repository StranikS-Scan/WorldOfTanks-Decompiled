# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/settings/loggers.py
from uilogging.base.logger import _BaseLogger as Logger
from uilogging.constants import LogLevels
from uilogging.settings.constants import FEATURE, GROUP

class SettingsLogger(Logger):
    __slots__ = ()

    def __init__(self):
        super(SettingsLogger, self).__init__(feature=FEATURE, group=GROUP)

    def log(self, action, sessionId, globalSettings, globalSettingsHash, localSettings, localSettingsHash):
        self._log(action=action, loglevel=LogLevels.NOTSET, session_id=sessionId, global_settings=globalSettings, global_settings_hash=globalSettingsHash, local_settings=localSettings, local_settings_hash=localSettingsHash)
