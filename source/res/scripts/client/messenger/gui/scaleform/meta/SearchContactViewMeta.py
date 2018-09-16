# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/SearchContactViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from messenger.gui.Scaleform.view.lobby.BaseContactView import BaseContactView

class SearchContactViewMeta(BaseContactView):

    def search(self, data):
        self._printOverrideError('search')

    def as_getSearchDPS(self):
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_setSearchResultTextS(self, message):
        return self.flashObject.as_setSearchResultText(message) if self._isDAAPIInited() else None

    def as_setSearchDisabledS(self, coolDown):
        return self.flashObject.as_setSearchDisabled(coolDown) if self._isDAAPIInited() else None
