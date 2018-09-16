# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseRallyViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.AbstractRallyView import AbstractRallyView

class BaseRallyViewMeta(AbstractRallyView):

    def as_setCoolDownS(self, value, requestId):
        return self.flashObject.as_setCoolDown(value, requestId) if self._isDAAPIInited() else None
