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
from portal_common.portal_constants import BattleState
from PortalBattleStateComponent import PortalBattleStateComponent

@registerPortalManager(CGF.DomainOption.DomainClient)
class EffectsManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EffectsManager, self).__init__()
        self.__onPortalBattleStateChangedWasPlayed = False
        PortalBattleStateComponent.onBattleStateChanged += self.__onBattleStateChanged
        PortalBattleStateComponent.onBossFightFinished += self.__onBossFightFinished
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdateAlt += self._onBasePointsUpdate
        return

    def destroy(self):
        PortalBattleStateComponent.onBattleStateChanged -= self.__onBattleStateChanged
        PortalBattleStateComponent.onBossFightFinished -= self.__onBossFightFinished
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdateAlt -= self._onBasePointsUpdate
        return

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

    def _onBasePointsUpdate(self, team, baseID, lastData, currData):
        _, lastInvadersCnt, _ = lastData
        _, invadersCnt, capturingStopped = currData
        if capturingStopped or lastInvadersCnt > 0 and invadersCnt <= 0:
            pass
        elif lastInvadersCnt <= 0 and invadersCnt > 0:
            playVoiceover(GameplayVoiceovers.ON_ENEMY_CAPTURE_BASE)

    def __onBossFightFinished(self):
        playVoiceover(GameplayVoiceovers.PORTAL_DESTROYED)
