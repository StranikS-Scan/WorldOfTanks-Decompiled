# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/common.py
from typing import Iterable, Any
import BigWorld
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class RequestProcessor(object):

    def __init__(self, delay, callback):
        self.__callback = callback
        self.__fired = False
        self.__bwCallbackID = BigWorld.callback(delay, self.__cooldownCallback)

    @property
    def isFired(self):
        return self.__fired

    def cancel(self):
        if self.__bwCallbackID is not None:
            BigWorld.cancelCallback(self.__bwCallbackID)
            self.__bwCallbackID = None
        return

    def __cooldownCallback(self):
        self.__bwCallbackID = None
        self.__fired = True
        self.__callback()
        return


class BaseDelta(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self._prevValues = {}
        self._currValues = {}
        self.__isInitialized = False

    def update(self, data):
        self._currValues.clear()
        self._currValues.update(self._getDataIterator(data))
        self.__initialize()
        self._removeOutdatedValues()

    def updatePrevValueToCurrentValue(self, entryId):
        if entryId in self._currValues:
            self._prevValues[entryId] = self._currValues[entryId]

    def getPrevValue(self, entryId):
        return self._prevValues[entryId] if entryId in self._prevValues else self._getDefaultValue()

    def clear(self):
        self._currValues.clear()
        self._prevValues.clear()
        self.__isInitialized = False

    def hasDiff(self, entryId):
        if entryId in self._currValues:
            if entryId in self._prevValues:
                return self._hasEntryChanged(entryId)
            return True
        return False

    def _hasEntryChanged(self, entryId):
        raise NotImplementedError

    def _removeOutdatedValues(self):
        for entryId in self._prevValues.keys():
            if entryId not in self._currValues:
                del self._prevValues[entryId]

    def _getDataIterator(self, data):
        raise NotImplementedError

    def _getDefaultValue(self):
        raise NotImplementedError

    def __initialize(self):
        if not self.__isInitialized:
            for entryId in self._currValues.iterkeys():
                self._prevValues[entryId] = self._currValues[entryId]

            self.__isInitialized = True
