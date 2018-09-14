# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bwpydevd.py
import os
import sys
import ResMgr
import BigWorld
import inspect
import threading
import bwdebug
REPLACE_PATHS = []
HAS_BW_CONFIG = False
if os.name == 'posix':
    try:
        import BWConfig
        HAS_BW_CONFIG = True
    except ImportError:
        HAS_BW_CONFIG = False

else:

    class BWConfig:
        scriptConfig = None

        @staticmethod
        def readString(key, default=''):
            return BWConfig.scriptConfig.readString(key, default)

        @staticmethod
        def readBool(key, default=False):
            return BWConfig.scriptConfig.readBool(key, default)

        @staticmethod
        def readInt(key, default=0):
            return BWConfig.scriptConfig.readInt(key, default)

        @staticmethod
        def getSections(key):
            sections = []
            for sectName, sect in BWConfig.scriptConfig.items():
                if sectName == key:
                    sections.append(sect)

            return sections


def BWConfigWrapper(fn):

    def wrapped(*args, **kwargs):
        global HAS_BW_CONFIG
        if os.name == 'posix':
            return fn(*args, **kwargs)
        else:
            BWConfig.scriptConfig = ResMgr.openSection('scripts_config.xml')
            if BWConfig.scriptConfig is not None:
                HAS_BW_CONFIG = True
            fn(*args, **kwargs)
            BWConfig.scriptConfig = None
            return

    return wrapped


@BWConfigWrapper
def startDebug(isStartUp=False):
    if not HAS_BW_CONFIG:
        return
    if isStartUp and not BWConfig.readBool('pydevd/autoConnect/%s' % BigWorld.component, False):
        return
    for pydevdSect in BWConfig.getSections('pydevd'):
        for sectName, sect in pydevdSect.items():
            if sectName == 'replacePath':
                REPLACE_PATHS.append((sect.readString('to'), sect.readString('from')))

    ide = BWConfig.readString('pydevd/ide', 'pycharm')
    host = BWConfig.readString('pydevd/host', 'localhost')
    port = BWConfig.readInt('pydevd/port', 5678)
    suspend = BWConfig.readBool('pydevd/suspend', False)
    traceOnlyCurrentThread = BWConfig.readBool('pydevd/traceOnlyCurrentThread', False)
    startPyDevD(ide, host, port, suspend, traceOnlyCurrentThread)


bwPyDevDStarted = False

def startPyDevD(ide, host='127.0.0.1', port=5678, suspend=False, traceOnlyCurrentThread=False):
    global bwPyDevDStarted
    if not bwPyDevDStarted:
        bwPyDevDStarted = True
        pydevDir = ResMgr.resolveToAbsolutePath('scripts/common/pydev/%s/pydev' % ide)
        if not os.path.isdir(pydevDir):
            bwdebug.ERROR_MSG('Failed to start pydevd: Unable to find pydevd directory for IDE %s' % ide)
        sys.path.append(pydevDir)
        try:
            import pydevd
            bwdebug.INFO_MSG('PyDevD connecting to %s:%d' % (host, port))
            pydevd.settrace(host=host, port=port, suspend=suspend, stdoutToServer=True, stderrToServer=True, trace_only_current_thread=traceOnlyCurrentThread)
            threading.currentThread().__pydevd_id__ = BigWorld.component
        except Exception as e:
            from traceback import print_exc
            print_exc()
            bwdebug.ERROR_MSG('Failed to load pydevd: %s' % repr(e))
