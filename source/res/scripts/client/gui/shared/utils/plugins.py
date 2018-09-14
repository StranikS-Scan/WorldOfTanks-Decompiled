# Embedded file name: scripts/client/gui/shared/utils/plugins.py
import weakref
import operator
from debug_utils import LOG_ERROR
from shared_utils import forEach

class IPlugin(object):

    def __init__(self, parentObj):
        self._parentObj = parentObj

    def init(self):
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

    def __init__(self, parentObj):
        super(PluginsCollection, self).__init__(weakref.proxy(parentObj))
        self.__plugins = {}

    def addPlugins(self, plugins):
        for pluginName, pluginClass in plugins.iteritems():
            if pluginName in self.__plugins:
                LOG_ERROR('Plugin with this name was already added: ', pluginName, pluginClass)
                continue
            pluginObj = pluginClass(self._parentObj)
            self.__plugins[pluginName] = pluginObj

    def init(self):
        self._invoke('init')

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
