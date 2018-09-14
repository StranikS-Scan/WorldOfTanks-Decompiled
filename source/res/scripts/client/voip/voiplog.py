# Embedded file name: scripts/client/VOIP/VOIPLog.py
import sys
import Settings
from datetime import datetime
from debug_utils import LOG_VOIP, LOG_CURRENT_EXCEPTION
g_useVivoxlog = None
g_vivoxLogFile = None

def LOG_VOIP_INT(msg, *kargs):
    global g_useVivoxlog
    if g_useVivoxlog is None:
        checkUseVivoxLog()
    if not g_useVivoxlog is not None:
        raise AssertionError
        g_useVivoxlog and _writeLog(msg, kargs)
    elif kargs:
        LOG_VOIP(msg, kargs)
    else:
        LOG_VOIP(msg)
    return


def checkUseVivoxLog():
    global g_useVivoxlog
    g_useVivoxlog = False
    section = Settings.g_instance.userPrefs
    if section.has_key('development'):
        section = section['development']
        if section.has_key('enableVivoxLog'):
            g_useVivoxlog = section['enableVivoxLog'].asBool
            if g_useVivoxlog:
                _openLog()


def _openLog():
    global g_vivoxLogFile
    if g_vivoxLogFile is None:
        try:
            g_vivoxLogFile = open('vivox.log', 'w')
            g_vivoxLogFile.write('----------------------------\n')
        except:
            LOG_CURRENT_EXCEPTION()

    return


def closeLog():
    global g_useVivoxlog
    global g_vivoxLogFile
    g_useVivoxlog = None
    if g_vivoxLogFile is not None:
        try:
            g_vivoxLogFile.close()
            g_vivoxLogFile = None
        except:
            LOG_CURRENT_EXCEPTION()

    return


def _writeLog(msg, args):
    try:
        frame = sys._getframe(2)
        dt = datetime.time(datetime.now())
        g_vivoxLogFile.write('%s: (%s, %d):' % (dt, frame.f_code.co_filename, frame.f_lineno))
        g_vivoxLogFile.write(msg)
        if args:
            g_vivoxLogFile.write(args)
        g_vivoxLogFile.write('\n')
        g_vivoxLogFile.flush()
    except:
        LOG_CURRENT_EXCEPTION()
