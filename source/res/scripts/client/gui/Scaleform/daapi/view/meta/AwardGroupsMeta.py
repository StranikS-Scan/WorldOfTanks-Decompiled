# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AwardGroupsMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AwardGroupsMeta(BaseDAAPIComponent):

    def showGroup(self, groupId):
        self._printOverrideError('showGroup')

    def as_setDataS(self, groups):
        """
        :param groups: Represented by Array (AS)
        """
        return self.flashObject.as_setData(groups) if self._isDAAPIInited() else None

    def as_setTooltipsS(self, tooltips):
        """
        :param tooltips: Represented by Array (AS)
        """
        return self.flashObject.as_setTooltips(tooltips) if self._isDAAPIInited() else None

    def as_setSelectedS(self, id, value):
        return self.flashObject.as_setSelected(id, value) if self._isDAAPIInited() else None

    def as_setEnabledS(self, id, value):
        return self.flashObject.as_setEnabled(id, value) if self._isDAAPIInited() else None
