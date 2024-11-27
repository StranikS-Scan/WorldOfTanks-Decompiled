# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrebattleCarouselViewMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class PrebattleCarouselViewMeta(InjectComponentAdaptor):

    def setFilter(self, id):
        self._printOverrideError('setFilter')

    def onViewIsHidden(self):
        self._printOverrideError('onViewIsHidden')

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self, useAnim):
        return self.flashObject.as_hide(useAnim) if self._isDAAPIInited() else None
