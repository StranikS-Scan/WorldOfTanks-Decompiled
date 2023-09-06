# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/appearance_cache_ctrls/maps_training_appearance_cache_ctrl.py
import logging
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from helpers import uniprof
_logger = logging.getLogger(__name__)

class MapsTrainingAppearanceCacheController(EventAppearanceCacheController):

    @uniprof.regionDecorator(label='MapsTrainingAppearanceCacheController.updateSpawnList', scope='wrap')
    def updateSpawnList(self, spawnListData):
        self._updateSpawnList(spawnListData)
        _logger.debug('MapsTrainingAppearanceCacheController SpawnList cache updated=%s', spawnListData)
