# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WrapperViewMeta.py
from gui.Scaleform.framework.entities.View import View

class WrapperViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def onWindowClose(self):
        self._printOverrideError('onWindowClose')

    def as_showWaitingS(self, msg, props):
        return self.flashObject.as_showWaiting(msg, props) if self._isDAAPIInited() else None

    def as_hideWaitingS(self):
        return self.flashObject.as_hideWaiting() if self._isDAAPIInited() else None
