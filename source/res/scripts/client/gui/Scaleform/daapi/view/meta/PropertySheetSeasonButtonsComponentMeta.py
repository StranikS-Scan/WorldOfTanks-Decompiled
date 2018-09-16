# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PropertySheetSeasonButtonsComponentMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PropertySheetSeasonButtonsComponentMeta(BaseDAAPIComponent):

    def refreshSeasonButtons(self):
        self._printOverrideError('refreshSeasonButtons')

    def show(self):
        self._printOverrideError('show')

    def refresh(self):
        self._printOverrideError('refresh')

    def hide(self):
        self._printOverrideError('hide')

    def as_setRendererDataS(self, data):
        """
        :param data: Represented by PropertySheetSeasonButtonsComponentVO (AS)
        """
        return self.flashObject.as_setRendererData(data) if self._isDAAPIInited() else None
