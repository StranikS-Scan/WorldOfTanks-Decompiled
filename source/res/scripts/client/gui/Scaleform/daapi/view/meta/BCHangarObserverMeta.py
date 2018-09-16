# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCHangarObserverMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BCHangarObserverMeta(BaseDAAPIComponent):

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
