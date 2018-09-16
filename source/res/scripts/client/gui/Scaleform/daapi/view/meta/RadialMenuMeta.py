# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RadialMenuMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RadialMenuMeta(BaseDAAPIComponent):

    def onSelect(self):
        self._printOverrideError('onSelect')

    def onAction(self, action):
        self._printOverrideError('onAction')

    def as_buildDataS(self, data):
        """
        :param data: Represented by Array (AS)
        """
        return self.flashObject.as_buildData(data) if self._isDAAPIInited() else None

    def as_showS(self, radialState, offset, ratio):
        """
        :param offset: Represented by Array (AS)
        :param ratio: Represented by Array (AS)
        """
        return self.flashObject.as_show(radialState, offset, ratio) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
