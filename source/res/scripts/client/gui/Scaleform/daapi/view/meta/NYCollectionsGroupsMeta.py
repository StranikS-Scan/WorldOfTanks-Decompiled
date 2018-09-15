# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYCollectionsGroupsMeta.py
from gui.Scaleform.framework.entities.View import View

class NYCollectionsGroupsMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onAlbumClick(self, settingsId):
        self._printOverrideError('onAlbumClick')

    def as_setDataS(self, data):
        """
        :param data: Represented by NYCollectionsGroupsVo (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
