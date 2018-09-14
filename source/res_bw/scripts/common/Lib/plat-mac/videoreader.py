# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/videoreader.py
from warnings import warnpy3k
warnpy3k('In 3.x, the videoreader module is removed.', stacklevel=2)
import sys
from Carbon import Qt
from Carbon import QuickTime
from Carbon import Qd
from Carbon import Qdoffs
from Carbon import QDOffscreen
from Carbon import Res
try:
    from Carbon import MediaDescr
except ImportError:

    def _audiodescr(data):
        return None


else:

    def _audiodescr(data):
        return MediaDescr.SoundDescription.decode(data)


try:
    from imgformat import macrgb
except ImportError:
    macrgb = 'Macintosh RGB format'

import os

class VideoFormat:

    def __init__(self, name, descr, width, height, format):
        self.__name = name
        self.__descr = descr
        self.__width = width
        self.__height = height
        self.__format = format

    def getname(self):
        return self.__name

    def getdescr(self):
        return self.__descr

    def getsize(self):
        return (self.__width, self.__height)

    def getformat(self):
        return self.__format


class _Reader:

    def __init__(self, path):
        fd = Qt.OpenMovieFile(path, 0)
        self.movie, d1, d2 = Qt.NewMovieFromFile(fd, 0, 0)
        self.movietimescale = self.movie.GetMovieTimeScale()
        try:
            self.audiotrack = self.movie.GetMovieIndTrackType(1, QuickTime.AudioMediaCharacteristic, QuickTime.movieTrackCharacteristic)
            self.audiomedia = self.audiotrack.GetTrackMedia()
        except Qt.Error:
            self.audiotrack = self.audiomedia = None
            self.audiodescr = {}
        else:
            handle = Res.Handle('')
            n = self.audiomedia.GetMediaSampleDescriptionCount()
            self.audiomedia.GetMediaSampleDescription(1, handle)
            self.audiodescr = _audiodescr(handle.data)
            self.audiotimescale = self.audiomedia.GetMediaTimeScale()
            del handle

        try:
            self.videotrack = self.movie.GetMovieIndTrackType(1, QuickTime.VisualMediaCharacteristic, QuickTime.movieTrackCharacteristic)
            self.videomedia = self.videotrack.GetTrackMedia()
        except Qt.Error:
            self.videotrack = self.videomedia = self.videotimescale = None

        if self.videotrack:
            self.videotimescale = self.videomedia.GetMediaTimeScale()
            x0, y0, x1, y1 = self.movie.GetMovieBox()
            self.videodescr = {'width': x1 - x0,
             'height': y1 - y0}
            self._initgworld()
        self.videocurtime = None
        self.audiocurtime = None
        return

    def __del__(self):
        self.audiomedia = None
        self.audiotrack = None
        self.videomedia = None
        self.videotrack = None
        self.movie = None
        return

    def _initgworld(self):
        old_port, old_dev = Qdoffs.GetGWorld()
        try:
            movie_w = self.videodescr['width']
            movie_h = self.videodescr['height']
            movie_rect = (0,
             0,
             movie_w,
             movie_h)
            self.gworld = Qdoffs.NewGWorld(32, movie_rect, None, None, QDOffscreen.keepLocal)
            self.pixmap = self.gworld.GetGWorldPixMap()
            Qdoffs.LockPixels(self.pixmap)
            Qdoffs.SetGWorld(self.gworld.as_GrafPtr(), None)
            Qd.EraseRect(movie_rect)
            self.movie.SetMovieGWorld(self.gworld.as_GrafPtr(), None)
            self.movie.SetMovieBox(movie_rect)
            self.movie.SetMovieActive(1)
            self.movie.MoviesTask(0)
            self.movie.SetMoviePlayHints(QuickTime.hintsHighQuality, QuickTime.hintsHighQuality)
        finally:
            Qdoffs.SetGWorld(old_port, old_dev)

        return

    def _gettrackduration_ms(self, track):
        tracktime = track.GetTrackDuration()
        return self._movietime_to_ms(tracktime)

    def _movietime_to_ms(self, time):
        value, d1, d2 = Qt.ConvertTimeScale((time, self.movietimescale, None), 1000)
        return value

    def _videotime_to_ms(self, time):
        value, d1, d2 = Qt.ConvertTimeScale((time, self.videotimescale, None), 1000)
        return value

    def _audiotime_to_ms(self, time):
        value, d1, d2 = Qt.ConvertTimeScale((time, self.audiotimescale, None), 1000)
        return value

    def _videotime_to_movietime(self, time):
        value, d1, d2 = Qt.ConvertTimeScale((time, self.videotimescale, None), self.movietimescale)
        return value

    def HasAudio(self):
        return self.audiotrack is not None

    def HasVideo(self):
        return self.videotrack is not None

    def GetAudioDuration(self):
        return 0 if not self.audiotrack else self._gettrackduration_ms(self.audiotrack)

    def GetVideoDuration(self):
        return 0 if not self.videotrack else self._gettrackduration_ms(self.videotrack)

    def GetAudioFormat(self):
        if not self.audiodescr:
            return (None, None, None, None, None)
        else:
            bps = self.audiodescr['sampleSize']
            nch = self.audiodescr['numChannels']
            if nch == 1:
                channels = ['mono']
            elif nch == 2:
                channels = ['left', 'right']
            else:
                channels = map(lambda x: str(x + 1), range(nch))
            if bps % 8:
                blocksize = 0
                fpb = 0
            else:
                blocksize = bps / 8 * nch
                fpb = 1
            if self.audiodescr['dataFormat'] == 'raw ':
                encoding = 'linear-excess'
            elif self.audiodescr['dataFormat'] == 'twos':
                encoding = 'linear-signed'
            else:
                encoding = 'quicktime-coding-%s' % self.audiodescr['dataFormat']
            return (channels,
             encoding,
             blocksize,
             fpb,
             bps)

    def GetAudioFrameRate(self):
        return None if not self.audiodescr else int(self.audiodescr['sampleRate'])

    def GetVideoFormat(self):
        width = self.videodescr['width']
        height = self.videodescr['height']
        return VideoFormat('dummy_format', 'Dummy Video Format', width, height, macrgb)

    def GetVideoFrameRate(self):
        tv = self.videocurtime
        if tv is None:
            tv = 0
        flags = QuickTime.nextTimeStep | QuickTime.nextTimeEdgeOK
        tv, dur = self.videomedia.GetMediaNextInterestingTime(flags, tv, 1.0)
        dur = self._videotime_to_ms(dur)
        return int(1000.0 / dur + 0.5)

    def ReadAudio(self, nframes, time=None):
        if time is not None:
            self.audiocurtime = time
        flags = QuickTime.nextTimeStep | QuickTime.nextTimeEdgeOK
        if self.audiocurtime is None:
            self.audiocurtime = 0
        tv = self.audiomedia.GetMediaNextInterestingTimeOnly(flags, self.audiocurtime, 1.0)
        if tv < 0 or self.audiocurtime and tv < self.audiocurtime:
            return (self._audiotime_to_ms(self.audiocurtime), None)
        else:
            h = Res.Handle('')
            desc_h = Res.Handle('')
            size, actualtime, sampleduration, desc_index, actualcount, flags = self.audiomedia.GetMediaSample(h, 0, tv, desc_h, nframes)
            self.audiocurtime = actualtime + actualcount * sampleduration
            return (self._audiotime_to_ms(actualtime), h.data)

    def ReadVideo(self, time=None):
        if time is not None:
            self.videocurtime = time
        flags = QuickTime.nextTimeStep
        if self.videocurtime is None:
            flags = flags | QuickTime.nextTimeEdgeOK
            self.videocurtime = 0
        tv = self.videomedia.GetMediaNextInterestingTimeOnly(flags, self.videocurtime, 1.0)
        if tv < 0 or self.videocurtime and tv <= self.videocurtime:
            return (self._videotime_to_ms(self.videocurtime), None)
        else:
            self.videocurtime = tv
            moviecurtime = self._videotime_to_movietime(self.videocurtime)
            self.movie.SetMovieTimeValue(moviecurtime)
            self.movie.MoviesTask(0)
            return (self._videotime_to_ms(self.videocurtime), self._getpixmapcontent())

    def _getpixmapcontent(self):
        """Shuffle the offscreen PixMap data, because it may have funny stride values"""
        rowbytes = Qdoffs.GetPixRowBytes(self.pixmap)
        width = self.videodescr['width']
        height = self.videodescr['height']
        start = 0
        rv = []
        for i in range(height):
            nextline = Qdoffs.GetPixMapBytes(self.pixmap, start, width * 4)
            start = start + rowbytes
            rv.append(nextline)

        return ''.join(rv)


def reader(url):
    try:
        rdr = _Reader(url)
    except IOError:
        return None

    return rdr


def _test():
    import EasyDialogs
    try:
        from PIL import Image
    except ImportError:
        Image = None

    import MacOS
    Qt.EnterMovies()
    path = EasyDialogs.AskFileForOpen(message='Video to convert')
    if not path:
        sys.exit(0)
    rdr = reader(path)
    if not rdr:
        sys.exit(1)
    dstdir = EasyDialogs.AskFileForSave(message='Name for output folder')
    if not dstdir:
        sys.exit(0)
    num = 0
    os.mkdir(dstdir)
    videofmt = rdr.GetVideoFormat()
    imgfmt = videofmt.getformat()
    imgw, imgh = videofmt.getsize()
    timestamp, data = rdr.ReadVideo()
    while data:
        fname = 'frame%04.4d.jpg' % num
        num = num + 1
        pname = os.path.join(dstdir, fname)
        if not Image:
            print 'Not',
        print 'Writing %s, size %dx%d, %d bytes' % (fname,
         imgw,
         imgh,
         len(data))
        if Image:
            img = Image.fromstring('RGBA', (imgw, imgh), data)
            img.save(pname, 'JPEG')
            timestamp, data = rdr.ReadVideo()
            MacOS.SetCreatorAndType(pname, 'ogle', 'JPEG')
            if num > 20:
                print 'stopping at 20 frames so your disk does not fill up:-)'
                break

    print 'Total frames:', num
    return


if __name__ == '__main__':
    _test()
    sys.exit(1)
