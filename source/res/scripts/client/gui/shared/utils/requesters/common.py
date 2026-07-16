# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/common.py
from __future__ import absolute_import
import typing
import BigWorld
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Iterable, Any

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

    def __init__(self, prevFactory=None):
        self._currValues = {}
        self._prevValues = {}
        self._prevFactory = prevFactory
        self._prevIsInitialized = False

    def update(self, data):
        self._currValues.clear()
        self._currValues.update(self._getDataIterator(data))
        self._initializePrevValues()
        self._removeOutdatedValues()

    def updatePrevValueToCurrentValue(self, entryId):
        if entryId in self._currValues:
            self._prevValues[entryId] = self._currValues[entryId]

    def getPrevValue(self, entryId):
        return self._prevValues[entryId] if entryId in self._prevValues else self._getDefaultValue()

    def clear(self):
        self._prevValues.clear()
        self._currValues.clear()
        self._prevIsInitialized = False

    def hasDiff(self, entryId):
        return self._hasEntryChanged(entryId) if entryId in self._currValues else False

    def _hasEntryChanged(self, entryId):
        prevValues = self.getPrevValue(entryId)
        return self._currValues.get(entryId) != prevValues

    def _removeOutdatedValues(self):
        for entryId in list(self._prevValues):
            if entryId not in self._currValues:
                del self._prevValues[entryId]

    def _getDataIterator(self, data):
        raise NotImplementedError

    def _getDefaultValue(self):
        raise NotImplementedError

    def _initializePrevValues(self):
        if self._prevIsInitialized:
            return
        if self._prevFactory:
            self._prevValues = self._prevFactory()
        else:
            self._prevValues = dict(self._currValues)
        self._prevIsInitialized = True
