# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AwardWindowsBaseMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class AwardWindowsBaseMeta(AbstractWindowView):

    def as_setDataS(self, data):
        """
        :param data: Represented by AwardWindowVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
