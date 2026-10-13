# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleSoundComponent.py
from __future__ import absolute_import
import BigWorld
import SoundGroups
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from halloween_common.halloween_constants import BOSS_ROLE_TAG, PLAYERS_TEAM, ATTACK_REASON, ARENA_BONUS_TYPE
from halloween.gui.sounds import ComponentsHolder
from halloween.gui.sounds.vehicle_components import HWBossBattleSounds, HWCommonEnemySounds, HWSoulsContainerSounds, HWHexapodBossBattleSounds
from halloween.gui.sounds.sound_constants import VEHICLE_OBJ_NAME_PATTERN
from skeletons.gui.battle_session import IBattleSessionProvider
_VEHICLE_SOUND_COMPONENTS = [(HWBossBattleSounds, lambda parent: parent.isBoss),
 (HWHexapodBossBattleSounds, lambda parent: parent.isBoss and parent.arena.bonusType != ARENA_BONUS_TYPE.HALLOWEEN),
 (HWCommonEnemySounds, lambda parent: parent.isEnemy),
 (HWSoulsContainerSounds, lambda parent: parent.hwSoulsContainer is not None)]

class HWVehicleSoundComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWVehicleSoundComponent, self).__init__()
        self._components = ComponentsHolder([], self)
        self._soundObject = SoundGroups.g_instance.WWgetSoundObject(VEHICLE_OBJ_NAME_PATTERN.format(self.entity.id), self.entity.matrix)

    def onDestroy(self):
        self._components.onDestroy()
        self.soundObject.stopAll()
        BigWorld.player().arena.onVehicleKilled -= self._onVehicleKilled
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossLivesChanged -= self._onBossLivesChanged
        super(HWVehicleSoundComponent, self).onDestroy()

    @property
    def soundObject(self):
        return self._soundObject

    @property
    def isBoss(self):
        return BOSS_ROLE_TAG in self.entity.typeDescriptor.type.tags

    @property
    def isEnemy(self):
        return self.sessionProvider.getArenaDP().getVehicleInfo(self.entity.id).team != PLAYERS_TEAM

    @property
    def hwSoulsContainer(self):
        return self.entity.dynamicComponents.get('hwSoulsContainer')

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    @property
    def arena(self):
        player = BigWorld.player()
        return None if not player else player.arena

    def _onAvatarReady(self):
        componentList = [ component for component, condition in _VEHICLE_SOUND_COMPONENTS if condition(self) ]
        self._components = ComponentsHolder(componentList, self)
        self._components.onAvatarReady()
        if self.isBoss:
            arenaSoundComponent = self._arenaSoundComponent
            if arenaSoundComponent is not None:
                arenaSoundComponent.onBossEnterWorld(self.entity)
        BigWorld.player().arena.onVehicleKilled += self._onVehicleKilled
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossLivesChanged += self._onBossLivesChanged
        return

    def onBossDamageReceived(self, attackerID, attackReasonID, damage):
        attackReason = ATTACK_REASON.getValue(attackReasonID)
        arenaSoundComponent = self._arenaSoundComponent
        if arenaSoundComponent is not None:
            arenaSoundComponent.onShotAtBoss(attackerID, attackReason, damage)
        self._components.call('onBossDamageReceived', attackerID, attackReason, damage)
        return

    def _onVehicleKilled(self, victimID, *args):
        if self.entity.id == victimID:
            self.soundObject.stopAll()
        self._components.call('onVehicleKilled', victimID, *args)

    def _onBossLivesChanged(self):
        self.soundObject.stopAll()
        self._components.call('onBossLivesChanged')

    @property
    def _arenaSoundComponent(self):
        return BigWorld.player().arena.arenaInfo.dynamicComponents.get('HWArenaSoundComponent')
