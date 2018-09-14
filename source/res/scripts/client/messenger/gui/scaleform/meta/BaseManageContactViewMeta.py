# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/BaseManageContactViewMeta.py
from messenger.gui.Scaleform.view.lobby.BaseContactView import BaseContactView

class BaseManageContactViewMeta(BaseContactView):

    def checkText(self, txt):
        self._printOverrideError('checkText')

    def as_setLabelS(self, msg):
        return self.flashObject.as_setLabel(msg) if self._isDAAPIInited() else None

    def as_setInputTextS(self, msg):
        return self.flashObject.as_setInputText(msg) if self._isDAAPIInited() else None
