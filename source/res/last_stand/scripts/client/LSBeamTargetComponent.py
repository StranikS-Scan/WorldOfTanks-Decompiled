# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBeamTargetComponent.py
from __future__ import absolute_import
import CGF
import BigWorld
import GenericComponents
import Math
import functools
import logging
from typing import TYPE_CHECKING
from CGF import HierarchyComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from BeamRibbonComponent import BeamRibbonComponent
from gui.shared.utils.TimeInterval import TimeInterval
from helpers.CallbackDelayer import CallbackDelayer
from ls_dyn_object_cache import LSPrefabs, getPrefabPath
if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set, Tuple
_logger = logging.getLogger(__name__)
_BEAM_NAME_TO_PREFAB_KEY = {'idle': LSPrefabs.BEAM_IDLE,
 'damage': LSPrefabs.BEAM_DAMAGE}

class BeamParam(object):

    def __init__(self, beamName, targetVehId, sourcePosition):
        self.beamName = beamName
        self.targetVehId = targetVehId
        self.sourcePosition = sourcePosition


class LSBeamTargetComponent(DynamicScriptComponent):
    _UPDATE_TICK_LENGTH = 0.5
    _DMG_BEAM_Y_OFFSET = 0.2

    def __init__(self):
        super(LSBeamTargetComponent, self).__init__()
        self._beams = {}
        self._sourceVehId = None
        self._targetVehIds = {}
        self._dmgBeams = {}
        self._dmgTargets = {}
        self._dmgBeamName = {}
        self._dmgSourcePosition = Math.Vector3()
        self._activeBeams = set()
        self._updateTI = TimeInterval(self._UPDATE_TICK_LENGTH, self, '_beamVisibilityUpdate')
        self._updateTI.start()
        self._callbackDelayer = CallbackDelayer()
        self._pendingBeams = {}
        self._loadingBeams = set()
        self._loadingDmgBeams = set()
        self._step = 0.0
        return

    def onDestroy(self):
        _logger.debug('onDestroy: sourceVehId=%s beams_keys=%s pending_keys=%s targets=%s', self._sourceVehId, list(self._beams.keys()), list(self._pendingBeams.keys()), self._targetVehIds)
        self.removeEffects([])
        self._updateTI.stop()
        self._callbackDelayer.destroy()

    @staticmethod
    def _safeRemove(queue, go):
        if go is not None and go.valid:
            queue.removeGameObject(go)
        return

    @staticmethod
    def _safeActivate(queue, go):
        if go is not None and go.valid:
            queue.activateGameObject(go)
        return

    @staticmethod
    def _safeDeactivate(queue, go):
        if go is not None and go.valid:
            queue.deactivateGameObject(go)
        return

    def applyEffects(self, beamName):
        _logger.debug('applyEffects: beamName=%s beamParams_count=%s', beamName, len(self.beamParams))
        beamParam = None
        for param in self.beamParams:
            if param['beamName'] == beamName:
                beamParam = param

        if not beamParam:
            _logger.debug('applyEffects: NO beamParam for beamName=%s -> abort', beamName)
            return
        else:
            sourcePosition = beamParam['sourcePosition']
            targetEntIds = beamParam['entIDs']
            targetVehIds = beamParam['vehIDs']
            self._sourceVehId = beamParam['sourceVehicleID']
            self._dmgSourcePosition = Math.Vector3(sourcePosition)
            self._dmgSourcePosition.y += self._DMG_BEAM_Y_OFFSET
            self._dmgBeamName[beamName] = beamParam['dmgBeamName']
            _logger.debug('applyEffects: sourceVehId=%s targetEntIds=%s targetVehIds=%s', self._sourceVehId, list(targetEntIds), list(targetVehIds))
            queue = CGF.CommandQueue(self.spaceID)
            for idx, entityId in enumerate(targetEntIds):
                beamParam = BeamParam(beamName, targetVehIds[idx], sourcePosition)
                isApplied = self._applyEffect(entityId, beamParam, queue)
                if not isApplied:
                    self._pendingBeams[entityId] = BeamParam(beamName, targetVehIds[idx], sourcePosition)

            return

    def removeEffects(self, vehiclesIds):
        _logger.debug('removeEffects: START vehiclesIds=%s (empty=%s) sourceVehId=%s beams_keys=%s dmg_keys=%s active=%s pending=%s', list(vehiclesIds), not vehiclesIds, self._sourceVehId, list(self._beams.keys()), list(self._dmgBeams.keys()), list(self._activeBeams), list(self._pendingBeams.keys()))
        queue = CGF.CommandQueue(self.spaceID)
        if not vehiclesIds:
            for beams in self._beams.values():
                for beam in beams.values():
                    self._safeRemove(queue, beam)

            self._beams = {}
            for beams in self._dmgBeams.values():
                for beam in beams.values():
                    self._safeRemove(queue, beam)

            self._dmgBeams = {}
            self._activeBeams.clear()
            self._targetVehIds = {}
            self._pendingBeams = {}
            self._dmgBeamName = {}
            self._sourceVehId = None
            self._loadingBeams.clear()
            self._loadingDmgBeams.clear()
        else:
            for vehId in vehiclesIds:
                if vehId in self._beams:
                    for beam in self._beams[vehId].values():
                        self._safeRemove(queue, beam)

                    del self._beams[vehId]
                if vehId in self._dmgBeams:
                    for beam in self._dmgBeams[vehId].values():
                        self._safeRemove(queue, beam)

                    del self._dmgBeams[vehId]
                if vehId in self._activeBeams:
                    self._activeBeams.remove(vehId)
                if vehId in self._dmgTargets:
                    self._safeRemove(queue, self._dmgTargets[vehId])
                    del self._dmgTargets[vehId]
                self._targetVehIds.pop(vehId, None)
                self._pendingBeams.pop(vehId, None)

        _logger.debug('removeEffects: END beams_keys=%s dmg_keys=%s active=%s pending=%s sourceVehId=%s targetVehIds=%s', list(self._beams.keys()), list(self._dmgBeams.keys()), list(self._activeBeams), list(self._pendingBeams.keys()), self._sourceVehId, self._targetVehIds)
        return

    def showDamage(self, entityId):
        _logger.debug('showDamage: entityId=%s in_dmgBeams=%s in_beams=%s', entityId, entityId in self._dmgBeams, entityId in self._beams)
        if entityId not in self._dmgBeams and entityId in self._beams:
            self._dmgBeams.setdefault(entityId, {})
            for beamName in self._beams[entityId]:
                loadKey = (entityId, beamName)
                if loadKey in self._loadingDmgBeams:
                    _logger.debug('showDamage: SKIP dup in-flight dmg load entId=%s beamName=%s', entityId, beamName)
                    continue
                dmgBeamName = self._dmgBeamName[beamName]
                prefabPath = getPrefabPath(_BEAM_NAME_TO_PREFAB_KEY.get(dmgBeamName))
                if not prefabPath:
                    _logger.warning('showDamage: no prefab registered for dmgBeamName=%s', dmgBeamName)
                    continue
                self._loadingDmgBeams.add(loadKey)
                CGF.loadAndCreatePrefab(prefabPath, self.spaceID, self._dmgSourcePosition, functools.partial(self._onDmgGameObjectLoaded, entityId, beamName))

    def _onGameObjectLoaded(self, entity, beamName, objects, queue):
        entId = entity.id
        self._loadingBeams.discard((entId, beamName))
        root = objects[0]
        beamComponent = queue.component(root, BeamRibbonComponent)
        if beamComponent is None:
            return False
        elif entity.id not in self._beams:
            _logger.debug('_onGameObjectLoaded: entId=%s NOT in _beams -> return False (CGF cancel)', entId)
            return False
        else:
            beamComponent.target = entity.entityGameObject.uuid
            newBeam = queue.gameObject(root)
            self._beams[entity.id][beamName] = newBeam
            _logger.debug('_onGameObjectLoaded: STORED entId=%s beamName=%s newBeam=%r', entity.id, beamName, newBeam)
            vehId = self._targetVehIds[entity.id]
            bwTarget = BigWorld.entity(vehId) if vehId else None
            bwSource = BigWorld.entity(self._sourceVehId) if self._sourceVehId else None
            if vehId and bwTarget is None and self._sourceVehId and bwSource is None:
                _logger.debug('_onGameObjectLoaded: DEACTIVATE on load (both src+target absent) entId=%s', entity.id)
                queue.deactivateGameObject(root)
                if entity.id in self._activeBeams:
                    self._activeBeams.remove(entity.id)
            return True

    def _onDmgGameObjectLoaded(self, entityId, beamName, objects, queue):
        self._loadingDmgBeams.discard((entityId, beamName))
        root = objects[0]
        dmgBeamComponent = queue.component(root, BeamRibbonComponent)
        beamComponent = None
        if entityId in self._beams and beamName in self._beams[entityId]:
            beamComponent = self._beams[entityId][beamName].findWrite(BeamRibbonComponent)
        if beamComponent and dmgBeamComponent is not None:
            dmgBeamComponent.target = self._dmgTargets[entityId].uuid
            newDmgBeam = queue.gameObject(root)
            self._dmgBeams[entityId][beamName] = newDmgBeam
            dmgBeamComponent.prevUpdateTime = beamComponent.prevUpdateTime
            _logger.debug('_onDmgGameObjectLoaded: STORED entId=%s beamName=%s lifetime=%s', entityId, beamName, dmgBeamComponent.lifetime)
            self._callbackDelayer.delayCallback(dmgBeamComponent.lifetime, functools.partial(self._removeDMGEffect, entityId, beamName))
            return True
        else:
            _logger.debug('_onDmgGameObjectLoaded: SKIPPED entId=%s beamName=%s -> return False', entityId, beamName)
            return False

    def _removeDMGEffect(self, entityId, beamName):
        _logger.debug('_removeDMGEffect: entId=%s beamName=%s in_dmgBeams=%s', entityId, beamName, entityId in self._dmgBeams)
        queue = CGF.CommandQueue(self.spaceID)
        if entityId in self._dmgBeams:
            for beam in self._dmgBeams[entityId].values():
                self._safeRemove(queue, beam)
                del self._dmgBeams[entityId][beamName]

            if not self._dmgBeams[entityId]:
                del self._dmgBeams[entityId]

    def _beamVisibilityUpdate(self):
        queue = CGF.CommandQueue(self.spaceID)
        srcAlive = bool(self._sourceVehId and BigWorld.entity(self._sourceVehId))
        for entityId, beamParam in list(self._pendingBeams.items()):
            applied = self._applyEffect(entityId, beamParam, queue)
            _logger.debug('_beamVisibilityUpdate: retry pending entId=%s -> applied=%s', entityId, applied)
            if applied:
                del self._pendingBeams[entityId]

        if srcAlive:
            for entityId in self._beams:
                self._setBeamActive(entityId, True, queue)

        else:
            for entId, vehId in self._targetVehIds.items():
                isAppear = BigWorld.entity(vehId) is not None
                self._setBeamActive(entId, isAppear, queue)

        return

    def _setBeamActive(self, entityId, isActive, queue):
        if entityId in self._beams:
            if isActive:
                if entityId not in self._activeBeams:
                    self._activeBeams.add(entityId)
                    for beam in self._beams[entityId].values():
                        self._safeActivate(queue, beam)

                    if entityId in self._dmgBeams:
                        for beam in self._dmgBeams[entityId].values():
                            self._safeActivate(queue, beam)

            elif entityId in self._activeBeams:
                self._activeBeams.remove(entityId)
                for beam in self._beams[entityId].values():
                    self._safeDeactivate(queue, beam)

                if entityId in self._dmgBeams:
                    for beam in self._dmgBeams[entityId].values():
                        self._safeDeactivate(queue, beam)

    def _onAvatarReady(self):
        _logger.debug('_onAvatarReady: beamParams_count=%s beamNames=%s', len(self.beamParams), [ p['beamName'] for p in self.beamParams ])
        for param in self.beamParams:
            self.applyEffects(param['beamName'])

    def _applyEffect(self, entityId, beamParam, queue):
        entity = BigWorld.entity(entityId)
        _logger.debug('_applyEffect: entId=%s beamName=%s targetVehId=%s entityResolved=%s', entityId, beamParam.beamName, beamParam.targetVehId, entity is not None)
        if entity:
            loadKey = (entityId, beamParam.beamName)
            if loadKey in self._loadingBeams:
                _logger.debug('_applyEffect: SKIP dup in-flight load entId=%s beamName=%s', entityId, beamParam.beamName)
                return True
            if beamParam.beamName in self._beams.get(entityId, {}):
                _logger.debug('_applyEffect: SKIP already loaded entId=%s beamName=%s', entityId, beamParam.beamName)
                return True
            if entityId not in self._dmgTargets:
                entityGO = entity.entityGameObject
                beamDmgTarget = queue.createGameObject()
                queue.createComponent(beamDmgTarget, HierarchyComponent, entityGO)
                queue.createComponent(beamDmgTarget, CGF.TransformComponent, Math.Vector3(0.0, self._DMG_BEAM_Y_OFFSET, 0.0))
                queue.createComponent(beamDmgTarget, GenericComponents.NodeFollowerComponent, '', entityGO.uuid)
                self._dmgTargets[entityId] = beamDmgTarget
            if entityId not in self._targetVehIds:
                self._targetVehIds[entityId] = beamParam.targetVehId
            prefabPath = getPrefabPath(_BEAM_NAME_TO_PREFAB_KEY.get(beamParam.beamName))
            if not prefabPath:
                _logger.warning('_applyEffect: no prefab registered for beamName=%s', beamParam.beamName)
                return False
            self._beams.setdefault(entityId, {})
            self._loadingBeams.add(loadKey)
            CGF.loadAndCreatePrefab(prefabPath, self.spaceID, beamParam.sourcePosition, functools.partial(self._onGameObjectLoaded, entity, beamParam.beamName))
            return True
        else:
            return False
