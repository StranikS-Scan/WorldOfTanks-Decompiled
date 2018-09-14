# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
from gui.prb_control.functional.interfaces import IPrbListener, IUnitListener, IPreQueueListener
from gui.prb_control.functional.interfaces import IGlobalListener

class prbDispatcherProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getDispatcher()


class prbPeripheriesHandlerProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getPeripheriesHandler()


class prbInvitesProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getInvitesManager()


class prbAutoInvitesProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getAutoInvitesNotifier()


class prbFunctionalProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        functional = None
        if dispatcher is not None:
            functional = dispatcher.getPrbFunctional()
        return functional


class preQueueFunctionalProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        functional = None
        if dispatcher is not None:
            functional = dispatcher.getPreQueueFunctional()
        return functional


class unitFunctionalProperty(property):

    def __get__(self, obj, objType = None):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        functional = None
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
        return functional


class PrbListener(IPrbListener):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbFunctionalProperty
    def prbFunctional(self):
        return None

    def startPrbListening(self):
        dispatcher = self.prbDispatcher
        if dispatcher:
            dispatcher.getPrbFunctional().addListener(self)

    def stopPrbListening(self):
        dispatcher = self.prbDispatcher
        if dispatcher:
            dispatcher.getPrbFunctional().removeListener(self)


class QueueListener(IPreQueueListener):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @preQueueFunctionalProperty
    def preQueueFunctional(self):
        return None

    def startQueueListening(self):
        dispatcher = self.prbDispatcher
        if dispatcher:
            dispatcher.getPreQueueFunctional().addListener(self)

    def stopQueueListening(self):
        dispatcher = self.prbDispatcher
        if dispatcher:
            dispatcher.getPreQueueFunctional().removeListener(self)


class UnitListener(IUnitListener):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    def startUnitListening(self):
        dispatcher = self.prbDispatcher
        if dispatcher:
            dispatcher.getUnitFunctional().addListener(self)

    def stopUnitListening(self):
        dispatcher = self.prbDispatcher
        if dispatcher:
            dispatcher.getUnitFunctional().removeListener(self)


class GlobalListener(IGlobalListener):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbFunctionalProperty
    def prbFunctional(self):
        return None

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    @preQueueFunctionalProperty
    def preQueueFunctional(self):
        return None

    def startGlobalListening(self):
        if self.prbDispatcher:
            self.prbDispatcher.addGlobalListener(self)

    def stopGlobalListening(self):
        if self.prbDispatcher:
            self.prbDispatcher.removeGlobalListener(self)
