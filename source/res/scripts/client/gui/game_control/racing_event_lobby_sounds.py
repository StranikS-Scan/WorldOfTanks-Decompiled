# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/racing_event_lobby_sounds.py
import WWISE
from gui.impl import backport
from gui.impl.gen import R

def _playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)


def _setSoundState(groupName, stateName, eventName=None):
    _playSound(eventName=eventName)
    if not groupName:
        return
    if not stateName:
        return
    WWISE.WW_setState(groupName, stateName)


class RacingEventLobbySounds(object):
    EV_FEST_META_RACE_MODE_ENTER = 'ev_fest_meta_race_mode_enter'
    EV_FEST_META_RACE_MODE_EXIT = 'ev_fest_meta_race_mode_exit'
    EV_FEST_META_RACE_RECOVERY = 'ev_fest_meta_race_recovery'
    EV_FEST_META_RACE_BUTTON = 'ev_fest_meta_race_button'
    EV_FEST_META_RACE_CUP_APPEAR = 'ev_fest_meta_race_cup_appear'
    EV_FEST_META_RACE_RESULT_CUP = 'ev_fest_meta_race_result_cup'
    EV_RACE_META_MUSIC_STATE = 'STATE_ev_race_meta_music'
    EV_RACE_META_MUSIC_STATE_ON = 'STATE_ev_race_meta_music_on'
    EV_RACE_META_MUSIC_STATE_OFF = 'STATE_ev_race_meta_music_off'
    EV_RACE_META_COLLECTION_STATE = 'STATE_ev_race_collection'
    EV_RACE_META_COLLECTION_STATE_OFF = 'STATE_ev_race_collection_off'
    EV_RACE_META_STATE = 'STATE_ev_race_meta'
    EV_RACE_META_STATE_ACTIVE = 'STATE_ev_race_meta_active'
    EV_RACE_META_STATE_INACTIVE = 'STATE_ev_race_meta_inactive'

    @staticmethod
    def playRaceButtonClicked():
        _playSound(RacingEventLobbySounds.EV_FEST_META_RACE_BUTTON)

    @staticmethod
    def playBattleResultCupAnimation():
        _playSound(RacingEventLobbySounds.EV_FEST_META_RACE_CUP_APPEAR)

    @staticmethod
    def playCupWon():
        _playSound(RacingEventLobbySounds.EV_FEST_META_RACE_RESULT_CUP)

    @staticmethod
    def playEventModeOn():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE, RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE_ON, RacingEventLobbySounds.EV_FEST_META_RACE_MODE_ENTER)

    @staticmethod
    def playEventModeOff():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE, RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE_OFF, RacingEventLobbySounds.EV_FEST_META_RACE_MODE_EXIT)

    @staticmethod
    def playCooldownOff():
        _playSound(RacingEventLobbySounds.EV_FEST_META_RACE_RECOVERY)

    @staticmethod
    def playRacingCollectionOff():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_COLLECTION_STATE, RacingEventLobbySounds.EV_RACE_META_COLLECTION_STATE_OFF)

    @staticmethod
    def playRacingMetaGameOn():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE, RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE_ON, backport.sound(R.sounds.ev_race_metagame_enter()))

    @staticmethod
    def playRacingMetaGameOff():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE, RacingEventLobbySounds.EV_RACE_META_MUSIC_STATE_OFF, backport.sound(R.sounds.ev_race_metagame_exit()))

    @staticmethod
    def playRacingMetaStateActive():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_STATE, RacingEventLobbySounds.EV_RACE_META_STATE_ACTIVE)

    @staticmethod
    def playRacingMetaStateInactive():
        _setSoundState(RacingEventLobbySounds.EV_RACE_META_STATE, RacingEventLobbySounds.EV_RACE_META_STATE_INACTIVE)
