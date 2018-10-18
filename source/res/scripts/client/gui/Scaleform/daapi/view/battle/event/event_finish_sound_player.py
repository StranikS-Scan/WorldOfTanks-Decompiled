# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_finish_sound_player.py
from gui.Scaleform.daapi.view.battle.shared.finish_sound_player import FinishSoundPlayer, _SOUND_EVENTS
_SOUND_EVENT_OVERRIDES = {_SOUND_EVENTS.TIME_IS_OVER: 'ev_halloween_end_battle'}

class EventFinishSoundPlayer(FinishSoundPlayer):

    def _playSound(self, soundID):
        if soundID in _SOUND_EVENT_OVERRIDES:
            soundID = _SOUND_EVENT_OVERRIDES[soundID]
        super(EventFinishSoundPlayer, self)._playSound(soundID)
