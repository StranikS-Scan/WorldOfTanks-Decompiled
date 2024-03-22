# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/mods_statistic/logger.py
import BigWorld
import json
import logging
from wotdecorators import noexcept
from uilogging.base.logger import _BaseLogger as Logger
from uilogging.constants import DEFAULT_LOGGER_NAME
_logger = logging.getLogger(DEFAULT_LOGGER_NAME)

class ModsStatisticLogger(Logger):
    FEATURE_NAME = 'mods_statistic'
    GROUP_NAME = 'mods_statistic'
    ACTION = 'collected'
    __alreadyLogged = False

    def __init__(self):
        super(ModsStatisticLogger, self).__init__(self.FEATURE_NAME, self.GROUP_NAME)

    @noexcept
    def log(self):
        if ModsStatisticLogger.__alreadyLogged:
            return
        _logger.debug('Mods statistic requested.')
        if self.disabled:
            return
        mods = BigWorld.wg_getMods()
        if not mods:
            _logger.debug('There are not mods.')
            return
        modsJson = json.dumps(mods)
        super(ModsStatisticLogger, self)._log(self.ACTION, mods_statistic_json=modsJson)
        ModsStatisticLogger.__alreadyLogged = True
