# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/client/Ball.py
import BigWorld
import Math
import ResMgr
from Math import Vector3, Matrix
import Event
import SoundGroups
from PhysicalObject import PhysicalObject
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR
from event_special_effects import BallEffectType
from helpers import dependency
from helpers.bound_effects import ModelBoundEffects
from skeletons.gui.battle_session import IBattleSessionProvider
from svarog_script.py_component_system import ComponentSystem, ComponentDescriptor
from vehicle_systems.tankStructure import ColliderTypes, TankPartNames
_FOOTBALL_CONFIG_SECTION = 'scripts/dynamic_objects.xml/footballBattle'

class Ball(PhysicalObject, ComponentSystem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    collisions = ComponentDescriptor()
    __objectName = 'BallEntityModel'

    def __init__(self):
        PhysicalObject.__init__(self)
        ComponentSystem.__init__(self)
        self.filter = BigWorld.WGBallFilter()
        self.__eventEffectsStorage = None
        self.__hitEffects = None
        self.__soundObject = None
        self.__collisionName = ''
        self.__highlightCylinder = None
        self.__ballExplosionDelay = 0.0
        self.onDestroyBall = Event.Event()
        self.onRespawnBall = Event.Event()
        self.__setPickingEnabled(True)
        return

    def isAlive(self):
        return False

    def drawEdge(self):
        pass

    def removeEdge(self):
        pass

    def prerequisites(self):
        self.__readCfg()
        spaceID = BigWorld.player().spaceID
        assembler = BigWorld.CompoundAssembler(Ball.__objectName, spaceID)
        assembler.addRootPart(self.__modelName, TankPartNames.TURRET)
        collisionModels = ((TankPartNames.getIdx(TankPartNames.TURRET), self.__collisionName),)
        collisionAssembler = BigWorld.CollisionAssembler(collisionModels, spaceID)
        prereqs = [assembler, collisionAssembler]
        self.__eventEffectsStorage = self._sessionProvider.dynamic.footballCtrl.eventEffectsStorage
        self.__highlightCylinder = self.__eventEffectsStorage.getHighlightCylinderForEntity(self)
        prereqs.extend(self.__highlightCylinder.prerequisites())
        prereqs.extend(self.__eventEffectsStorage.prerequisites())
        return prereqs

    def onEnterWorld(self, prereqs):
        self.model = prereqs[Ball.__objectName]
        self.model.matrix = self.matrix
        self.collisions = prereqs['collisionAssembler']
        collisionData = ((TankPartNames.getIdx(TankPartNames.TURRET), self.model.matrix),)
        self.collisions.connect(self.id, ColliderTypes.DYNAMIC_COLLIDER, collisionData)
        self.__soundObject = SoundGroups.g_instance.WWgetSoundObject('ballObject', self.model.matrix, (0.0, 0.0, 0.0))

        def _createMatrixProvider(entity):
            translationOnlyMP = Math.WGTranslationOnlyMP()
            translationOnlyMP.source = entity.matrix
            boundMP = Math.WGBoundMatrixProvider()
            boundMP.source = translationOnlyMP
            entityPos = Math.Matrix(entity.matrix).translation
            down = Math.Vector3(0.0, -1.0, 0.0)
            collisionResult = BigWorld.wg_collideSegment(BigWorld.player().spaceID, entityPos, entityPos + down * 1000.0, 0, 8)
            y = collisionResult.closestPoint.y if collisionResult else entityPos.y
            boundMP.minBound = Vector3(-100000.0, y, -100000.0)
            boundMP.maxBound = Vector3(100000.0, y, 100000.0)
            return boundMP

        self.__highlightCylinder.keepPrereqs(prereqs)
        self.__highlightCylinder.attachTo(_createMatrixProvider(self))
        self.__eventEffectsStorage.keepPrereqs(prereqs)
        self.__hitEffects = _HitEffects(self.model, self.__eventEffectsStorage)
        ComponentSystem.activate(self)
        BigWorld.player().arena.onReturnToPlay += self.respawnBall
        self._sessionProvider.dynamic.footballEntitiesCtrl.registerEntity(self)
        self.__setVisibleOnMinimap(True, isImmediate=False)

    def onLeaveWorld(self):
        self.__setVisibleOnMinimap(False)
        self._sessionProvider.dynamic.footballEntitiesCtrl.unregisterEntity(self)
        ComponentSystem.deactivate(self)
        ComponentSystem.destroy(self)
        BigWorld.player().arena.onReturnToPlay -= self.respawnBall
        if self.__soundObject is not None:
            self.__soundObject.stopAll()
        self.__soundObject = None
        if self.__highlightCylinder is not None:
            self.__highlightCylinder.destroy()
        self.__highlightCylinder = None
        return

    def showDamageFromShot(self, attackerID, point, team):
        self.__hitEffects.showHit(point, attackerID, team)
        self.playSoundOnShot(attackerID)

    def playSoundOnShot(self, attackerID):
        self.__playTerrainEffect(BallEffectType.HIT_SOUND, attackerID=attackerID)

    def playSoundOnCollision(self, energy):
        self.__soundObject.setRTPC('RTPC_ext_ev_football_drop_energy', energy)
        self.__soundObject.play('ev_collision_with_ball')

    def explodeBall(self, position):
        self.__explodeBall(position)

    def respawnBall(self, data):
        self.__respawnBall()

    def showRam(self, point):
        self.__playTerrainEffect(BallEffectType.RAM, position=point)

    def __setPickingEnabled(self, enable):
        self.targetCaps = [1] if enable else [0]

    def __explodeBall(self, position):
        self.onDestroyBall()
        self.__playTerrainEffect(BallEffectType.DESTRUCTION, position=position)
        self.__setVisibile(False)

    def __respawnBall(self):
        self.__setVisibile(True)
        self.__playTerrainEffect(BallEffectType.RESPAWN)
        self.onRespawnBall()

    def __playTerrainEffect(self, effectType, **kwargs):
        effect = self.__eventEffectsStorage.getBallEffect(effectType)
        if effect is not None:
            position = kwargs.pop('position', None) or self.position
            BigWorld.player().terrainEffects.addNew(position, effect.effectsList, effect.keyPoints, None, **kwargs)
        return

    def __setVisibile(self, visible):
        self.__setVisibleInWorld(visible)
        self.__setVisibleOnMinimap(visible)
        self.__setPickingEnabled(visible)

    def __setVisibleInWorld(self, visible):
        if self.model is not None:
            self.model.visible = visible
        if self.__highlightCylinder is not None:
            self.__highlightCylinder.visible = visible
        return

    def __setVisibleOnMinimap(self, visible, isImmediate=True):
        if visible:
            self._sessionProvider.startPhysicalObjectVisual(self.proxy, isImmediate)
        else:
            self._sessionProvider.stopPhysicalObjectVisual(self.proxy.id)

    def __readCfg(self):
        dataSec = ResMgr.openSection(_FOOTBALL_CONFIG_SECTION)
        self.__modelName = dataSec.readString('football', '')
        self.__collisionName = dataSec.readString('collision', self.__modelName)


class _HitEffects(ModelBoundEffects):

    def __init__(self, model, effectsStorage):
        super(_HitEffects, self).__init__(model)
        self.__effectsStorage = effectsStorage

    def showHit(self, position, attackerID, _):
        avatar = BigWorld.player()
        isPlayerVehicle = avatar.isVehicleAlive and attackerID == avatar.playerVehicleID
        effect = self.__getEffect(attackerID, isPlayerVehicle)
        if effect is None:
            LOG_ERROR('[Football] Cannot find ball hit effect for attackerID = {}', attackerID)
            return
        else:
            self.addNew(position, effect.effectsList, effect.keyPoints, attackerID=attackerID, isPlayerVehicle=isPlayerVehicle, showDecal=False)
            return

    def addNew(self, position, effectsList, keyPoints, waitForKeyOff=False, **kwargs):
        shotMatrix = Matrix()
        shotMatrix.setTranslate(position)
        super(_HitEffects, self).addNew(shotMatrix, effectsList, keyPoints, waitForKeyOff, **kwargs)

    def __getEffect(self, vehicleID, isPlayerVehicle):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is not None:
            effect = self.__effectsStorage.getBallHitEffectForVehicle(vehicle, isPlayerVehicle)
        else:
            effect = None
        return effect
