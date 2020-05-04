# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/se20/se20_gramophone_behaviour.py
import SoundGroups
from .se20_client_selectable_object_behaviour import SE20ClientSelectableObjectBehaviour

class SE20HangarGramophoneBehaviour(SE20ClientSelectableObjectBehaviour):
    _SOUND_START = 'ev_2020_secret_event_2_hangar_main_gramophone_start'
    _SOUND_PAUSE = 'ev_2020_secret_event_2_hangar_main_gramophone_pause'
    _SOUND_RESUME = 'ev_2020_secret_event_2_hangar_main_gramophone_resume'

    def __init__(self, owner):
        super(SE20HangarGramophoneBehaviour, self).__init__(owner)
        self._isPlaying = False
        self._sound = None
        return

    def onMouseClick(self):
        if self._sound is None:
            self._sound = SoundGroups.g_instance.getSound3D(self._owner.model.root, self._SOUND_START)
            self._sound.play()
            self._sound.setCallback(self._onSoundFinished)
            self._isPlaying = True
            animator = self._owner.animator
            if animator is not None:
                animator.unpause()
        elif self._isPlaying:
            SoundGroups.g_instance.playSound2D(self._SOUND_PAUSE)
            animator = self._owner.animator
            if animator is not None:
                animator.pause()
            self._isPlaying = False
        else:
            SoundGroups.g_instance.playSound2D(self._SOUND_RESUME)
            animator = self._owner.animator
            if animator is not None:
                animator.unpause()
            self._isPlaying = True
        return

    def onLeaveWorld(self):
        self._clearSound()

    def onAnimatorReady(self):
        animator = self._owner.animator
        if animator is not None:
            animator.pause()
        return

    def _onSoundFinished(self, _):
        self._clearSound()

    def _clearSound(self):
        animator = self._owner.animator
        if animator is not None:
            animator.pause()
        self._isPlaying = False
        if self._sound is not None:
            if self._sound.isPlaying:
                self._sound.stop()
            self._sound.releaseMatrix()
            self._sound = None
        return
