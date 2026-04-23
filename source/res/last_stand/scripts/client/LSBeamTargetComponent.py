# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBeamTargetComponent.py
from __future__ import absolute_import
import CGF
import BigWorld
import GenericComponents
import Math
import functools
from script_component.DynamicScriptComponent import DynamicScriptComponent
from BeamRibbonComponent import BeamRibbonComponent
from gui.shared.utils.TimeInterval import TimeInterval
from helpers.CallbackDelayer import CallbackDelayer

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
        self._step = 0.0
        return

    def onDestroy(self):
        self.removeEffects([])
        self._updateTI.stop()
        self._callbackDelayer.destroy()

    def applyEffects(self, beamName):
        beamParam = None
        for param in self.beamParams:
            if param['beamName'] == beamName:
                beamParam = param

        if not beamParam:
            return
        else:
            sourcePosition = beamParam['sourcePosition']
            targetEntIds = beamParam['entIDs']
            targetVehIds = beamParam['vehIDs']
            self._sourceVehId = beamParam['sourceVehicleID']
            self._dmgSourcePosition = Math.Vector3(sourcePosition)
            self._dmgSourcePosition.y += self._DMG_BEAM_Y_OFFSET
            self._dmgBeamName[beamName] = beamParam['dmgBeamName']
            for idx, entityId in enumerate(targetEntIds):
                beamParam = BeamParam(beamName, targetVehIds[idx], sourcePosition)
                isApplied = self._applyEffect(entityId, beamParam)
                if not isApplied:
                    self._pendingBeams[entityId] = BeamParam(beamName, targetVehIds[idx], sourcePosition)

            return

    def removeEffects(self, vehiclesIds):
        if not vehiclesIds:
            for beams in self._beams.values():
                for beam in beams.values():
                    CGF.removeGameObject(beam)

            self._beams = {}
            for beams in self._dmgBeams.values():
                for beam in beams.values():
                    CGF.removeGameObject(beam)

            self._dmgBeams = {}
            self._activeBeams.clear()
        else:
            for id in vehiclesIds:
                if id in self._beams:
                    for beam in self._beams[id].values():
                        CGF.removeGameObject(beam)

                    del self._beams[id]
                if id in self._dmgBeams:
                    for beam in self._dmgBeams[id].values():
                        CGF.removeGameObject(beam)

                    del self._dmgBeams[id]
                if id in self._activeBeams:
                    self._activeBeams.remove(id)

    def showDamage(self, entityId):
        if entityId not in self._dmgBeams and entityId in self._beams:
            self._dmgBeams[entityId] = {}
            for beamName in self._beams[entityId]:
                dmgBeamName = self._dmgBeamName[beamName]
                CGF.loadGameObject('last_stand/content/CGFPrefabs/beams/{}.prefab'.format(dmgBeamName), self.spaceID, self._dmgSourcePosition, lambda obj, _entityId=entityId, _beamName=beamName: self._onDmgGameObjectLoaded(obj, _entityId, _beamName))

    def _onGameObjectLoaded(self, gameObject, entity, beamName):
        beamComponent = gameObject.findComponentByType(BeamRibbonComponent, '')
        if beamComponent:
            beamComponent.target = entity.entityGameObject
            if entity.id in self._beams:
                if beamName in self._beams[entity.id]:
                    CGF.removeGameObject(self._beams[entity.id][beamName])
                self._beams[entity.id][beamName] = gameObject
                self._setBeamActive(entity.id, True)
                vehId = self._targetVehIds[entity.id]
                if vehId and BigWorld.entity(vehId) is None and self._sourceVehId and BigWorld.entity(self._sourceVehId) is None:
                    self._setBeamActive(entity.id, False)
            else:
                CGF.removeGameObject(gameObject)
        return

    def _onDmgGameObjectLoaded(self, gameObject, entityId, beamName):
        dmgBeamComponent = gameObject.findComponentByType(BeamRibbonComponent, '')
        beamComponent = None
        if entityId in self._beams and beamName in self._beams[entityId]:
            beamComponent = self._beams[entityId][beamName].findComponentByType(BeamRibbonComponent, '')
        if beamComponent and dmgBeamComponent:
            dmgBeamComponent.target = self._dmgTargets[entityId]
            if beamName in self._dmgBeams[entityId]:
                CGF.removeGameObject(self._beams[entityId][beamName])
            self._dmgBeams[entityId][beamName] = gameObject
            dmgBeamComponent.prevUpdateTime = beamComponent.prevUpdateTime
            self._callbackDelayer.delayCallback(dmgBeamComponent.lifetime, functools.partial(self._removeDMGEffect, entityId, beamName))
        else:
            CGF.removeGameObject(gameObject)
        return

    def _removeDMGEffect(self, entityId, beamName):
        if entityId in self._dmgBeams:
            for beam in self._dmgBeams[entityId].values():
                CGF.removeGameObject(beam)
                del self._dmgBeams[entityId][beamName]

            if not self._dmgBeams[entityId]:
                del self._dmgBeams[entityId]

    def _beamVisibilityUpdate(self):
        for entityId, beamParam in list(self._pendingBeams.items()):
            if self._applyEffect(entityId, beamParam):
                del self._pendingBeams[entityId]

        if self._sourceVehId and BigWorld.entity(self._sourceVehId):
            for entityId in self._beams:
                self._setBeamActive(entityId, True)

        else:
            for entId, vehId in self._targetVehIds.items():
                isAppear = BigWorld.entity(vehId) is not None
                self._setBeamActive(entId, isAppear)

        return

    def _setBeamActive(self, entityId, isActive):
        if entityId in self._beams:
            if isActive:
                if entityId not in self._activeBeams:
                    self._activeBeams.add(entityId)
                    for beam in self._beams[entityId].values():
                        beam.activate()

                    if entityId in self._dmgBeams:
                        for beam in self._dmgBeams[entityId].values():
                            beam.activate()

            elif entityId in self._activeBeams:
                self._activeBeams.remove(entityId)
                for beam in self._beams[entityId].values():
                    beam.deactivate()

                if entityId in self._dmgBeams:
                    for beam in self._dmgBeams[entityId].values():
                        beam.deactivate()

    def _onAvatarReady(self):
        for param in self.beamParams:
            self.applyEffects(param['beamName'])

    def _applyEffect(self, entityId, beamParam):
        entity = BigWorld.entity(entityId)
        if entityId not in self._beams:
            self._beams[entityId] = {}
        if entity:
            if entityId not in self._dmgTargets:
                entityGO = entity.entityGameObject
                beamDmgTarget = CGF.GameObject(self.spaceID)
                beamDmgTarget.createComponent(GenericComponents.HierarchyComponent, entityGO)
                beamDmgTarget.createComponent(GenericComponents.TransformComponent, Math.Vector3(0.0, self._DMG_BEAM_Y_OFFSET, 0.0))
                beamDmgTarget.createComponent(GenericComponents.NodeFollower, '', entityGO)
                self._dmgTargets[entityId] = beamDmgTarget
            if entityId not in self._targetVehIds:
                self._targetVehIds[entityId] = beamParam.targetVehId
            if beamParam.beamName not in self._beams[entityId]:
                CGF.loadGameObject('last_stand/content/CGFPrefabs/beams/{}.prefab'.format(beamParam.beamName), self.spaceID, beamParam.sourcePosition, lambda obj, _entity=entity, _beamName=beamParam.beamName: self._onGameObjectLoaded(obj, _entity, _beamName))
            return True
        return False
