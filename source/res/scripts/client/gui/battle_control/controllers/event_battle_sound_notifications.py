# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_battle_sound_notifications.py
import BigWorld
import SoundGroups
from PlayerEvents import g_playerEvents
from constants import EQUIPMENT_STAGES
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider

class EventBattleSoundNotifications(IViewComponentsController):
    SHELL_NOTIFICATION_VALUE = 4
    battleSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self._playersLives = {}
        super(EventBattleSoundNotifications, self).__init__()

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_SOUND_NOTIFICATIONS

    def startControl(self, *args):
        g_playerEvents.onAvatarBecomePlayer += self._addListeners
        BigWorld.player().arena.onCombatEquipmentUsed += self._onEquipmentUsed

    def stopControl(self):
        self._removeListeners()
        g_playerEvents.onAvatarBecomePlayer -= self._addListeners
        BigWorld.player().arena.onCombatEquipmentUsed -= self._onEquipmentUsed

    def setViewComponents(self, *components):
        pass

    def clearViewComponents(self):
        pass

    def _addListeners(self):
        ammoCtrl = self.battleSessionProvider.shared.ammo
        ammoCtrl.onShellsUpdated += self._onShellsUpdated
        respawnCrtl = self.battleSessionProvider.dynamic.respawn
        respawnCrtl.onPlayerRespawnLivesUpdated += self._onPlayerLivesUpdate
        respawnCrtl.onTeammateRespawnLivesUpdated += self._onTeammateLivesUpdate
        eqCtrl = self.battleSessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self._onEquipmentUpdated
        return

    def _removeListeners(self):
        ammoCtrl = self.battleSessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsUpdated -= self._onShellsUpdated
        respawnCrtl = self.battleSessionProvider.dynamic.respawn
        respawnCrtl.onPlayerRespawnLivesUpdated -= self._onPlayerLivesUpdate
        respawnCrtl.onTeammateRespawnLivesUpdated -= self._onTeammateLivesUpdate
        eqCtrl = self.battleSessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self._onEquipmentUpdated
        return

    def _onShellsUpdated(self, intCD, quantity, *args):
        ammoCtrl = self.battleSessionProvider.shared.ammo
        totalAmmo = sum([ shell[2] for shell in ammoCtrl.getOrderedShellsLayout() ])
        if totalAmmo == self.SHELL_NOTIFICATION_VALUE:
            getSoundNotifications().play('hb1_shells_running_out')

    def _onEquipmentUsed(self, shooterID, equipmentID):
        if shooterID == BigWorld.player().playerVehicleID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if equipment.activationSoundNotification is not None:
                getSoundNotifications().play(equipment.activationSoundNotification)
        return

    def _onEquipmentUpdated(self, intCD, item):
        equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
        if not equipment:
            return
        activatedStages = (EQUIPMENT_STAGES.DEPLOYING,
         EQUIPMENT_STAGES.PREPARING,
         EQUIPMENT_STAGES.ACTIVE,
         EQUIPMENT_STAGES.COOLDOWN)
        if item.getPrevStage() == EQUIPMENT_STAGES.READY and item.getStage() in activatedStages:
            if equipment.activationWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.activationWWSoundFeedback)
        elif item.getPrevStage() == EQUIPMENT_STAGES.PREPARING and item.getStage() in activatedStages:
            if equipment.targetConfirmWWSoundFeedback:
                SoundGroups.g_instance.playSound2D(equipment.targetConfirmWWSoundFeedback)
        elif item.getPrevStage() == EQUIPMENT_STAGES.ACTIVE and item.getStage() != EQUIPMENT_STAGES.ACTIVE:
            if equipment.deactivationSoundNotification:
                getSoundNotifications().play(equipment.deactivationSoundNotification)

    def _onPlayerLivesUpdate(self, playerLivesLeft):
        playerVehicleID = BigWorld.player().playerVehicleID
        prevLives = self._playersLives.get(playerVehicleID)
        vehicle = BigWorld.entities[playerVehicleID]
        self._playersLives[playerVehicleID] = playerLivesLeft
        if prevLives is not None and playerLivesLeft == 0:
            getSoundNotifications().play('hb1_lost_all_own_lives')
        elif prevLives is not None and not vehicle.isAlive():
            getSoundNotifications().play('hb1_player_lost_life')
        return

    def _onTeammateLivesUpdate(self, teammateVehId, teammateLivesLeft):
        prevLives = self._playersLives.get(teammateVehId)
        self._playersLives[teammateVehId] = teammateLivesLeft
        if prevLives is not None and teammateLivesLeft == 0 and teammateVehId != BigWorld.player().playerVehicleID:
            getSoundNotifications().play('hb1_ally_lost_all_lives')
        return
