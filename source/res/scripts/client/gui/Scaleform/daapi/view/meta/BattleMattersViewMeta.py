# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleMattersViewMeta.py
from gui.Scaleform.daapi.view.meta.MissionsViewBaseMeta import MissionsViewBaseMeta

class BattleMattersViewMeta(MissionsViewBaseMeta):

    def as_showViewS(self):
        return self.flashObject.as_showView() if self._isDAAPIInited() else None

    def as_hideViewS(self):
        return self.flashObject.as_hideView() if self._isDAAPIInited() else None

    def as_setPlaceIdS(self, placeId):
        return self.flashObject.as_setPlaceId(placeId) if self._isDAAPIInited() else None
