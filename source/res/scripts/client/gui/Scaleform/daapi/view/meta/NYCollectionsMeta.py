# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYCollectionsMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class NYCollectionsMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onChange(self, settings, level):
        self._printOverrideError('onChange')

    def as_setDataS(self, data):
        """
        :param data: Represented by NYCollectionsVo (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setLevelDataS(self, data):
        """
        :param data: Represented by NYLevelCollectionVo (AS)
        """
        return self.flashObject.as_setLevelData(data) if self._isDAAPIInited() else None
