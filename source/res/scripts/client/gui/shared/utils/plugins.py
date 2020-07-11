# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/plugins.py
import operator
import weakref
from debug_utils import LOG_ERROR
from shared_utils import forEach

class IPlugin(object):
    __slots__ = ('_parentObj',)

    def __init__(self, parentObj):
        self._parentObj = parentObj

    def init(self, *args):
        pass

    def fini(self):
        self._parentObj = None
        return

    def start(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass

    def update(self):
        pass

    @property
    def parentObj(self):
        return self._parentObj


class PluginsCollection(IPlugin):
    __slots__ = ('__plugins',)

    def __init__(self, parentObj):
        super(PluginsCollection, self).__init__(weakref.proxy(parentObj))
        self.__plugins = {}

    def __iter__(self):
        return iter(self.__plugins)

    def addPlugins(self, plugins):
        for pluginName, pluginClass in plugins.iteritems():
            if pluginName in self.__plugins:
                LOG_ERROR('Plugin with this name was already added: ', pluginName, pluginClass)
                continue
            pluginObj = pluginClass(self._parentObj)
            self.__plugins[pluginName] = pluginObj

    def removePlugins(self, *names):
        for name in names:
            plugin = self.__plugins.pop(name, None)
            if plugin is not None:
                plugin.stop()
                plugin.fini()

        return

    def getPlugin(self, name):
        return self.__plugins[name] if name in self.__plugins else None

    def init(self, *args):
        self._invoke('init', *args)

    def fini(self):
        self._invoke('fini')
        self.__plugins.clear()
        super(PluginsCollection, self).fini()

    def start(self):
        self._invoke('start')

    def stop(self):
        self._invoke('stop')

    def reset(self):
        self._invoke('reset')

    def update(self):
        self._invoke('update')

    def _invoke(self, method, *args):
        forEach(operator.methodcaller(method, *args), self.__plugins.itervalues())
