# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareConfiguratorMainMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.meta.VehicleCompareCommonViewMeta import VehicleCompareCommonViewMeta

class VehicleCompareConfiguratorMainMeta(VehicleCompareCommonViewMeta):

    def as_showViewS(self, alias):
        return self.flashObject.as_showView(alias) if self._isDAAPIInited() else None
