# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/true_dict/observer.py
from __future__ import absolute_import
from typing import Any, List, Tuple

class _TrueDictObserverBase(object):

    def onTrueDictAdded(self, propertyName, keyName):
        pass

    def onTrueDictUpdated(self, propertyName, keyName, oldValue):
        pass

    def onTrueDictRemoved(self, propertyName, keyName, oldValue):
        pass

    def _observeNested(self, propertyName, changePath, oldValue):
        prop, index = changePath[0], changePath[1]
        keys, values = self._window(propertyName, index, index + 1)
        if not keys:
            return
        if prop == 'values':
            self.onTrueDictUpdated(propertyName, keys[0], oldValue)
        elif prop == 'keys':
            oldKey, newKey = oldValue, keys[0]
            if oldKey != newKey:
                self.onTrueDictRemoved(propertyName, oldKey, values[0])
                self.onTrueDictAdded(propertyName, newKey)

    def _observeSlice(self, propertyName, changePath, oldValue):
        prop = changePath[0]
        if prop == 'values' and len(changePath) > 2 and isinstance(changePath[-1], (tuple, list)):
            index = changePath[1]
            keys, _ = self._window(propertyName, index, index + 1)
            if keys:
                self.onTrueDictUpdated(propertyName, keys[0], oldValue)
            return
        start, end = self._sliceBounds(changePath)
        oldSlice = list(oldValue)
        newKeys, newValues = self._window(propertyName, start, end)
        if prop == 'values' and start < end and oldSlice:
            for offset, newVal in enumerate(newValues):
                if offset < len(oldSlice) and oldSlice[offset] != newVal:
                    self.onTrueDictUpdated(propertyName, newKeys[offset], oldSlice[offset])

            return
        slot = self._pending().setdefault(propertyName, {})
        if prop == 'keys':
            slot['addedItems'] = [ key for key in newKeys if key not in oldSlice ]
            slot['removedItems'] = [ key for key in oldSlice if key not in newKeys ]
        else:
            slot['prevValues'] = oldSlice
        if 'addedItems' in slot and 'prevValues' in slot:
            del self._pending()[propertyName]
            for key in slot['addedItems']:
                self.onTrueDictAdded(propertyName, key)

            for key, oldVal in zip(slot['removedItems'], slot['prevValues']):
                self.onTrueDictRemoved(propertyName, key, oldVal)

    def _window(self, propertyName, start, end):
        trueDict = getattr(self, propertyName, None)
        return ([], []) if trueDict is None else trueDict.positionalSlice(start, end)

    def _pending(self):
        return self.__dict__.setdefault('_truedict_pending', {})

    @staticmethod
    def _sliceBounds(changePath):
        spec = changePath[1]
        return (spec[0], spec[1]) if isinstance(spec, (tuple, list)) else (changePath[-2], changePath[-1])


def TrueDictObserverMixin(propertyName):

    def _setNested(self, changePath, oldValue):
        self._observeNested(propertyName, changePath, oldValue)

    def _setSlice(self, changePath, oldValue):
        self._observeSlice(propertyName, changePath, oldValue)

    attrs = {'setNested_%s' % propertyName: _setNested,
     'setSlice_%s' % propertyName: _setSlice}
    return type('TrueDictObserverMixin_%s' % propertyName, (_TrueDictObserverBase,), attrs)
