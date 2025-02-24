# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/GeyserSplash.py
import BigWorld
import CGF
from GenericComponents import ParticleComponent
from helpers import dependency
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_sound import CosmicBattleSounds

class GeyserSplash(BigWorld.Entity):
    _cosmicController = dependency.descriptor(ICosmicEventBattleController)

    def onEnterWorld(self, *args):
        config = self._cosmicController.getModeSettings()
        effect = config.effects.get('geyserSplashEffect', {})
        effectPath = effect.get('path')
        rate = effect.get('rate', 1.0)
        isAutoStart = effect.get('autoStart', True)
        self.entityGameObject.createComponent(ParticleComponent, effectPath, isAutoStart, rate)
        self.entityGameObject.activate()
        CosmicBattleSounds.playGeyserSplash(self.position)

    def onLeaveWorld(self):
        self.__removeGO()

    def __removeGO(self):
        if self.entityGameObject is not None and self.entityGameObject.isValid():
            self.entityGameObject.removeComponentByType(ParticleComponent)
            CGF.removeGameObject(self.entityGameObject)
            self.entityGameObject = None
        return
