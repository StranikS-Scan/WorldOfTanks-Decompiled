# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/dev_sub_mode.py
import logging
import typing
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
if typing.TYPE_CHECKING:
    from fun_random.helpers.server_settings import FunSubModeConfig
_logger = logging.getLogger(__name__)

class FunDevSubMode(FunBaseSubMode):

    def __init__(self, subModeSettings):
        super(FunDevSubMode, self).__init__(subModeSettings)
        _logger.info('%s is created with settings %s', self, self._settings)

    def __repr__(self):
        return 'FunDevSubMode id={}, isEnabled={}'.format(self._settings.eventID, self._settings.isEnabled)

    def clearNotification(self):
        super(FunDevSubMode, self).clearNotification()
        _logger.info('%s cleared all inner timers', self)

    def destroy(self):
        super(FunDevSubMode, self).destroy()
        _logger.info('%s is destroyed', self)

    def startNotification(self):
        super(FunDevSubMode, self).startNotification()
        _logger.info('%s starts inner timers for status tracking', self)

    def stopNotification(self):
        super(FunDevSubMode, self).stopNotification()
        _logger.info('%s stops inner timers for status tracking', self)

    def _updateSettings(self, subModeSettings):
        _logger.info('%s received new settings %s', self, subModeSettings)
        return super(FunDevSubMode, self)._updateSettings(subModeSettings)

    def _subModeStatusTick(self):
        _logger.info('%s triggering SUB_STATUS_TICK event', self)
        super(FunDevSubMode, self)._subModeStatusTick()

    def _subModeStatusUpdate(self):
        _logger.info('%s triggering SUB_STATUS_UPDATE event', self)
        super(FunDevSubMode, self)._subModeStatusUpdate()
