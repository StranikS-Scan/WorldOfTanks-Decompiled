# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bwpydevd.py
from __future__ import absolute_import
import os
import sys
import ResMgr
import BigWorld
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
        debugConfig = None

        @staticmethod
        def readString(key, default=''):
            return BWConfig.debugConfig.readString(key, default)

        @staticmethod
        def readBool(key, default=False):
            return BWConfig.debugConfig.readBool(key, default)

        @staticmethod
        def readInt(key, default=0):
            return BWConfig.debugConfig.readInt(key, default)

        @staticmethod
        def getSections(key):
            sections = []
            for sectName, sect in BWConfig.debugConfig.items():
                if sectName == key:
                    sections.append(sect)

            return sections


def BWConfigWrapper(fn):

    def wrapped(*args, **kwargs):
        global HAS_BW_CONFIG
        if os.name == 'posix':
            return fn(*args, **kwargs)
        else:
            prefsConfig = ResMgr.openSection('../../bin/client/preferences.xml')
            if prefsConfig and prefsConfig.has_key('scriptsPreferences/development/pydevd'):
                BWConfig.debugConfig = prefsConfig['scriptsPreferences/development']
            else:
                BWConfig.debugConfig = ResMgr.openSection('scripts_config.xml')
            if BWConfig.debugConfig is not None:
                HAS_BW_CONFIG = True
            fn(*args, **kwargs)
            BWConfig.debugConfig = None
            return

    return wrapped


@BWConfigWrapper
def startDebug(isStartUp=False, host=None, port=None, ide=None):
    if not HAS_BW_CONFIG:
        return
    if isStartUp and not BWConfig.readBool('pydevd/autoConnect/%s' % BigWorld.component, False):
        return
    for pydevdSect in BWConfig.getSections('pydevd'):
        for sectName, sect in pydevdSect.items():
            if sectName == 'replacePath':
                REPLACE_PATHS.append((sect.readString('to'), sect.readString('from')))

    ide = ide or BWConfig.readString('pydevd/ide', 'pycharm')
    host = host or BWConfig.readString('pydevd/host', 'localhost')
    port = port or BWConfig.readInt('pydevd/port', 5678)
    suspend = BWConfig.readBool('pydevd/suspend', False)
    traceOnlyCurrentThread = BWConfig.readBool('pydevd/traceOnlyCurrentThread', False)
    inspectDoubleUnderscore = BWConfig.readBool('pydevd/inspectDoubleUnderscore', True)
    bwdebug.INFO_MSG('bwdebug start: %s - %s:%d for VS Code' % (ide, host, port))
    startPyDevD(ide, host, port, suspend, traceOnlyCurrentThread, inspectDoubleUnderscore)


bwPyDevDStarted = False
bwActiveIde = None

def startPyDevD(ide, host='127.0.0.1', port=5678, suspend=False, traceOnlyCurrentThread=False, inspectDoubleUnderscore=False, pathMappings=None):
    global bwPyDevDStarted
    global bwActiveIde
    if not bwPyDevDStarted:
        bwPyDevDStarted = True
        bwActiveIde = ide
        if ide == 'vscode':
            pydevDir = 'scripts/common/pydev/vscode'
            sys.path.append(pydevDir)
            sys.path.append(pydevDir + '/pydev')
        else:
            pydevDir = 'scripts/common/pydev/%s/pydev' % ide
            sys.path.append(pydevDir)
        try:
            if ide == 'vscode':
                import ptvsd
                activeMappings = pathMappings if pathMappings is not None else REPLACE_PATHS
                if activeMappings:
                    import pydevd_file_utils
                    pydevd_file_utils.setup_client_server_paths(activeMappings)
                    bwdebug.INFO_MSG('ptvsd path mappings: %s' % repr(activeMappings))
                bwdebug.INFO_MSG('ptvsd listening on %s:%d for VS Code' % (host, port))
                ptvsd.enable_attach(address=(host, port), redirect_output=True)
                if suspend:
                    ptvsd.wait_for_attach()
            else:
                import pydevd
                bwdebug.INFO_MSG('PyDevD connecting to %s:%d' % (host, port))
                pydevd.settrace(host=host, port=port, suspend=suspend, stdoutToServer=True, stderrToServer=True, trace_only_current_thread=traceOnlyCurrentThread, inspect_double_underscore=inspectDoubleUnderscore)
            threading.currentThread().__pydevd_id__ = BigWorld.component
        except Exception as e:
            from traceback import print_exc
            print_exc()
            bwdebug.ERROR_MSG('Failed to load pydevd: %s' % repr(e))

    return


def stopPyDevD():
    global bwPyDevDStarted
    global bwActiveIde
    if bwPyDevDStarted:
        bwPyDevDStarted = False
        try:
            if bwActiveIde == 'vscode':
                import ptvsd
                ptvsd.tracing(False)
            else:
                import pydevd
                pydevd.stoptrace()
            del threading.currentThread().__pydevd_id__
            bwdebug.INFO_MSG('PyDevD debug has stopped')
        except Exception as e:
            from traceback import print_exc
            print_exc()
            bwdebug.ERROR_MSG('Failed to stop pydevd: %s' % repr(e))

        bwActiveIde = None
    return
