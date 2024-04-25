# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_control/controllers/appearance_cache_controller.py
import BigWorld
from logging import getLogger
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from helpers import uniprof
from vehicle_systems import model_assembler
from items.vehicles import VehicleDescriptor
from vehicle_systems.tankStructure import ModelsSetParams
from gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin, PerformanceGroup
_logger = getLogger(__name__)

class HBAppearanceCacheController(EventAppearanceCacheController):

    @uniprof.regionDecorator(label='HBAppearanceCacheController.updateSpawnList', scope='wrap')
    def updateSpawnList(self, spawnListData):
        self._updateSpawnList(spawnListData)
        _logger.debug('HBAppearanceCacheController SpawnList cache updated=%s', spawnListData)

    def arenaLoadCompleted(self):
        super(HBAppearanceCacheController, self).arenaLoadCompleted()
        pam = PerformanceAnalyzerMixin()
        performanceGroup = pam.getPerformanceGroup()
        if performanceGroup in (PerformanceGroup.MEDIUM_RISK, PerformanceGroup.HIGH_RISK):
            _logger.info('HBAppearanceCacheController start to precache resources.')
            self.__precacheExtraResources()

    def __precacheExtraResources(self):
        playerVehicleDescr = BigWorld.player().vehicleTypeDescriptor
        descr = VehicleDescriptor(typeName=playerVehicleDescr.name)
        assembler = model_assembler.prepareCompoundAssembler(descr, ModelsSetParams('', 'destroyed', []), BigWorld.camera().spaceID, False)
        collisionAssembler = model_assembler.prepareCollisionAssembler(descr, False, BigWorld.camera().spaceID)
        self._appearanceCache.loadResources(descr.makeCompactDescr(), [(assembler, collisionAssembler)])
