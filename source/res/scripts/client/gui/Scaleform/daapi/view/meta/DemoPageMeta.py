# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DemoPageMeta.py
from gui.Scaleform.framework.entities.View import View

class DemoPageMeta(View):

    def onButtonClicked(self, buttonID):
        self._printOverrideError('onButtonClicked')

    def as_setContentS(self, buttons):
        return self.flashObject.as_setContent(buttons) if self._isDAAPIInited() else None
