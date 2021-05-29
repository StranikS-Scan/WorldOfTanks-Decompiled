# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BWLogging.py
import encodings
import json
import logging
import sys
import BigWorld

class BWLogger(logging.Logger):
    TRACE = logging.DEBUG - 1
    NOTICE = logging.INFO + 1
    HACK = logging.CRITICAL + 1

    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name, level)

    def trace(self, msg, *args, **kw):
        if self.isEnabledFor(BWLogger.TRACE):
            self._log(BWLogger.TRACE, msg, args, **kw)

    def notice(self, msg, *args, **kw):
        if self.isEnabledFor(BWLogger.NOTICE):
            self._log(BWLogger.NOTICE, msg, args, **kw)

    def hack(self, msg, *args, **kw):
        if self.isEnabledFor(BWLogger.HACK):
            self._log(BWLogger.HACK, msg, args, **kw)


logLevelToBigWorldFunction = {logging.NOTSET: BigWorld.logTrace,
 BWLogger.TRACE: BigWorld.logTrace,
 logging.DEBUG: BigWorld.logDebug,
 logging.INFO: BigWorld.logInfo,
 BWLogger.NOTICE: BigWorld.logNotice,
 logging.WARN: BigWorld.logWarning,
 logging.WARNING: BigWorld.logWarning,
 logging.ERROR: BigWorld.logError,
 logging.CRITICAL: BigWorld.logCritical,
 logging.FATAL: BigWorld.logCritical,
 BWLogger.HACK: BigWorld.logHack}

class BWLogRedirectionHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        logCategory = record.name.encode(sys.getdefaultencoding())
        msg = record.getMessage()
        finalMessage = msg.encode(sys.getdefaultencoding())
        if hasattr(record, 'metadata'):
            logMetaData = json.dumps(record.metadata)
        else:
            logMetaData = None
        bwInternalLogFunction = logLevelToBigWorldFunction[record.levelno]
        bwInternalLogFunction(logCategory, finalMessage, logMetaData)
        return


_bwRedirectionHandler = None

def getBwHandler():
    global _bwRedirectionHandler
    return _bwRedirectionHandler


def init():
    global _bwRedirectionHandler
    _bwRedirectionHandler = BWLogRedirectionHandler()
    logging.setLoggerClass(BWLogger)
    logging.addLevelName(BWLogger.TRACE, 'TRACE')
    logging.addLevelName(BWLogger.NOTICE, 'NOTICE')
    logging.addLevelName(BWLogger.HACK, 'HACK')
    rootLogger = logging.getLogger()
    rootLogger.addHandler(_bwRedirectionHandler)
    rootLogger.setLevel(BWLogger.TRACE)
    logging.captureWarnings(True)
