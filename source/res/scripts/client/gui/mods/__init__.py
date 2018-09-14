# Embedded file name: scripts/client/gui/mods/__init__.py
import importlib
import ResMgr
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_WARNING
from shared_utils import forEach
_mods = {}
if IS_DEVELOPMENT:
    _MOD_NAME_POSTFIX = '.py'
else:
    _MOD_NAME_POSTFIX = '.pyc'

def init():
    global _mods
    _mods = _findValidMODs()
    forEach(lambda mod: _callModMethod(mod, 'init'), _mods.itervalues())


def fini():
    forEach(lambda mod: _callModMethod(mod, 'fini'), _mods.itervalues())
    _mods.clear()


def sendEvent(eventName, *args, **kwargs):
    forEach(lambda mod: _callModMethod(mod, eventName, *args, **kwargs), _mods.itervalues())


def _callModMethod(mod, methodName, *args, **kwargs):
    try:
        return getattr(mod, methodName)(*args, **kwargs)
    except AttributeError:
        pass


def _isValidMOD(scriptName):
    return scriptName.startswith('mod_') and scriptName.endswith(_MOD_NAME_POSTFIX)


def _findValidMODs(path = None, package = None):
    result = {}
    path = path or __path__[0]
    package = package or __package__
    modsFolder = ResMgr.openSection(path)
    if modsFolder:
        for scriptName in modsFolder.keys():
            if _isValidMOD(scriptName):
                try:
                    moduleName = '%s.%s' % (package, scriptName.replace(_MOD_NAME_POSTFIX, ''))
                    result[moduleName] = importlib.import_module(moduleName)
                    LOG_DEBUG('Gui mod found', moduleName, result[moduleName])
                except ImportError:
                    LOG_WARNING('There is problem while import gui mod', package, scriptName)
                    LOG_CURRENT_EXCEPTION()

    else:
        LOG_ERROR('There is no mods folder found', __path__)
    return result
