# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Flash.py
# Compiled at: 2011-12-13 13:17:42
import json, constants
import GUI, _Scaleform, weakref
from gui.Scaleform import SCALEFORM_SWF_PATH
from debug_utils import LOG_DEBUG, LOG_CODEPOINT_WARNING, LOG_ERROR, LOG_GUI, _doLog

class Flash(object):

    def __init__(self, swf, className='Flash', args=None):
        if args is None:
            args = []
        self.__fsCbs = {}
        self.__exCbs = {}
        movieDefinition = _Scaleform.MovieDef(SCALEFORM_SWF_PATH + '/' + swf)
        movie = movieDefinition.createInstance()
        self.component = getattr(GUI, className)(movie, *args)
        self.component.focus = True
        self.component.moveFocus = True
        self.component.position.z = 0.5
        self.flashSize = (2, 2)
        self.isActive = False
        movie = self.component.movie
        movie.setFSCommandCallback(_FuncObj(self, 'handleFsCommandCallback'))
        movie.setExternalInterfaceCallback(_FuncObj(self, 'handleExternalInterfaceCallback'))
        return

    def __del__(self):
        LOG_DEBUG('Deleted: %s' % self)

    def __onLogGui(self, type, msg, *kargs):
        if type == 'DEBUG' and not constants.IS_DEVELOPMENT:
            return
        _doLog('%s.GUI' % str(type), msg, kargs)

    def __onLogGuiFormat(self, type, msg, *kargs):
        if type == 'DEBUG' and not constants.IS_DEVELOPMENT:
            return
        else:
            _doLog('%s.GUI' % str(type), msg % kargs, None)
            return

    @property
    def movie(self):
        return self.component.movie

    def afterCreate(self):
        self.addExternalCallback('debug.LOG_GUI', self.__onLogGui)
        self.addExternalCallback('debug.LOG_GUI_FORMAT', self.__onLogGuiFormat)

    def beforeDelete(self):
        self.removeAllCallbacks()

    def active(self, state):
        if self.isActive != state:
            self.isActive = state
            if state:
                GUI.addRoot(self.component)
                self.component.size = self.flashSize
            else:
                GUI.delRoot(self.component)

    def close(self):
        self.component.script = None
        self.active(False)
        self.beforeDelete()
        return

    def setMovieVariable(self, path, value):
        if not isinstance(value, list):
            value = [value]
        try:
            self.movie.invoke(('_root._level0.' + path, value))
        except Exception:
            LOG_ERROR('Error to set movie variable "' + '_root._level0.' + path + '"')

    def call(self, methodName, args=None):
        if args is None:
            args = []
        args.insert(0, methodName)
        self.movie.invoke(('call', args))
        return

    def callNice(self, methodName, args=None):
        if args is None:
            args = []
        jsonArgs = [methodName, json.dumps(args)]
        self.movie.invoke(('callJson', jsonArgs))
        return

    def respond(self, args=None):
        if args is None:
            args = []
        self.movie.invoke(('respond', args))
        return

    def addFsCallback(self, command, function):
        self.__fsCbs.setdefault(command, set())
        self.__fsCbs[command].add(function)

    def removeFsCallback(self, command):
        try:
            self.__fsCbs.pop(command)
        except KeyError:
            pass

    def addFsCallbacks(self, commands):
        for command, function in commands.items():
            self.addFsCallback(command, function)

    def removeFsCallbacks(self, *args):
        for command in args:
            self.removeFsCallback(command)

    def addExternalCallback(self, command, function):
        self.__exCbs.setdefault(command, set())
        self.__exCbs[command].add(function)

    def removeExternalCallback(self, command, function=None):
        try:
            if function is None:
                self.__exCbs.pop(command)
            elif function in self.__exCbs[command]:
                self.__exCbs[command].remove(function)
        except KeyError:
            pass

        return

    def addExternalCallbacks(self, commands):
        for command, function in commands.items():
            self.addExternalCallback(command, function)

    def removeExternalCallbacks(self, *args):
        for command in args:
            self.removeExternalCallback(command)

    def removeAllCallbacks(self):
        self.__fsCbs.clear()
        self.__exCbs.clear()

    def handleFsCommandCallback(self, command, arg):
        callbacks = self.__fsCbs.get(command)
        result = callbacks is not None
        if result:
            for callback in callbacks:
                callback(arg)

        else:
            LOG_DEBUG('FsCommandCallback "%s" not found' % command, arg)
        return result

    def handleExternalInterfaceCallback(self, command, args):
        if command == 'callNice':
            command, uid, params = json.loads(args[0])
            args = [uid, params]
        callbacks = self.__exCbs.get(command)
        result = callbacks is not None
        if result:
            for callback in callbacks:
                callback(*args)

        else:
            LOG_DEBUG('ExternalInterfaceCallback "%s" not found' % command, args)
        return result


class _FuncObj:

    def __init__(self, obj, funcName):
        self.__weakObj = weakref.ref(obj)
        self.__funcName = funcName

    def __call__(self, command, args):
        if self.__weakObj() is not None:
            getattr(self.__weakObj(), self.__funcName)(command, args)
        else:
            LOG_CODEPOINT_WARNING('weak object has been already destroyed.')
        return
