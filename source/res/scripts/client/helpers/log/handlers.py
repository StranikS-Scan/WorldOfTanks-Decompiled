# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/log/handlers.py
import cStringIO
import logging
import sys
import traceback
from contextlib import closing
import BigWorld
_LOG_LEVEL_2_BW_FUNCTION = {logging.NOTSET: BigWorld.logTrace,
 logging.DEBUG: BigWorld.logDebug,
 logging.INFO: BigWorld.logInfo,
 logging.WARN: BigWorld.logWarning,
 logging.WARNING: BigWorld.logWarning,
 logging.ERROR: BigWorld.logError,
 logging.CRITICAL: BigWorld.logCritical,
 logging.FATAL: BigWorld.logCritical}

class WotFormatter(logging.Formatter):

    def formatException(self, ei):
        return ''.join(traceback.format_exception(*ei))


class WotExtendedFormatter(WotFormatter):

    def __init__(self, fmt=None, datefmt=None, frameSize=-1):
        super(WotExtendedFormatter, self).__init__(fmt, datefmt)
        self._frameSize = frameSize

    def formatException(self, ei):
        message = super(WotExtendedFormatter, self).formatException(ei)
        _, _, etb = ei
        frames = []
        while etb.tb_next:
            etb = etb.tb_next

        frame = etb.tb_frame
        while frame:
            frames.append(frame)
            frame = frame.f_back

        with closing(cStringIO.StringIO()) as sio:
            print >> sio, message
            for frame in reversed(frames):
                print >> sio
                print >> sio, 'Frame {} in {} at line {}'.format(frame.f_code.co_name, frame.f_code.co_filename, frame.f_lineno)
                size = self._frameSize
                for key, value in frame.f_locals.iteritems():
                    if not size:
                        break
                    size -= 1
                    try:
                        print >> sio, '\t{:>20} = {}'.format(key, repr(value))
                    except Exception:
                        print >> sio, '\t{:>20} = <UNDEFINED>'.format(key)

            return sio.getvalue()


class WotLogHandler(logging.Handler):

    def emit(self, record):
        logCategory = record.name.encode(sys.getdefaultencoding())
        msg = self.format(record)
        finalMessage = msg.encode(sys.getdefaultencoding())
        logFunction = _LOG_LEVEL_2_BW_FUNCTION[record.levelno]
        logFunction(logCategory, finalMessage, None)
        return
