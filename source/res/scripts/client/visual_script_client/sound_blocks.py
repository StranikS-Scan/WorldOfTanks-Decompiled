# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/sound_blocks.py
import BigWorld
from visual_script import ASPECT
from visual_script.block import Block, Meta, EDITOR_TYPE
from visual_script.dependency import dependencyImporter
from visual_script.misc import errorVScript
from visual_script.slot_types import SLOT_TYPE, arrayOf
BattleReplay, SoundGroups, MusicControllerWWISE, helpers = dependencyImporter('BattleReplay', 'SoundGroups', 'MusicControllerWWISE', 'helpers')

class SoundMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class Play2DSound(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(Play2DSound, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._soundID = self._makeDataInputSlot('sound', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def blockName(cls):
        pass

    def captionText(self):
        pass

    def _execute(self):
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            SoundGroups.g_instance.playSound2D(self._soundID.getValue())
        self._out.call()


class SetMutedSounds(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetMutedSounds, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._soundIDs = self._makeDataInputSlot('sounds', arrayOf(SLOT_TYPE.STR))
        self._out = self._makeEventOutputSlot('out')

    def validate(self):
        return super(SetMutedSounds, self).validate()

    def _execute(self):
        avatar = BigWorld.player()
        if avatar:
            if self._soundIDs.hasValue():
                avatar.muteSounds(self._soundIDs.getValue())
            else:
                avatar.muteSounds(())


class PlayCombatMusic(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(PlayCombatMusic, self).__init__(*args, **kwargs)
        self._play = self._makeEventInputSlot('play', self._doPlay)
        self._stop = self._makeEventInputSlot('stop', self._doMute)
        self._musicId = self._makeDataInputSlot('music', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._musicId.setEditorData(['wwmusicLoading',
         'wwmusicRelaxed',
         'wwmusicIntensive',
         'wwmusicStop',
         'wwmusicEndbattleStop',
         'wwmusicResultWin',
         'wwmusicResultDrawn',
         'wwmusicResultDefeat'])
        self._out = self._makeEventOutputSlot('out')

    def _doPlay(self):
        self._execute(True)
        self._out.call()

    def _doMute(self):
        self._execute(False)
        self._out.call()

    def _execute(self, play):
        if helpers.isPlayerAvatar():
            avatar = BigWorld.player()
            arenaType = avatar.arena.arenaType
            if arenaType.wwmusicSetup is not None:
                musicId = self._musicId.getValue()
                soundEventName = arenaType.wwmusicSetup.get(musicId, None)
                if soundEventName:
                    self.__combatMusic = SoundGroups.g_instance.getSound2D(soundEventName)
                    if self.__combatMusic is not None:
                        if play:
                            if not self.__combatMusic.isPlaying and not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
                                self.__combatMusic.play()
                        elif self.__combatMusic.isPlaying:
                            self.__combatMusic.stop()
                        return
                elif musicId in arenaType.wwmusicSetup:
                    return
        errorVScript(self, "Can't play combat music")
        return


class SetMusicSkipArenaChanges(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetMusicSkipArenaChanges, self).__init__(*args, **kwargs)
        self._set = self._makeEventInputSlot('play', self._execute)
        self._skip = self._makeDataInputSlot('skip', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        MusicControllerWWISE.g_musicController.skipArenaChanges = self._skip.getValue()
        self._out.call()
