# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AimSound.py
import SoundGroups

class AimSound(object):
    TARGET_UNLOCKED = 0
    TARGET_LOCKED = 1
    TARGET_LOST = 2
    aimSounds = (('ui_target_unlocked', 'target_unlocked'), ('ui_target_locked', 'target_captured'), ('ui_target_lost', 'target_lost'))

    @staticmethod
    def play(state, playerNotifications=None):
        sounds = AimSound.aimSounds[state]
        SoundGroups.g_instance.playSound2D(sounds[0])
        if playerNotifications is not None:
            playerNotifications.play(sounds[1])
        return
