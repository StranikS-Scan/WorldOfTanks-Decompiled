# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/appearance_cache_ctrl.py
import logging
import BigWorld
from gui.battle_control.controllers.appearance_cache_ctrls.default_appearance_cache_ctrl import DefaultAppearanceCacheController
from helpers import uniprof
from items.vehicles import VehicleDescriptor
from vehicle_outfit.outfit import Outfit
from vehicle_systems.camouflages import getOutfitComponent
from vehicle_systems.tankStructure import ModelStates
from vehicle_systems.vehicle_damage_state import VehicleDamageState
from vehicle_systems import model_assembler
from vehicle_systems import camouflages
from vehicle_systems.tankStructure import ModelsSetParams
_logger = logging.getLogger(__name__)

class LSAppearanceCacheController(DefaultAppearanceCacheController):

    def __init__(self, setup):
        super(LSAppearanceCacheController, self).__init__(setup)
        self._spawnList = set()

    def startControl(self, battleCtx, arenaVisitor):
        super(LSAppearanceCacheController, self).startControl(battleCtx, arenaVisitor)
        self._spawnList = set()

    def stopControl(self):
        super(LSAppearanceCacheController, self).stopControl()
        self._spawnList = set()

    def _addListeners(self):
        avatar = BigWorld.player()
        if hasattr(avatar, 'onSpawnListUpdated'):
            avatar.onSpawnListUpdated += self.updateSpawnList

    def _removeListeners(self):
        avatar = BigWorld.player()
        if hasattr(avatar, 'onSpawnListUpdated'):
            avatar.onSpawnListUpdated -= self.updateSpawnList

    @uniprof.regionDecorator(label='LSAppearanceCacheController.updateSpawnList', scope='wrap')
    def updateSpawnList(self, spawnListData):
        toAdd = spawnListData.difference(self._spawnList)
        toRemove = self._spawnList.difference(spawnListData)
        for data in toAdd:
            vDesc = VehicleDescriptor(compactDescr=data.vehicleCD)
            outfit = Outfit(component=getOutfitComponent(data.outfitCD), vehicleCD=data.vehicleCD)
            prereqs = set(self.collectPrerequisitesForEventBattle(vDesc, outfit, BigWorld.player().spaceID, False, ModelStates.UNDAMAGED))
            self._appearanceCache.loadResources(data.vehicleCD, list(prereqs))

        for data in toRemove:
            self._appearanceCache.unloadResources(data.vehicleCD)

        self._spawnList = spawnListData
        _logger.debug('SpawnList cache updated=%s', spawnListData)

    @staticmethod
    def collectPrerequisitesForEventBattle(typeDescriptor, outfit, spaceID, isTurretDetached, damageState):
        isUndamaged = VehicleDamageState.isUndamagedModel(damageState)
        prereqs = typeDescriptor.prerequisites(True)
        attachments = camouflages.getAttachments(outfit, typeDescriptor) if isUndamaged else []
        prereqs.extend(camouflages.getCamoPrereqs(outfit, typeDescriptor))
        prereqs.extend(camouflages.getAttachmentsAnimatorsPrereqs(attachments, spaceID))
        splineDesc = typeDescriptor.chassis.splineDesc
        modelsSet = outfit.modelsSet
        if splineDesc is not None:
            for _, trackDesc in splineDesc.trackPairs.iteritems():
                prereqs += trackDesc.prerequisites(modelsSet)

        modelsSetParams = ModelsSetParams(outfit.modelsSet, damageState, attachments)
        compoundAssembler = model_assembler.prepareCompoundAssembler(typeDescriptor, modelsSetParams, spaceID, isTurretDetached)
        prereqs.append(compoundAssembler)
        collisionAssembler = model_assembler.prepareCollisionAssembler(typeDescriptor, isTurretDetached, spaceID)
        prereqs.append(collisionAssembler)
        physicalTracksBuilders = typeDescriptor.chassis.physicalTracks
        for name, builders in physicalTracksBuilders.iteritems():
            for index, builder in enumerate(builders):
                prereqs.append(builder.createLoader(spaceID, '{0}{1}PhysicalTrack'.format(name, index), modelsSetParams.skin))

        return prereqs
