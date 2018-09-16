# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCLobbyObserverMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BCLobbyObserverMeta(BaseDAAPIComponent):

    def onAnimationsComplete(self):
        self._printOverrideError('onAnimationsComplete')

    def registerAppearManager(self, component):
        self._printOverrideError('registerAppearManager')

    def as_setBootcampDataS(self, data):
        """
        :param data: Represented by BCLobbySettingsVO (AS)
        """
        return self.flashObject.as_setBootcampData(data) if self._isDAAPIInited() else None

    def as_showAnimatedS(self, data):
        """
        :param data: Represented by Vector.<String> (AS)
        """
        return self.flashObject.as_showAnimated(data) if self._isDAAPIInited() else None

    def as_setAppearConfigS(self, data):
        return self.flashObject.as_setAppearConfig(data) if self._isDAAPIInited() else None
