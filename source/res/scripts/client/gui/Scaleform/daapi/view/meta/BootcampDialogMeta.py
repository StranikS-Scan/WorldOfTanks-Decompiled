# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BootcampDialogMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog

class BootcampDialogMeta(SimpleDialog):

    def as_setDataS(self, path, label, showAward, awardText):
        return self.flashObject.as_setData(path, label, showAward, awardText) if self._isDAAPIInited() else None
