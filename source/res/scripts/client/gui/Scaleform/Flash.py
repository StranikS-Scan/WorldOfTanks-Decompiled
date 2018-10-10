# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Flash.py
import json
import logging
import weakref
from collections import defaultdict
import GUI
from gui.Scaleform import SCALEFORM_SWF_PATH
_logger = logging.getLogger(__name__)

class Flash(object):

    def __init__(self, swf, className='Flash', args=None, path=SCALEFORM_SWF_PATH, descriptor=0):
        args = args or []
        super(Flash, self).__init__()
        self.__fsCbs = defaultdict(set)
        self.__exCbs = defaultdict(set)
        fileName = '{}/{}'.format(path, swf)
        self.component = getattr(GUI, className)(fileName, descriptor, *args)
        self.component.focus = True
        self.component.moveFocus = True
        self.component.position.z = 0.5
        self.flashSize = (2, 2)
        self.isActive = False
        movie = self.component.movie
        movie.setFSCommandCallback(_FsCommandObj(self))
        movie.setExternalInterfaceCallback(_ExternalInterfaceObj(self))

    def __del__(self):
        _logger.debug('Deleted: %s', self)

    def __onLogGui(self, logType, msg, *kargs):
        _logger.debug('%s.GUI: %r, %r', str(logType), msg, kargs)

    def __onLogGuiFormat(self, logType, msg, *kargs):
        _logger.debug('%s.GUI: %r', str(logType), msg % kargs)

    @property
    def movie(self):
        return self.component.movie

    @property
    def moviePath(self):
        return self.component.moviePath

    @property
    def movieUid(self):
        return self.component.movie.movieUid

    def afterCreate(self):
        self.addExternalCallback('debug.LOG_GUI', self.__onLogGui)
        self.addExternalCallback('debug.LOG_GUI_FORMAT', self.__onLogGuiFormat)

    def beforeDelete(self):
        self.removeAllCallbacks()
        self.__fsCbs.clear()
        self.__exCbs.clear()
        self.flashSize = None
        del self.component
        self.component = None
        return

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
            _logger.error('Error to set movie variable "_root._level0.%s"', path)

    def getMember(self, path):
        return getattr(self.movie, path, None)

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
        self.__fsCbs[command].add(function)

    def removeFsCallback(self, command):
        try:
            self.__fsCbs.pop(command)
        except KeyError:
            pass

    def addFsCallbacks(self, commands):
        add = self.addFsCallback
        for command, function in commands.items():
            add(command, function)

    def removeFsCallbacks(self, *args):
        remove = self.removeFsCallback
        for command in args:
            remove(command)

    def addExternalCallback(self, command, function):
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
        add = self.addExternalCallback
        for command, function in commands.items():
            add(command, function)

    def removeExternalCallbacks(self, *args):
        remove = self.removeExternalCallback
        for command in args:
            remove(command)

    def removeAllCallbacks(self):
        self.__fsCbs.clear()
        self.__exCbs.clear()

    def handleFsCommandCallback(self, command, arg):
        result = False
        if command in self.__fsCbs:
            result = True
            callbacks = self.__fsCbs[command]
            for callback in callbacks:
                callback(arg)

        else:
            _logger.debug('FsCommandCallback "%s" not found: %r', command, arg)
        return result

    def handleExternalInterfaceCallback(self, command, args):
        result = False
        if command == 'callNice':
            tmp = list(json.loads(args[0]))
            command = tmp.pop(0)
            args = tmp
        if command in self.__exCbs:
            result = True
            callbacks = self.__exCbs[command]
            for callback in callbacks:
                callback(*args)

        else:
            _logger.debug('ExternalInterfaceCallback "%s" not found: %r', command, args)
        return result


class _FsCommandObj(object):

    def __init__(self, obj):
        self.__weakObj = weakref.ref(obj)

    def __call__(self, command, args):
        obj = self.__weakObj()
        if obj:
            obj.handleFsCommandCallback(command, args)
        else:
            _logger.warning('Weak object has been already destroyed: command = %s, args = %r.', command, args)


class _ExternalInterfaceObj(object):

    def __init__(self, obj):
        self.__weakObj = weakref.ref(obj)

    def __call__(self, command, args):
        obj = self.__weakObj()
        if obj:
            obj.handleExternalInterfaceCallback(command, args)
        else:
            _logger.warning('Weak object has been already destroyed: command = %s, args = %r.', command, args)
