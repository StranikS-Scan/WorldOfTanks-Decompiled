# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/BootcampManagerMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BootcampManagerMeta(BaseDAAPIComponent):

    def registerObserver(self, observer, alias):
        self._printOverrideError('registerObserver')

    def unregisterObserver(self, alias):
        self._printOverrideError('unregisterObserver')

    def as_setSystemEnabledS(self, value):
        return self.flashObject.as_setSystemEnabled(value) if self._isDAAPIInited() else None

    def as_configObserversS(self, items):
        """
        :param items: Represented by Vector.<BootcampObserverConfigVO> (AS)
        """
        return self.flashObject.as_configObservers(items) if self._isDAAPIInited() else None
