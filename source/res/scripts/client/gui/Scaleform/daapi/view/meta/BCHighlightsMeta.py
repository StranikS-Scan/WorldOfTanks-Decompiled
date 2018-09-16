# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCHighlightsMeta.py
from gui.Scaleform.framework.entities.View import View

class BCHighlightsMeta(View):

    def onComponentTriggered(self, highlightId):
        self._printOverrideError('onComponentTriggered')

    def onHighlightAnimationComplete(self, highlightId):
        self._printOverrideError('onHighlightAnimationComplete')

    def as_setDescriptorsS(self, data):
        return self.flashObject.as_setDescriptors(data) if self._isDAAPIInited() else None

    def as_addHighlightS(self, highlightId):
        return self.flashObject.as_addHighlight(highlightId) if self._isDAAPIInited() else None

    def as_removeHighlightS(self, highlightId):
        return self.flashObject.as_removeHighlight(highlightId) if self._isDAAPIInited() else None
