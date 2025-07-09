# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ShotsReceiver.py
import BigWorld
import CGF
import GenericComponents
import Math
import logging
from Event import Event
from cgf_components_common.material_component import MaterialComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_IDS, EFFECT_MATERIAL_INDEXES_BY_NAMES
from functools import partial
from constants import IS_EDITOR
from cgf_components.on_shot_components import EffectOnShotComponent, SoundOnShotComponent
from cgf_script.component_meta_class import registerReplicableComponent
_logger = logging.getLogger(__name__)
_DIR_UP = Math.Vector3(0.0, 1.0, 0.0)
if IS_EDITOR:

    class DynamicScriptComponent(object):
        pass


else:
    from BigWorld import DynamicScriptComponent

@registerReplicableComponent
class ShotsReceiver(DynamicScriptComponent):

    def __init__(self):
        super(ShotsReceiver, self).__init__()
        self.onShot = Event()

    def receiveShot(self, hitPoint, hitDir, speed, normal, shotID, effectIndex, prefabEffectIndex, shellType, shellCaliber, matKind, damagedDestructibles):
        self.onShot(hitPoint, hitDir, speed, normal, shotID, effectIndex, prefabEffectIndex, shellType, shellCaliber, matKind, damagedDestructibles)


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainServer)
class ShotReceiverManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, ShotsReceiver)
    def onShotsReceiverAdded(self, gameObject, shotsReceiver):
        shotsReceiver.onShot += partial(self.__onShot, gameObject)

    @onRemovedQuery(CGF.GameObject, ShotsReceiver)
    def onShotsReceiverRemoved(self, gameObject, shotsReceiver):
        shotsReceiver.onShot -= self.__onShot

    def __onShot(self, go, hitPoint, hitDir, speed, normal, shotID, effectIndex, prefabEffectIndex, shellType, shellCaliber, matKind, damagedDestructibles):
        effectQuery = CGF.Query(self.spaceID, (CGF.GameObject,
         ShotsReceiver,
         EffectOnShotComponent,
         GenericComponents.TransformComponent))
        soundQuery = CGF.Query(self.spaceID, (CGF.GameObject,
         ShotsReceiver,
         SoundOnShotComponent,
         GenericComponents.TransformComponent))
        explosionQuery = CGF.Query(self.spaceID, (CGF.GameObject, ShotsReceiver, CGF.No(EffectOnShotComponent)))
        normal.normalise()
        shot = {'hitPoint': hitPoint,
         'hitDir': hitDir,
         'speed': speed,
         'normal': normal,
         'shotID': int(shotID),
         'effectIndex': int(effectIndex),
         'prefabEffectIndex': int(prefabEffectIndex),
         'shellType': int(shellType),
         'caliber': float(shellCaliber),
         'matKind': int(matKind),
         'damagedDestructibles': damagedDestructibles}
        for gameObject, _, effectComponent, transform in effectQuery:
            if gameObject.id == go.id:
                self.__processEffect(gameObject, shot, effectComponent.effectPath, transform)

        for gameObject, _, soundComponent, transform in soundQuery:
            if gameObject.id == go.id:
                self.__processSound(gameObject, shot, soundComponent.soundPath, transform)

        for gameObject, _ in explosionQuery:
            if gameObject.id == go.id:
                self.__processExplosion(gameObject, shot)

    def __processExplosion(self, gameObject, shot):
        materialIdx = 0
        if EFFECT_MATERIAL_INDEXES_BY_IDS.has_key(shot['matKind']):
            materialIdx = EFFECT_MATERIAL_INDEXES_BY_IDS[shot['matKind']]
        else:
            material = gameObject.findComponentByType(MaterialComponent)
            if material:
                materialIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES[material.kind]
        BigWorld.player().explodeProjectile(shot['shotID'], shot['effectIndex'], shot['prefabEffectIndex'], materialIdx, shot['shellType'], shot['caliber'], shot['hitPoint'], shot['hitDir'], shot['speed'], shot['damagedDestructibles'])

    def __processEffect(self, gameObject, shot, effectPath, transform):
        position, normal = shot['hitPoint'], shot['normal']
        localTransform = transform.worldTransform
        localTransform.invert()
        localPosition = localTransform.applyPoint(position)
        localNormal = localTransform.applyVector(normal)
        localNormal.normalise()
        shotEffectTransform = Math.createVectorRotationMatrix(_DIR_UP, localNormal)
        shotEffectTransform.translation = localPosition
        CGF.loadGameObjectIntoHierarchy(effectPath, gameObject, shotEffectTransform)

    def __processSound(self, gameObject, shot, soundPath, transform):
        position = shot['hitPoint']
        localTransform = transform.worldTransform
        localTransform.invert()
        localPosition = localTransform.applyPoint(position)
        CGF.loadGameObjectIntoHierarchy(soundPath, gameObject, localPosition)
