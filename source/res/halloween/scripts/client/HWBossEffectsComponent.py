# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBossEffectsComponent.py
import BigWorld
import logging
import Math
from effect_controller import EffectController
from helpers import newFakeModel
_logger = logging.getLogger(__name__)

class HWBossEffectsComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *args, **kwargs):
        self._deathFakeModel = None
        self._turretFakeModel = None
        self._hullFakeModel = None
        self._deathEffect = EffectController('boss_death')
        self._turretHitEffect = EffectController('boss_turret_hit')
        self._hullHitEffect = EffectController('boss_hull_hit')
        return

    def playHitEffect(self, componentName):
        self.__checkAttachedModels()
        if componentName in ('hull', 'chassis'):
            self._hullHitEffect.playSequence(self._hullFakeModel)
        elif componentName == 'turret':
            self._turretHitEffect.playSequence(self._turretFakeModel)

    def __checkAttachedModels(self):
        if not self._hullFakeModel:
            self._hullFakeModel = newFakeModel()
            bindNode = self.entity.model.node('hull')
            self._hullFakeModel.position = Math.Matrix(bindNode).applyToOrigin()
            bindNode.attach(self._hullFakeModel)
        if not self._turretFakeModel:
            self._turretFakeModel = newFakeModel()
            bindNode = self.entity.model.node('turret')
            self._turretFakeModel.position = Math.Matrix(bindNode).applyToOrigin()
            bindNode.attach(self._turretFakeModel)

    def playDeathEffect(self):
        self._deathFakeModel = newFakeModel()
        self._deathFakeModel.position = self.entity.position
        BigWorld.player().addModel(self._deathFakeModel)
        self._deathEffect.playSequence(self._deathFakeModel)

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        self._deathEffect.reset()
        self._turretHitEffect.reset()
        self._hullHitEffect.reset()
        self._hullFakeModel = None
        self._turretFakeModel = None
        self._deathFakeModel = None
        return
