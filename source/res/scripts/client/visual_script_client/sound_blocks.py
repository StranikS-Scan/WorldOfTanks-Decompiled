# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/sound_blocks.py
import BigWorld
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
from visual_script.misc import errorVScript, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE, arrayOf
BattleReplay, SoundGroups, MusicControllerWWISE, helpers, avatar_getter = dependencyImporter('BattleReplay', 'SoundGroups', 'MusicControllerWWISE', 'helpers', 'gui.battle_control.avatar_getter')

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
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class PlaySound(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(PlaySound, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._sound = self._makeDataInputSlot('soundToPlay', SLOT_TYPE.SOUND)
        self._out = self._makeEventOutputSlot('out')
        self._onSoundStop = self._makeEventOutputSlot('onSoundStop')

    def _execute(self):
        sound = self._sound.getValue()
        if sound:
            sound.setCallback(self.__onSoundEnd)
            if not sound.play():
                self._onSoundStop.call()
        self._out.call()

    def __onSoundEnd(self, sound):
        self._onSoundStop.call()


class StopSound(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(StopSound, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._sound = self._makeDataInputSlot('sound', SLOT_TYPE.SOUND)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        sound = self._sound.getValue()
        if sound:
            sound.stop()
        self._out.call()


class Create2DSound(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(Create2DSound, self).__init__(*args, **kwargs)
        self._soundName = self._makeDataInputSlot('soundName', SLOT_TYPE.STR)
        self._sound = self._makeDataOutputSlot('sound', SLOT_TYPE.SOUND, self._execute)

    def _execute(self):
        sound = SoundGroups.g_instance.getSound2D(self._soundName.getValue())
        if sound:
            self._sound.setValue(sound)


class Create3DSound(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(Create3DSound, self).__init__(*args, **kwargs)
        self._soundName = self._makeDataInputSlot('soundName', SLOT_TYPE.STR)
        self._soundObjectName = self._makeDataInputSlot('soundObjectName', SLOT_TYPE.STR)
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._sound = self._makeDataOutputSlot('sound', SLOT_TYPE.SOUND, self._execute)

    def _execute(self):
        sound = SoundGroups.g_instance.WWgetSoundPos(self._soundName.getValue(), self._soundObjectName.getValue(), self._position.getValue())
        if sound:
            self._sound.setValue(sound)


class SetMutedSounds(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetMutedSounds, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._soundNames = self._makeDataInputSlot('soundNames', arrayOf(SLOT_TYPE.STR))
        self._out = self._makeEventOutputSlot('out')

    def validate(self):
        return super(SetMutedSounds, self).validate()

    def _execute(self):
        avatar = BigWorld.player()
        if avatar:
            if self._soundNames.hasValue():
                avatar.muteSounds(self._soundNames.getValue())
            else:
                avatar.muteSounds(())
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


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

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class SetMusicSkipArenaChanges(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetMusicSkipArenaChanges, self).__init__(*args, **kwargs)
        self._set = self._makeEventInputSlot('play', self._execute)
        self._skip = self._makeDataInputSlot('skip', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        MusicControllerWWISE.g_musicController.skipArenaChanges = self._skip.getValue()
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class SetSoundRTPC(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetSoundRTPC, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._setValue)
        self._out = self._makeEventOutputSlot('out')
        self._soundIn = self._makeDataInputSlot('soundIn', SLOT_TYPE.SOUND)
        self._soundOut = self._makeDataOutputSlot('soundOut', SLOT_TYPE.SOUND, None)
        self._rtpcName = self._makeDataInputSlot('rtpcName', SLOT_TYPE.STR)
        self._rtpcValue = self._makeDataInputSlot('rtpcValue', SLOT_TYPE.FLOAT)
        return

    def _setValue(self):
        sound = self._soundIn.getValue()
        if sound:
            sound.setRTPC(self._rtpcName.getValue(), self._rtpcValue.getValue())
        self._soundOut.setValue(sound)
        self._out.call()


class SetSoundSwitch(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetSoundSwitch, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._setValue)
        self._out = self._makeEventOutputSlot('out')
        self._soundIn = self._makeDataInputSlot('soundIn', SLOT_TYPE.SOUND)
        self._soundOut = self._makeDataOutputSlot('soundOut', SLOT_TYPE.SOUND, None)
        self._switchName = self._makeDataInputSlot('switchName', SLOT_TYPE.STR)
        self._switchValue = self._makeDataInputSlot('switchValue', SLOT_TYPE.STR)
        return

    def _setValue(self):
        sound = self._soundIn.getValue()
        if sound:
            sound.setSwitch(self._switchName.getValue(), self._switchValue.getValue())
        self._soundOut.setValue(sound)
        self._out.call()


class GetSoundName(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(GetSoundName, self).__init__(*args, **kwargs)
        self._sound = self._makeDataInputSlot('sound', SLOT_TYPE.SOUND)
        self._name = self._makeDataOutputSlot('name', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        sound = self._sound.getValue()
        if sound:
            self._name.setValue(sound.name)
        else:
            self._name.setValue('')


class IsSoundPlaying(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(IsSoundPlaying, self).__init__(*args, **kwargs)
        self._sound = self._makeDataInputSlot('sound', SLOT_TYPE.SOUND)
        self._isPlaying = self._makeDataOutputSlot('isPlaying', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        sound = self._sound.getValue()
        if sound:
            self._isPlaying.setValue(sound.isPlaying)
        else:
            self._isPlaying.setValue(False)


class PlayGlobalSound(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(PlayGlobalSound, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._sound = self._makeDataInputSlot('soundToPlay', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        SoundGroups.g_instance.playSound2D(self._sound.getValue())
        self._out.call()


class SetGlobalSoundSwitch(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(SetGlobalSoundSwitch, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._setValue)
        self._out = self._makeEventOutputSlot('out')
        self._switchName = self._makeDataInputSlot('switchName', SLOT_TYPE.STR)
        self._switchValue = self._makeDataInputSlot('switchValue', SLOT_TYPE.STR)

    def _setValue(self):
        SoundGroups.g_instance.setState(self._switchName.getValue(), self._switchValue.getValue())
        self._out.call()


class PlaySoundNotification(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(PlaySoundNotification, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self._eventName = self._makeDataInputSlot('eventName', SLOT_TYPE.STR)

    def _execute(self):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications is not None:
            soundNotifications.play(self._eventName.getValue())
        self._out.call()
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
