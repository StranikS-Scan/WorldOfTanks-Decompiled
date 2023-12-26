# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class NYMainViewMeta(View):

    def onEscPress(self):
        self._printOverrideError('onEscPress')

    def onSwitchView(self):
        self._printOverrideError('onSwitchView')

    def as_switchViewS(self, toInject):
        return self.flashObject.as_switchView(toInject) if self._isDAAPIInited() else None
