# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsMapboxViewMeta.py
from gui.Scaleform.daapi.view.meta.MissionsViewBaseMeta import MissionsViewBaseMeta

class MissionsMapboxViewMeta(MissionsViewBaseMeta):

    def as_showViewS(self):
        return self.flashObject.as_showView() if self._isDAAPIInited() else None
