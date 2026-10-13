# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/effects/managers.py
import BigWorld
import CGF
from helpers import dependency
from cgf_script.managers_registrator import onAddedQuery
from skeletons.gui.battle_session import IBattleSessionProvider
from portal_common_cgf.portal_components import BossComponent
from portal_common_cgf.portal_helpers import registerPortalManager
from portal.sounds.sound_constants import GameplayVoiceovers
from portal.sounds.sound_helpers import playVoiceover
from portal_common.portal_constants import BattleState, PortalBattleLevel
from PortalBattleStateComponent import PortalBattleStateComponent

@registerPortalManager(CGF.DomainOption.DomainClient)
class EffectsManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EffectsManager, self).__init__()
        self.__onPortalBattleStateChangedWasPlayed = False
        PortalBattleStateComponent.onBattleStateChanged += self.__onBattleStateChanged
        PortalBattleStateComponent.onBossFightFinished += self.__onBossFightFinished

    def destroy(self):
        PortalBattleStateComponent.onBattleStateChanged -= self.__onBattleStateChanged
        PortalBattleStateComponent.onBossFightFinished -= self.__onBossFightFinished

    @property
    def battleState(self):
        return BigWorld.player().arena.arenaInfo.portalBattleStateComponent

    @onAddedQuery(CGF.GameObject, BossComponent)
    def onBossAdded(self, go, bossComponent):
        if self.battleState.battleState == BattleState.SUPER_BOSS_FIGHT:
            CGF.removeGameObject(go)

    def __onBattleStateChanged(self, battleState):
        if battleState == BattleState.BOSS_FIGHT and not self.__onPortalBattleStateChangedWasPlayed:
            playVoiceover(GameplayVoiceovers.PORTAL_FIRST_DAMAGE)
            self.__onPortalBattleStateChangedWasPlayed = True

    def __onBossFightFinished(self):
        player = BigWorld.player()
        battleLevel = 1
        if player and player.arena:
            battleLevel = player.arena.extraData.get('battleLevel', 1)
        if battleLevel == PortalBattleLevel.HARD:
            playVoiceover(GameplayVoiceovers.PORTAL_DESTROYED)
