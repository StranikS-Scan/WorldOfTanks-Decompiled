# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_jukebox_controller.py
from collections import deque
from random import randint, choice
import typing
import SoundGroups
import math_utils
from Event import Event, EventManager
from skeletons.new_year import IJukeboxController

class JukeboxSides(object):
    A = 'sideA'
    B = 'sideB'


class JukeboxStateMachineConstants(object):
    IDLE_NODE = 'idle'
    START_TRIGGER = 'start'
    HIGHLIGHT_TRIGGER = {JukeboxSides.A: 'over_a',
     JukeboxSides.B: 'over_b'}
    FADE_TRIGGER = {JukeboxSides.A: 'out_a',
     JukeboxSides.B: 'out_b'}
    CLICK_TRIGGER = {JukeboxSides.A: 'click_a',
     JukeboxSides.B: 'click_b'}
    SUSPEND_TRIGGER = 'suspend'
    PLAY_EVENT = 'Play'
    IDLE_EVENT = 'Idle'
    STOP_EVENT = 'Stop'
    ENABLE_HIGHLIGHT_EVENTS = (PLAY_EVENT, IDLE_EVENT)


class _JukeboxConstants(object):
    MIN_FIRST_IDLE = 60
    MAX_FIRST_IDLE = 120
    MIN_OTHERS_IDLE = 120
    MAX_OTHERS_IDLE = 240
    PLAYLIST_A = 'playlistA'
    PLAYLIST_B = 'playlistB'
    PLAYLIST_C = 'playlistC'
    AUTO_PLAYLISTS = (PLAYLIST_A, PLAYLIST_B)
    PLAYLIST_BY_SIDE = {JukeboxSides.A: PLAYLIST_A,
     JukeboxSides.B: PLAYLIST_B}
    SIDE_BY_PLAYLIST = {playlist:side for side, playlist in PLAYLIST_BY_SIDE.iteritems()}
    CLICK_COUNT_FOR_PLAY_PLAYLIST_C = 9
    TRACK_LENGTH = 55


JUKEBOX_MUSIC = {_JukeboxConstants.PLAYLIST_A: [ 'hangar_newyear_music_jukebox_playlist_a_song_{:02d}'.format(n) for n in xrange(1, 9) ],
 _JukeboxConstants.PLAYLIST_B: [ 'hangar_newyear_music_jukebox_playlist_b_song_{:02d}'.format(n) for n in xrange(1, 9) ],
 _JukeboxConstants.PLAYLIST_C: [ 'hangar_newyear_music_jukebox_playlist_c_song_{:02d}'.format(n) for n in xrange(1, 6) ]}

class JukeboxController(IJukeboxController):

    def __init__(self):
        self.__eventsManager = EventManager()
        self.onPlaylistSelected = Event(self.__eventsManager)
        self.onTrackSuspended = Event(self.__eventsManager)
        self.onHighlighted = Event(self.__eventsManager)
        self.onFaded = Event(self.__eventsManager)
        self.onHighlightEnable = Event(self.__eventsManager)
        self.__idleLeft = 0
        self.__resetPlaylists()
        self.__currentPlaylist = _JukeboxConstants.PLAYLIST_A
        self.__clickCount = 0
        self.__nextTrackName = None
        self.__position = None
        self.__sounds = []
        return

    def init(self):
        super(JukeboxController, self).init()
        self.__idleLeft = randint(_JukeboxConstants.MIN_FIRST_IDLE, _JukeboxConstants.MAX_FIRST_IDLE)

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__resetPlaylists()
        self.__stop()

    def fini(self):
        self.__stop()
        self.__eventsManager.clear()
        super(JukeboxController, self).fini()

    def setJukeboxPosition(self, position):
        self.__position = position

    def handleJukeboxClick(self, side):
        self.__idleLeft = 0
        self.__choiceTrackAfterClick(side)

    def handleJukeboxHighlight(self, side, isHighlighed):
        if isHighlighed:
            self.onHighlighted(side)
        else:
            self.onFaded(side)

    def onAnimatorEvent(self, name):
        self.onHighlightEnable(name in JukeboxStateMachineConstants.ENABLE_HIGHLIGHT_EVENTS)
        if name == JukeboxStateMachineConstants.PLAY_EVENT:
            self.__playTrack()
        elif name == JukeboxStateMachineConstants.IDLE_EVENT:
            if self.__updateAndCheckIdleCounter():
                self.__idleLeft = 0
                self.__autoChoiceTrack()

    def __updateAndCheckIdleCounter(self):
        if not self.__idleLeft:
            self.__idleLeft = randint(_JukeboxConstants.MIN_OTHERS_IDLE, _JukeboxConstants.MAX_OTHERS_IDLE)
        self.__idleLeft -= 1
        return self.__idleLeft == 0

    def __choiceTrackAfterClick(self, side):
        track = ''
        self.__clickCount += 1
        if self.__clickCount >= _JukeboxConstants.CLICK_COUNT_FOR_PLAY_PLAYLIST_C:
            self.__clickCount = 0
            track = self.__getTrack(_JukeboxConstants.PLAYLIST_C, repeat=True)
        elif side in _JukeboxConstants.PLAYLIST_BY_SIDE:
            self.__currentPlaylist = _JukeboxConstants.PLAYLIST_BY_SIDE[side]
            track = self.__getTrack(self.__currentPlaylist, repeat=True)
        self.__nextTrackName = track
        self.onPlaylistSelected(side)

    def __autoChoiceTrack(self):
        track = self.__getTrack(self.__currentPlaylist)
        if not track:
            self.__currentPlaylist = choice([ p for p in _JukeboxConstants.AUTO_PLAYLISTS if p != self.__currentPlaylist ])
            track = self.__getTrack(self.__currentPlaylist, repeat=True)
        self.__nextTrackName = track
        self.onPlaylistSelected(_JukeboxConstants.SIDE_BY_PLAYLIST[self.__currentPlaylist])

    def __getTrack(self, playlistName, repeat=False):
        playlist = self.__playlists[playlistName]
        if playlist:
            track = playlist.popleft()
        elif repeat:
            playlist.extend(JUKEBOX_MUSIC[playlistName])
            track = playlist.popleft()
        else:
            track = None
        return track

    def __playTrack(self):
        if self.__nextTrackName and self.__position:
            sound = SoundGroups.g_instance.getSound3D(math_utils.createTranslationMatrix(self.__position), self.__nextTrackName)
            sound.setCallback(self.__soundCallback)
            sound.play()
            self.__sounds.append(sound)
            self.__nextTrackName = None
        return

    def __soundCallback(self, sound):
        sound.releaseMatrix()
        self.__sounds.remove(sound)
        if not self.__nextTrackName:
            self.onTrackSuspended()

    def __stop(self):
        for sound in self.__sounds:
            sound.releaseMatrix()

        self.__sounds = []

    def __resetPlaylists(self):
        self.__playlists = {_JukeboxConstants.PLAYLIST_A: deque(JUKEBOX_MUSIC[_JukeboxConstants.PLAYLIST_A]),
         _JukeboxConstants.PLAYLIST_B: deque(JUKEBOX_MUSIC[_JukeboxConstants.PLAYLIST_B]),
         _JukeboxConstants.PLAYLIST_C: deque(JUKEBOX_MUSIC[_JukeboxConstants.PLAYLIST_C])}
