# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsFilterPopoverViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class MissionsFilterPopoverViewMeta(SmartPopOverView):

    def changeFilter(self, hideUnavailable, hideDone):
        self._printOverrideError('changeFilter')

    def setDefaultFilter(self):
        self._printOverrideError('setDefaultFilter')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by MissionsFilterPopoverInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setStateS(self, data):
        """
        :param data: Represented by MissionsFilterPopoverStateVO (AS)
        """
        return self.flashObject.as_setState(data) if self._isDAAPIInited() else None

    def as_enableDefaultBtnS(self, value):
        return self.flashObject.as_enableDefaultBtn(value) if self._isDAAPIInited() else None
