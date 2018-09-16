# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FE18SpecialRewardScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class FE18SpecialRewardScreenMeta(View):

    def as_showS(self, val):
        return self.flashObject.as_show(val) if self._isDAAPIInited() else None
