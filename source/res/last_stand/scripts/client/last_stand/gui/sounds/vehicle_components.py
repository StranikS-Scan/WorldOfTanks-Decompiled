# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/sounds/vehicle_components.py
import BigWorld
import SoundGroups
from last_stand.gui.sounds import SoundComponentBase, playSound
from last_stand.gui.sounds.sound_constants import BOTS_ENGINE, BOTS_EXPLOSION, LootSounds

class LSCommonEnemySounds(SoundComponentBase):

    def onAvatarReady(self):
        engineEvent = BOTS_ENGINE.get(self.parent.entity.typeDescriptor.name)
        if engineEvent is not None:
            self.parent.soundObject.play(engineEvent)
        return

    def onVehicleKilled(self, victimID, *_):
        if self.parent.entity.id == victimID:
            destroyEvent = BOTS_EXPLOSION.get(self.parent.entity.typeDescriptor.name)
            if destroyEvent is not None:
                SoundGroups.g_instance.playSoundPos(destroyEvent, self.parent.entity.position)
        return


class LSLootSounds(SoundComponentBase):

    def onLootSucceed(self, lootID, vehicleIDs):
        player = BigWorld.player()
        if player is None:
            return
        else:
            if player.playerVehicleID == self.parent.entity.id:
                playSound(LootSounds.Player.PICKUP_SUCCEED.get(lootID))
            elif not vehicleIDs or player.playerVehicleID in vehicleIDs:
                self.parent.soundObject.play(LootSounds.Ally.PICKUP_SUCCEED)
            return
