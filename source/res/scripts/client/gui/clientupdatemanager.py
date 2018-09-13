# Embedded file name: scripts/client/gui/ClientUpdateManager.py
import inspect

class _ClientUpdateManager(object):
    EVENT_TYPE_DELIMITER = '.'

    def __init__(self):
        self.__handlers = dict()
        self.__removedHandlers = set()

    def update(self, diff):
        self.__clearRemoved()
        for handler, diffpaths in self.__handlers.iteritems():
            if handler in self.__removedHandlers:
                continue
            for diffpath in diffpaths:
                isFire, args = self.__processPath(diffpath, diff)
                if isFire:
                    handler(args)
                    break

    def addCallback(self, diffpath, handler):
        self.__subscribeHandler(handler, diffpath)

    def addCallbacks(self, map_of_handlers):
        for diffpath, handler in map_of_handlers.iteritems():
            self.__subscribeHandler(handler, diffpath)

    def removeCallback(self, diffpath, handler):
        self.__unsubscribeHandler(handler, diffpath)

    def removeObjectCallbacks(self, obj_instance, force = False):
        removed = set(filter(lambda key: inspect.ismethod(key) and key.__self__ is obj_instance, self.__handlers.iterkeys()))
        if force:
            for item in removed:
                del self.__handlers[item]

        else:
            self.__removedHandlers |= removed

    def __subscribeHandler(self, handler, diffpath):
        self.__clearRemoved()
        if handler not in self.__handlers:
            self.__handlers[handler] = []
        if diffpath not in self.__handlers[handler]:
            self.__handlers[handler].append(diffpath)

    def __unsubscribeHandler(self, handler, diffpath):
        if handler in self.__handlers:
            if diffpath in self.__handlers[handler]:
                self.__handlers[handler].remove(diffpath)
            if not len(self.__handlers[handler]):
                del self.__handlers[handler]

    def __processPath(self, diffpath, diff):
        diff_ptr = diff
        if diffpath == '':
            return (True, diff_ptr)
        else:
            for key in diffpath.split(self.EVENT_TYPE_DELIMITER):
                key = (key[:-2], '_r') if key.endswith('_r') else (key if not key.isdigit() else int(key))
                if type(diff_ptr) != dict or key not in diff_ptr:
                    return (False, None)
                diff_ptr = diff_ptr[key]

            return (True, diff_ptr)

    def __clearRemoved(self):
        if not len(self.__removedHandlers):
            return
        for item in self.__removedHandlers:
            del self.__handlers[item]

        self.__removedHandlers = set()


g_clientUpdateManager = _ClientUpdateManager()
