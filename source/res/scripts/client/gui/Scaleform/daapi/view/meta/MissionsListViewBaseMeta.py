# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsListViewBaseMeta.py
from gui.Scaleform.daapi.view.meta.MissionsViewBaseMeta import MissionsViewBaseMeta

class MissionsListViewBaseMeta(MissionsViewBaseMeta):

    def openMissionDetailsView(self, id, blockId):
        self._printOverrideError('openMissionDetailsView')

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_scrollToItemS(self, idFieldName, itemId):
        return self.flashObject.as_scrollToItem(idFieldName, itemId) if self._isDAAPIInited() else None
