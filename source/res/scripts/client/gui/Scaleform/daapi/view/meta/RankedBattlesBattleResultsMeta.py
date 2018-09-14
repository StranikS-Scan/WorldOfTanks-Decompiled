# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesBattleResultsMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedBattlesBattleResultsMeta(WrapperViewMeta):

    def closeView(self):
        self._printOverrideError('closeView')

    def ready(self):
        self._printOverrideError('ready')

    def as_setDataS(self, data):
        """
        :param data: Represented by RankedBattleResultsVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
