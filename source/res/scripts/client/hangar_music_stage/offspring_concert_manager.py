# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/offspring_concert_manager.py
import random
import logging
from skeletons.hangar_music_stage import IOffspringConcertManager
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
_TRACK_NAMES = (backport.text(R.strings.festival.theOffspringConcert.track1()),
 backport.text(R.strings.festival.theOffspringConcert.track2()),
 backport.text(R.strings.festival.theOffspringConcert.track3()),
 backport.text(R.strings.festival.theOffspringConcert.track4()),
 backport.text(R.strings.festival.theOffspringConcert.track5()))
_SONGS_COUNT = len(_TRACK_NAMES)

class OffspringConcertManager(IOffspringConcertManager):

    def __init__(self):
        super(OffspringConcertManager, self).__init__()
        self.__concertView = None
        self.__concertEntity = None
        self.__songsRndWeights = {}
        return

    def fini(self):
        self.__concertEntity = None
        return

    def setConcertEntity(self, entity):
        if self.__concertEntity is not None:
            _logger.warning('Try to set ConcertEntity multiple times!')
            return
        else:
            self.__concertEntity = entity
            self.__resetSongsRndWeights()
            return

    def removeConcertEntity(self):
        self.__concertEntity = None
        return

    def concertViewStart(self, view):
        if self.__concertView is not None:
            _logger.warning('Try to set ConcertView( multiple times!')
            return
        else:
            self.__concertView = view
            rndTrackIndex = self.__choiceRndTrack()
            if self.__concertEntity is not None:
                self.__concertEntity.switchToSong(rndTrackIndex)
            return rndTrackIndex

    def concertViewDone(self):
        self.__concertView = None
        if self.__concertEntity is not None:
            self.__concertEntity.switchToIdle()
        return

    def onSongFinished(self, songIdx):
        if self.__concertView is not None:
            newSong = (songIdx + 1) % _SONGS_COUNT
            self.__concertView.onSongFinished(newSong)
        return

    def onSongSwitched(self, songIdx):
        if 0 <= songIdx < _SONGS_COUNT:
            if self.__concertEntity is not None:
                self.__concertEntity.switchToSong(songIdx)
            if self.__concertView is not None:
                self.__concertView.switchToSong(songIdx)
        else:
            _logger.warning('Try to set track num %i out of range', songIdx)
        return

    @property
    def trackNames(self):
        return _TRACK_NAMES

    def __resetSongsRndWeights(self):
        self.__songsRndWeights = {i:0 for i, _ in enumerate(_TRACK_NAMES)}

    def __choiceRndTrack(self):
        if not self.__songsRndWeights:
            self.__resetSongsRndWeights()
        minWeight = min(self.__songsRndWeights.values())
        tracksToChoice = [ i for i, w in self.__songsRndWeights.iteritems() if w == minWeight ]
        rndTrackIndex = random.choice(tracksToChoice)
        self.__songsRndWeights[rndTrackIndex] += 1
        return rndTrackIndex
