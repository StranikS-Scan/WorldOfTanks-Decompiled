# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_control/controllers/appearance_cache_controller.py
import BigWorld
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from helpers import uniprof
from vehicle_systems import model_assembler
from vehicle_systems.tankStructure import ModelsSetParams, ModelStates
from gui.battle_control.controllers.appearance_cache_ctrls import getWholeVehModels
from items.vehicles import VehicleDescr, parseIntCompactDescr
from vehicle_outfit.outfit import Outfit

class HBAppearanceCacheController(EventAppearanceCacheController):

    @uniprof.regionDecorator(label='HBAppearanceCacheController.updateSpawnList', scope='wrap')
    def updateSpawnList(self, spawnListData):
        self._updateSpawnList(spawnListData)

    def arenaLoadCompleted(self):
        super(HBAppearanceCacheController, self).arenaLoadCompleted()
        self.__precacheExtraResources()

    def __precacheExtraResources(self):
        tankSet = BigWorld.player().HBAvatarComponent.tankSet
        for intCD in tankSet:
            descr = VehicleDescr(typeID=parseIntCompactDescr(intCD)[1:])
            cd = descr.makeCompactDescr()
            outfit = Outfit(vehicleCD=cd)
            prereqs = set(getWholeVehModels(descr))
            modelsSetParams = ModelsSetParams(outfit.modelsSet, ModelStates.UNDAMAGED, [])
            compoundAssembler = model_assembler.prepareCompoundAssembler(descr, modelsSetParams, BigWorld.camera().spaceID)
            prereqs.add(compoundAssembler)
            modelsSetParams = ModelsSetParams(outfit.modelsSet, ModelStates.DESTROYED, [])
            compoundAssembler = model_assembler.prepareCompoundAssembler(descr, modelsSetParams, BigWorld.camera().spaceID)
            prereqs.add(compoundAssembler)
            modelsSetParams = ModelsSetParams(outfit.modelsSet, ModelStates.EXPLODED, [])
            compoundAssembler = model_assembler.prepareCompoundAssembler(descr, modelsSetParams, BigWorld.camera().spaceID)
            prereqs.add(compoundAssembler)
            self._appearanceCache.loadResources(cd, list(prereqs))
