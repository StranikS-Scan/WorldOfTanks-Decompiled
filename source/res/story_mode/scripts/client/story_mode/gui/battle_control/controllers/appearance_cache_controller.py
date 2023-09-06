# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/appearance_cache_controller.py
from logging import getLogger
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)

class AppearanceCacheController(EventAppearanceCacheController):

    def updateSpawnList(self, spawnListData):
        self._updateSpawnList(spawnListData)
        _logger.debug('AppearanceCacheController.SpawnList cache updated=%s', spawnListData)
