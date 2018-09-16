# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/PixieBG.py
import Pixie
from vehicle_systems import stricted_loading
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

class PixieBG(object):
    __slots__ = ('__loader', '__callback', '__data', 'name', 'pixie')

    @staticmethod
    def enablePixie(pixie, turnOn):
        multiplier = 1.0 if turnOn else 0.0
        for i in xrange(pixie.nSystems()):
            try:
                source = pixie.system(i).action(16)
                source.MultRate(multiplier)
            except Exception:
                LOG_CURRENT_EXCEPTION()

    def __init__(self, name, onLoadCallback, pixie=None, data=None, modifiers=None):
        self.name = name
        self.pixie = pixie
        self.__data = data
        if pixie is None:
            self.__loader = stricted_loading.restrictBySpace(self.__onLoad)
            self.__callback = onLoadCallback
            Pixie.createBG(name, self.__loader, modifiers)
        else:
            self.__loader = None
            self.__callback = None
            if modifiers is not None:
                self.pixie.applyModifiers(modifiers)
        return

    def __del__(self):
        self.__loader = None
        self.__callback = None
        self.__data = None
        if self.pixie is not None:
            self.pixie.clear()
            self.pixie = None
        self.name = None
        return

    def destroy(self):
        self.__loader = None
        self.__callback = None
        self.__data = None
        if self.pixie is not None:
            self.pixie.clear()
            self.pixie = None
        self.name = None
        return

    def __onLoad(self, newPixie):
        if newPixie is None:
            LOG_ERROR("Can't create pixie '%s'." % self.name)
            return
        else:
            self.pixie = newPixie
            if self.__data is not None:
                self.__callback(self, self.__data)
            else:
                self.__callback(self)
            self.__loader = None
            self.__callback = None
            self.__data = None
            return

    def stopLoading(self):
        self.__loader = None
        self.__callback = None
        return

    def stopEmission(self):
        if self.pixie is not None:
            for i in xrange(self.pixie.nSystems()):
                source = self.pixie.system(i).action(1)
                source.rate = 0

        return

    def clear(self):
        if self.pixie is not None:
            self.pixie.clear()
        return

    def scale(self, scale):
        if self.pixie is not None:
            self.pixie.scale = scale
        return

    def force(self, force):
        if self.pixie is not None and force > 0:
            self.pixie.force(force)
        return
