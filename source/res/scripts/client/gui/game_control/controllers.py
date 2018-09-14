# Embedded file name: scripts/client/gui/game_control/controllers.py
import weakref
import operator
from shared_utils import forEach

class _IController(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def onConnected(self):
        raise NotImplementedError

    def onDisconnected(self):
        raise NotImplementedError

    def onAvatarBecomePlayer(self):
        raise NotImplementedError

    def onAccountBecomePlayer(self):
        raise NotImplementedError

    def onLobbyStarted(self, ctx):
        raise NotImplementedError

    def onLobbyInited(self, event):
        raise NotImplementedError


class ControllersCollection(_IController):

    def __init__(self, controllers):
        self._controllers = {}
        self._addControllers(controllers)

    def getController(self, controllerName):
        return self._controllers.get(controllerName)

    def init(self):
        self._invoke('init')

    def fini(self):
        self._invoke('fini')

    def onConnected(self):
        self._invoke('onConnected')

    def onDisconnected(self):
        self._invoke('onDisconnected')

    def onAvatarBecomePlayer(self):
        self._invoke('onAvatarBecomePlayer')

    def onAccountBecomePlayer(self):
        self._invoke('onAccountBecomePlayer')

    def onLobbyStarted(self, ctx):
        self._invoke('onLobbyStarted', ctx)

    def onLobbyInited(self, event):
        self._invoke('onLobbyInited', event)

    def _addController(self, controllerName, controller):
        raise issubclass(controller, Controller) or AssertionError('Controller should be child class of Controller')
        controllerInstance = controller(self)
        self._controllers[controllerName] = controllerInstance
        setattr(self, controllerName, weakref.proxy(controllerInstance))

    def _removeController(self, controllerName):
        if controllerName in self._controllers:
            del self._controllers[controllerName]
        delattr(self, controllerName)

    def _addControllers(self, controllers):
        for controllerName, controller in controllers.iteritems():
            self._addController(controllerName, controller)

    def _invoke(self, method, *args):
        forEach(operator.methodcaller(method, *args), self._controllers.itervalues())


class Controller(_IController):

    def __init__(self, proxy):
        super(Controller, self).__init__()
        self._proxy = weakref.proxy(proxy)

    def init(self):
        pass

    def fini(self):
        self._proxy = None
        return

    def onConnected(self):
        pass

    def onDisconnected(self):
        pass

    def onAvatarBecomePlayer(self):
        pass

    def onAccountBecomePlayer(self):
        pass

    def onLobbyStarted(self, ctx):
        pass

    def onLobbyInited(self, event):
        pass
