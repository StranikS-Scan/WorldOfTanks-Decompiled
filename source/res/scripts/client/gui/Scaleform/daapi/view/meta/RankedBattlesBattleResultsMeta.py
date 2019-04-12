# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesBattleResultsMeta.py
from gui.Scaleform.framework.entities.View import View

class RankedBattlesBattleResultsMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onWidgetUpdate(self):
        self._printOverrideError('onWidgetUpdate')

    def animationCheckBoxSelected(self, value):
        self._printOverrideError('animationCheckBoxSelected')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
