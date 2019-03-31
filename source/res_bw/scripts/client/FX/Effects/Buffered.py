# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Effects/Buffered.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld
import ResMgr
from OneShot import OneShot
from Queue import Queue
from functools import partial
from bwdebug import *
_overruns = {}
_effectBuffer = {}

def outputOverruns():
    """This method outputs a debug report stating which buffered effects
    encountered buffer overruns.  A buffer overrun occurs when the size of
    the circular buffer is not large enough to handle the number of requests
    to play that effect simultaneously.  If you encounter buffer overruns,
    there are two solutions: increase the buffer size, or reduce the duration
    of the effect."""
    global _overruns
    if len(_overruns.keys()) == 0:
        return
    DEBUG_MSG('---------------Effect Buffer Overruns------------------')
    DEBUG_MSG('Warning - during that run, some buffered effects ran out')
    DEBUG_MSG('')
    for fileName, (discard, largest) in _overruns.items():
        DEBUG_MSG(fileName, largest)

    _overruns = {}
    DEBUG_MSG('----------------------------------------------------')


def cleanupBufferedEffects():
    """This method cleans up all effects buffers, and should be called to
    free the effects system in a controlled manner."""
    global _effectBuffer
    _effectBuffer = {}


class _BufferedOneShot(OneShot):
    """This class is a buffered version of OneShot.  It is private
    ( don't create one of these yourself! )"""

    def __init__(self, fileName, maxDuration, queue, prereqs=None):
        OneShot.__init__(self, fileName, maxDuration, prereqs)
        self.queue = queue

    def stop(self, source, target, callbackFn):
        OneShot.stop(self, source, target, callbackFn)
        self.queue.put(self)


def _onAsyncLoadBufferedEffect(fileName, maxDuration, resourceRefs):
    queue = _effectBuffer[fileName]
    queue.put(_BufferedOneShot(fileName, maxDuration, queue, resourceRefs))


def _preloadBufferedOneShotEffect(fileName, maxDuration=10.0, prereqs=None):
    """This method preloads the whole effect buffer given by fileName.
    If no prerequisites are passed in, then the entire buffer is synchronously
    created.  This may create a pause in the rendering thread.
    If prerequisites are provided, it immediately queues up one effect, and
    then asnychronously loads the rest.
    """
    pSection = None
    if prereqs != None:
        pSection = prereqs[fileName]
    else:
        pSection = ResMgr.openSection(fileName)
    if not pSection:
        ERROR_MSG('Could not open file', fileName)
        return False
    else:
        _effectBuffer[fileName] = Queue()
        queue = _effectBuffer[fileName]
        bufferSize = pSection.readInt('bufferSize', 5)
        if prereqs != None:
            resourceIDs = tuple(prereqs.keys())
            queue.put(_BufferedOneShot(fileName, maxDuration, queue, prereqs))
            for i in xrange(0, bufferSize - 1):
                BigWorld.loadResourceListBG(resourceIDs, partial(_onAsyncLoadBufferedEffect, fileName, maxDuration))

        else:
            for i in xrange(0, bufferSize):
                queue.put(_BufferedOneShot(fileName, maxDuration, queue))

        return True


def getBufferedOneShotEffect(fileName, maxDuration=10.0, prereqs=None):
    """This method returns an instance of a buffered effect.  You should call
    this if you need access to a buffered effect, but do not want the effect
    to play immediately."""
    if not _effectBuffer.has_key(fileName):
        if _preloadBufferedOneShotEffect(fileName, maxDuration, prereqs) == False:
            return None
    queue = _effectBuffer[fileName]
    if not queue.empty():
        if _overruns.has_key(fileName):
            current, largest = _overruns[fileName]
            _overruns[fileName] = (0, largest)
        return queue.get()
    else:
        if not _overruns.has_key(fileName):
            _overruns[fileName] = (1, 1)
        else:
            current, largest = _overruns[fileName]
            _overruns[fileName] = (current + 1, max(largest, current + 1))
        return None
        return None


def bufferedOneShotEffect(fileName, source, target=None, callbackFn=None, maxDuration=10.0, prereqs=None, **kargs):
    """This method plays an effect, retrieving it from an interally managed
    fixed-size cirular buffer.  If there are none available to play, it
    fails silently and internally reports it as a buffer overrun."""
    s = getBufferedOneShotEffect(fileName, maxDuration, prereqs)
    if s:
        s.maxDuration = maxDuration
        s.go(source, target, callbackFn, **kargs)


queue = Queue()
