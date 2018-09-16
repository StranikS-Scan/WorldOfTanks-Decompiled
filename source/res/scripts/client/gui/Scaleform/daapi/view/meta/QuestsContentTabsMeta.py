# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsContentTabsMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class QuestsContentTabsMeta(BaseDAAPIComponent):

    def onSelectTab(self, id):
        self._printOverrideError('onSelectTab')

    def as_selectTabS(self, index):
        return self.flashObject.as_selectTab(index) if self._isDAAPIInited() else None

    def as_setTabsS(self, data):
        """
        :param data: Represented by TabsVO (AS)
        """
        return self.flashObject.as_setTabs(data) if self._isDAAPIInited() else None
