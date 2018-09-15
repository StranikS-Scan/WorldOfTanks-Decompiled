# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/BootcampManager.py
from bootcamp.BootcampUIConfig import readBootcampManagerConfig
from debug_utils import LOG_WARNING
from gui.Scaleform.framework.entities.abstract.BootcampManagerMeta import BootcampManagerMeta

class BootcampManager(BootcampManagerMeta):
    """
    The class provides functionality to override/change logic for Scaleform and Python parts of Views
    """

    def __init__(self, isEnabled=False, path=''):
        super(BootcampManager, self).__init__()
        self.__isEnabled = isEnabled
        self.__config = readBootcampManagerConfig(path)
        self.__observers = {}
        self.__classes = {}

    def registerObserverClass(self, alias, observerClass):
        """
        Register a Python part of the Observer
        
        :param alias: name of the Observer.
        :param observerClass: DAAPI class with observer logic.
        """
        if alias in self.__classes:
            LOG_WARNING('Trying to register a class twice:', alias)
            return
        self.__classes[alias] = observerClass

    def unregisterObserverClass(self, alias):
        """
        Unregister a Python part of the Observer
        
        :param alias: name of the Observer.
        """
        if alias not in self.__classes:
            LOG_WARNING('Trying to unregister a class twice:', alias)
            return
        self.__classes.pop(alias)

    def registerObserver(self, flashObserver, alias):
        """
        Register a Scaleform part of the Observer with a Python part
        
        :param flashObserver: Scaleform observer class.
        :param alias: name of the Observer.
        """
        if alias not in self.__classes:
            LOG_WARNING('Unknown observer class:', alias)
            return
        observer = self.__classes[alias]()
        self.__observers[alias] = observer
        observer.setFlashObject(flashObserver)

    def unregisterObserver(self, alias):
        """
        Unregister a Scaleform part of the Observer with a Python part
        
        :param alias: name of the Observer.
        """
        if alias not in self.__observers:
            LOG_WARNING('Trying to unregister not registered observer:', alias)
            return
        observer = self.__observers.pop(alias)
        observer.destroy()

    def getObserver(self, alias):
        """
        Returns Observer object with connected Python and Scaleform parts
        
        :param alias: name of the Observer.
        :return: Python Observer Instance
        """
        return self.__observers.get(alias)

    def _populate(self):
        super(BootcampManager, self)._populate()
        self.as_setSystemEnabledS(self.__isEnabled)
        observersConfig = map(lambda x: x.getVO(), self.__config['observers'])
        self.as_configObserversS(observersConfig)

    def _dispose(self):
        super(BootcampManager, self)._dispose()
        self.__isEnabled = False
        self.__classes.clear()
        while self.__observers:
            _, observer = self.__observers.popitem()
            observer.destroy()
