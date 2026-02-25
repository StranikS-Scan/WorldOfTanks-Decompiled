# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event_client_cgf/boosters/managers.py
import CGF
from GenericComponents import ParticleComponent
from BoosterComponent import BoosterComponent
from cosmic_event_common_cgf.helpers import registerCosmicEventManager
from cosmic_sound import CosmicBattleSounds

@registerCosmicEventManager(CGF.DomainOption.DomainClient)
class BoosterEffectManager(CGF.ComponentManager):
    __GEYSER_SPLASH_EFFECT = 'particles/Environment/interior/280_cosmic_geyser_26.eff'

    def __init__(self):
        super(BoosterEffectManager, self).__init__()
        BoosterComponent.onBoardApply += self.__onBoardApply
        BoosterComponent.onGeyserApply += self.__onGeyserApply

    def destroy(self):
        BoosterComponent.onBoardApply -= self.__onBoardApply
        BoosterComponent.onGeyserApply -= self.__onGeyserApply

    def __onBoardApply(self, boosterGO, position):
        CosmicBattleSounds.playBoardJump(position)

    def __onGeyserApply(self, boosterGO, position):
        component = boosterGO.findComponentByType(ParticleComponent)
        if component:
            boosterGO.removeComponent(component)
        rate = 1
        isAutoStart = True
        boosterGO.createComponent(ParticleComponent, self.__GEYSER_SPLASH_EFFECT, isAutoStart, rate)
        CosmicBattleSounds.playGeyserSplash(position)
