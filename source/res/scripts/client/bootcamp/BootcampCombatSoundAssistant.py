# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampCombatSoundAssistant.py
import BigWorld
import BattleReplay
import SoundGroups
from helpers import isPlayerAvatar
import MusicControllerWWISE

class BootcampCombatSoundAssistant(object):

    def __init__(self):
        self.__inited = False
        self.__combatMusic = None
        self.__avatar = None
        return

    def fini(self):
        self.muteCombatMusic()
        self.__inited = False
        self.__combatMusic = None
        return

    def onStartMission(self):
        self.__avatar = BigWorld.player()
        MusicControllerWWISE.g_musicController.skipArenaChanges = True
        self.__avatar.muteSounds(())

    def onStopMission(self):
        MusicControllerWWISE.g_musicController.skipArenaChanges = False
        self.__avatar = None
        return

    def muteSounds(self, sounds):
        if self.__avatar is None:
            return
        else:
            self.__avatar.muteSounds(sounds)
            return

    def muteCombatMusic(self):
        if not self.__inited:
            return
        else:
            if self.__combatMusic is not None and self.__combatMusic.isPlaying:
                self.__combatMusic.stop()
            return

    def playCombatMusic(self):
        if not self.__inited and not self._init():
            return
        else:
            if self.__combatMusic is not None and not self.__combatMusic.isPlaying and not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
                self.__combatMusic.play()
            return

    def playSound2D(self, soundID, checkTimeWarp=False):
        if not checkTimeWarp or not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            SoundGroups.g_instance.playSound2D(soundID)

    def _init(self):
        if not isPlayerAvatar():
            return False
        else:
            player = BigWorld.player()
            if player.arena is None:
                return False
            arenaType = player.arena.arenaType
            soundEventName = None
            if arenaType.wwmusicSetup is not None:
                soundEventName = arenaType.wwmusicSetup.get('wwmusicRelaxed', None)
            if soundEventName:
                self.__combatMusic = SoundGroups.g_instance.getSound2D(soundEventName)
            self.__inited = True
            return self.__inited
